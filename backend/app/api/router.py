import time
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from backend.app.database import get_db
from backend.app.models import Developer, Issue, Repository, Feedback, Interaction
from backend.app.schemas import (
    DeveloperOut,
    IssueOut,
    RecommendationResponse,
    RecommendationItem,
    FeedbackCreate,
    FeedbackOut,
    EvaluationMetricsOut
)
from backend.app.services.hybrid_ranker import hybrid_ranker
from backend.app.services.content_recommender import content_recommender
from backend.app.services.collaborative_recommender import collaborative_recommender
from backend.app.services.evaluator import evaluator
from backend.app.services.cache import cache_service
from backend.app.services.data_collector import seed_database, fetch_github_user_profile

logger = logging.getLogger(__name__)

api_router = APIRouter()

@api_router.get("/developers", response_model=List[DeveloperOut])
def get_developers(db: Session = Depends(get_db)):
    """
    Returns list of registered developers and demo personas.
    """
    return db.query(Developer).all()

@api_router.get("/developers/{user_id}", response_model=DeveloperOut)
def get_developer(user_id: int, db: Session = Depends(get_db)):
    dev = db.query(Developer).filter(Developer.id == user_id).first()
    if not dev:
        raise HTTPException(status_code=404, detail="Developer not found")
    return dev

@api_router.post("/developers/github/{username}", response_model=DeveloperOut)
def add_or_get_github_developer(username: str, db: Session = Depends(get_db)):
    """
    Imports a live public GitHub user profile and repositories into the database.
    """
    existing = db.query(Developer).filter(Developer.username.ilike(username)).first()
    if existing:
        return existing

    profile = fetch_github_user_profile(username)
    if not profile:
        # Create minimal profile
        profile = {
            "username": username,
            "name": username,
            "avatar_url": f"https://github.com/{username}.png",
            "bio": "GitHub Developer",
            "languages": "Python,JavaScript",
            "repos_summary": "Open source developer exploring issues."
        }

    dev = Developer(
        username=profile["username"],
        name=profile.get("name"),
        avatar_url=profile.get("avatar_url"),
        bio=profile.get("bio"),
        languages=profile.get("languages", ""),
        repos_summary=profile.get("repos_summary", ""),
        is_persona=False
    )
    db.add(dev)
    db.commit()
    db.refresh(dev)
    return dev

@api_router.get("/recommendations/{user_id}", response_model=RecommendationResponse)
def get_recommendations(
    user_id: int,
    model_type: str = Query("hybrid", regex="^(hybrid|content|collaborative)$"),
    top_k: int = Query(10, ge=1, le=50),
    language: Optional[str] = None,
    beginner_only: Optional[bool] = False,
    db: Session = Depends(get_db)
):
    """
    Returns ranked open-source issue recommendations for a developer.
    Includes scores, explainability breakdown, and cold-start detection.
    Cached via Redis/memory for fast sub-50ms latency.
    """
    start_time = time.time()
    cache_key = f"recs:{user_id}:{model_type}:{top_k}:{language}:{beginner_only}"
    
    dev = db.query(Developer).filter(Developer.id == user_id).first()
    if not dev:
        raise HTTPException(status_code=404, detail="Developer profile not found")

    # Check cache
    cached_payload = cache_service.get(cache_key)
    if cached_payload:
        cached_payload["computation_time_ms"] = round((time.time() - start_time) * 1000, 2)
        return cached_payload

    # Run recommendation algorithm
    ranked_items, is_cold_start = hybrid_ranker.recommend(
        user_id=user_id,
        db=db,
        top_k=top_k * 2,  # Fetch extra to accommodate optional filters
        model_type=model_type
    )

    # Apply client-side filters if requested
    filtered_items = []
    for item in ranked_items:
        issue = item["issue"]
        if language and issue.repository and issue.repository.language.lower() != language.lower():
            continue
        if beginner_only and not issue.is_beginner_friendly:
            continue
        filtered_items.append(item)
        if len(filtered_items) >= top_k:
            break

    # Build response items
    formatted_recs = []
    for rank_idx, item in enumerate(filtered_items):
        issue_model = item["issue"]
        formatted_recs.append(
            RecommendationItem(
                rank=rank_idx + 1,
                issue=IssueOut.from_orm(issue_model),
                hybrid_score=item["hybrid_score"],
                content_score=item["content_score"],
                collaborative_score=item["collaborative_score"],
                why_recommended=item["why_recommended"],
                breakdown=item["breakdown"]
            )
        )

    duration_ms = round((time.time() - start_time) * 1000, 2)

    response = RecommendationResponse(
        user_id=user_id,
        username=dev.username,
        algorithm=model_type,
        is_cold_start=is_cold_start,
        total_returned=len(formatted_recs),
        recommendations=formatted_recs,
        computation_time_ms=duration_ms
    )

    # Cache result
    cache_service.set(cache_key, response.dict())

    return response

@api_router.post("/feedback", response_model=FeedbackOut)
def submit_feedback(fb_in: FeedbackCreate, db: Session = Depends(get_db)):
    """
    Submits developer feedback (like, dislike, saved, applied).
    Updates interaction history and invalidates user cache.
    """
    fb = Feedback(
        developer_id=fb_in.developer_id,
        issue_id=fb_in.issue_id,
        action=fb_in.action
    )
    db.add(fb)

    # Also log positive interaction to boost future CF/Hybrid personalization
    if fb_in.action in ["like", "saved", "applied"]:
        weight = 3.0 if fb_in.action == "applied" else (2.0 if fb_in.action == "saved" else 1.5)
        interaction = Interaction(
            developer_id=fb_in.developer_id,
            issue_id=fb_in.issue_id,
            interaction_type="like",
            weight=weight
        )
        db.add(interaction)

    db.commit()
    db.refresh(fb)

    # Invalidate cached recommendations for this user
    cache_service.invalidate(f"recs:{fb_in.developer_id}:")

    return fb

@api_router.get("/issues", response_model=List[IssueOut])
def get_issues(
    language: Optional[str] = None,
    beginner_only: bool = False,
    query: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """
    Browse open issues with search and filtering.
    """
    q = db.query(Issue).options(joinedload(Issue.repository)).filter(Issue.state == "open")

    if language:
        q = q.join(Repository).filter(Repository.language.ilike(language))
    if beginner_only:
        q = q.filter(Issue.is_beginner_friendly == True)
    if query:
        search_filter = f"%{query}%"
        q = q.filter(Issue.title.ilike(search_filter) | Issue.body.ilike(search_filter))

    return q.limit(limit).all()

@api_router.get("/metrics", response_model=EvaluationMetricsOut)
def get_evaluation_metrics(db: Session = Depends(get_db)):
    """
    Returns offline evaluation benchmark numbers (NDCG@10, Recall@5, Recall@10, MRR).
    """
    return evaluator.evaluate_model(db)

@api_router.post("/retrain")
def retrain_models(db: Session = Depends(get_db)):
    """
    Triggers on-demand retraining of LightGBM Ranker and ALS collaborative filtering models.
    """
    train_res = hybrid_ranker.train(db)
    # Clear all cached recommendations
    cache_service.invalidate("recs:")
    return {
        "status": "success",
        "message": "Models retrained and cache invalidated.",
        "details": train_res
    }

@api_router.post("/seed")
def reseed_database(force: bool = False, db: Session = Depends(get_db)):
    """
    Seeds repositories, issues, developers, and interactions.
    """
    res = seed_database(db, force=force)
    # Retrain on fresh data
    hybrid_ranker.train(db)
    cache_service.invalidate("recs:")
    return {"status": "success", "counts": res}
