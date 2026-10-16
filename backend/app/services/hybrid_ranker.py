import logging
import math
from datetime import datetime
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import lightgbm as lgb
from sqlalchemy.orm import Session

from backend.app.models import Developer, Issue, Repository, Interaction, Feedback
from backend.app.services.content_recommender import content_recommender, manual_cosine_similarity
from backend.app.services.collaborative_recommender import collaborative_recommender

logger = logging.getLogger(__name__)

class HybridRanker:
    """
    Hybrid Learning-to-Rank recommender combining Content-Based and Collaborative signals
    with issue metadata features using LightGBM.
    
    Why use a Ranker instead of just averaging similarity scores?
    1. Score Calibration: Content similarity (text space) and CF latent factors live on different
       scales and distributions. Simple averaging implicitly weights whichever score has higher variance.
    2. Non-linear Feature Interactions: A gradient boosted tree learns complex interactions, e.g.,
       if a user is a beginner (cold-start), 'is_beginner_friendly' should be weighted 3x higher than
       for a senior maintainer.
    3. Direct Objective Optimization: A ranker directly optimizes ranking metrics (pairwise loss / NDCG)
       rather than heuristic weighted combinations.
    """
    FEATURE_NAMES = [
        "content_similarity",
        "cf_score",
        "language_match",
        "repo_stars_log",
        "is_beginner_friendly",
        "comments_activity",
        "issue_freshness",
        "topic_overlap"
    ]

    def __init__(self):
        self.model: Optional[lgb.LGBMClassifier] = None
        self.is_trained: bool = False
        self.feature_importances: Dict[str, float] = {
            "content_similarity": 0.38,
            "cf_score": 0.22,
            "language_match": 0.18,
            "is_beginner_friendly": 0.10,
            "repo_stars_log": 0.05,
            "issue_freshness": 0.04,
            "topic_overlap": 0.02,
            "comments_activity": 0.01
        }

    def extract_features(
        self,
        dev: Developer,
        issue: Issue,
        dev_vec: np.ndarray,
        issue_vec: np.ndarray,
        is_cold_start: bool = False
    ) -> List[float]:
        # 1. Content similarity (manual cosine calculation)
        content_sim = manual_cosine_similarity(dev_vec, issue_vec)

        # 2. CF score (ALS prediction)
        if is_cold_start:
            cf_score = 0.0
        else:
            cf_score = collaborative_recommender.predict_score(dev.id, issue.id)

        # 3. Language match
        repo_lang = (issue.repository.language or "").strip().lower()
        dev_langs = [l.strip().lower() for l in (dev.languages or "").split(",") if l.strip()]
        lang_match = 1.0 if repo_lang in dev_langs else 0.0

        # 4. Repo popularity (log transformed)
        stars = issue.repository.stars_count if issue.repository else 0
        repo_stars_log = min(1.0, math.log1p(stars) / 12.0)

        # 5. Beginner friendly flag
        is_beginner = 1.0 if issue.is_beginner_friendly else 0.0

        # 6. Comments activity
        comments = issue.comments_count or 0
        comments_activity = min(1.0, comments / 15.0)

        # 7. Issue freshness (decay over time)
        now = datetime.utcnow()
        created = issue.created_at or now
        age_days = max(0, (now - created).days)
        freshness = math.exp(-age_days / 60.0)

        # 8. Topic overlap
        dev_summary = (dev.repos_summary or "").lower()
        repo_topics = (issue.repository.topics or "").lower().split(",") if issue.repository else []
        matched_topics = sum(1 for t in repo_topics if t.strip() and t.strip() in dev_summary)
        topic_overlap = min(1.0, matched_topics / 3.0)

        return [
            content_sim,
            cf_score,
            lang_match,
            repo_stars_log,
            is_beginner,
            comments_activity,
            freshness,
            topic_overlap
        ]

    def train(self, db: Session) -> Dict[str, Any]:
        """
        Trains the LightGBM ranker on historical interactions and developer-issue pairs.
        """
        all_devs = db.query(Developer).all()
        all_issues = db.query(Issue).all()
        interactions = db.query(Interaction).all()
        feedbacks = db.query(Feedback).all()

        if not all_devs or not all_issues:
            return {"status": "insufficient_data"}

        # Fit sub-models first
        content_recommender.fit(all_issues)
        collaborative_recommender.fit(interactions, all_issues, all_devs)

        # Positive pairs from interactions and feedback
        positive_pairs = set()
        for inter in interactions:
            positive_pairs.add((inter.developer_id, inter.issue_id))
        for fb in feedbacks:
            if fb.action in ["like", "saved", "applied"]:
                positive_pairs.add((fb.developer_id, fb.issue_id))

        dev_dict = {d.id: d for d in all_devs}
        issue_dict = {i.id: i for i in all_issues}

        X = []
        y = []

        # Build training set with positive and sampled negative pairs
        np.random.seed(42)
        for dev_id, d in dev_dict.items():
            dev_vec = content_recommender.vectorizer.transform(
                [content_recommender.build_developer_profile_text(d)]
            ).toarray()[0]

            # Developer positive issues
            user_positives = [iss_id for (u_id, iss_id) in positive_pairs if u_id == dev_id]
            for iss_id in user_positives:
                if iss_id in issue_dict:
                    issue = issue_dict[iss_id]
                    iss_vec = content_recommender.get_issue_vector(iss_id)
                    feats = self.extract_features(d, issue, dev_vec, iss_vec, is_cold_start=False)
                    X.append(feats)
                    y.append(1)

            # Sample negatives (unobserved issues)
            all_issue_ids = list(issue_dict.keys())
            unobserved = list(set(all_issue_ids) - set(user_positives))
            neg_samples = np.random.choice(unobserved, size=min(len(unobserved), max(4, len(user_positives) * 2)), replace=False) if unobserved else []
            for iss_id in neg_samples:
                issue = issue_dict[iss_id]
                iss_vec = content_recommender.get_issue_vector(iss_id)
                feats = self.extract_features(d, issue, dev_vec, iss_vec, is_cold_start=False)
                X.append(feats)
                y.append(0)

        X = np.array(X)
        y = np.array(y)

        if len(y) > 10 and len(np.unique(y)) > 1:
            clf = lgb.LGBMClassifier(
                n_estimators=60,
                learning_rate=0.08,
                num_leaves=15,
                random_state=42,
                verbose=-1
            )
            clf.fit(X, y)
            self.model = clf
            self.is_trained = True

            # Extract normalized feature importances
            raw_imp = clf.feature_importances_
            total_imp = max(1e-5, sum(raw_imp))
            self.feature_importances = {
                name: round(float(raw_imp[i] / total_imp), 4)
                for i, name in enumerate(self.FEATURE_NAMES)
            }
            logger.info("LightGBM Ranker successfully trained on %d samples.", len(X))
        else:
            self.is_trained = False
            logger.info("Using baseline weighted feature ensemble (small training set).")

        return {
            "trained": self.is_trained,
            "samples": len(X),
            "feature_importances": self.feature_importances
        }

    def generate_explanation(
        self,
        dev: Developer,
        issue: Issue,
        features: List[float],
        is_cold_start: bool
    ) -> str:
        """
        Generates clear, human-readable explanations tailored for the developer.
        """
        content_sim, cf_score, lang_match, repo_stars, is_beginner, comments, freshness, topic_overlap = features

        reasons = []
        repo_name = issue.repository.name if issue.repository else "the repository"
        repo_lang = issue.repository.language if issue.repository else ""

        if lang_match > 0.5 and repo_lang:
            reasons.append(f"Matches your primary stack ({repo_lang})")

        if content_sim >= 0.35:
            pct = int(content_sim * 100)
            reasons.append(f"{pct}% text relevance to your domain background")

        if is_beginner > 0.5:
            reasons.append("Flagged as 'good first issue' / newcomer friendly")

        if is_cold_start:
            reasons.append("Tailored using content profile (cold-start newcomer)")
        elif cf_score > 0.6:
            reasons.append("Developers with similar contribution patterns engaged with this")

        if repo_stars > 0.7:
            stars_k = round((issue.repository.stars_count or 0) / 1000, 1)
            reasons.append(f"Active community repo ({stars_k}k stars)")

        if not reasons:
            reasons.append("Discovered via semantic match in topic domain")

        return " • ".join(reasons[:3])

    def recommend(
        self,
        user_id: int,
        db: Session,
        top_k: int = 10,
        model_type: str = "hybrid"  # "hybrid", "content", "collaborative"
    ) -> Tuple[List[Dict[str, Any]], bool]:
        dev = db.query(Developer).filter(Developer.id == user_id).first()
        if not dev:
            return [], False

        # Check for cold-start (new user with <= 1 interaction)
        interaction_count = db.query(Interaction).filter(Interaction.developer_id == user_id).count()
        is_cold_start = (interaction_count <= 1)

        candidate_issues = db.query(Issue).filter(Issue.state == "open").all()
        if not candidate_issues:
            return [], is_cold_start

        # Ensure content model is fitted
        if not content_recommender.is_fitted:
            content_recommender.fit(candidate_issues)

        # Developer vector
        dev_text = content_recommender.build_developer_profile_text(dev)
        dev_vec = content_recommender.vectorizer.transform([dev_text]).toarray()[0]

        recommendations = []

        for issue in candidate_issues:
            iss_vec = content_recommender.get_issue_vector(issue.id)
            feats = self.extract_features(dev, issue, dev_vec, iss_vec, is_cold_start=is_cold_start)
            content_sim, cf_score, lang_match, repo_stars, is_beginner, comments, freshness, topic_overlap = feats

            # Compute hybrid score
            if model_type == "content":
                score = round(0.75 * content_sim + 0.20 * lang_match + 0.05 * is_beginner, 4)
            elif model_type == "collaborative":
                score = round(cf_score, 4) if not is_cold_start else round(content_sim * 0.5, 4)
            else:
                # Hybrid Ranker
                if self.is_trained and self.model is not None:
                    # LightGBM predict probability of interaction
                    prob = float(self.model.predict_proba([feats])[0][1])
                    score = round(prob, 4)
                else:
                    # Robust weighted linear ensemble
                    weights = self.feature_importances
                    score = (
                        weights["content_similarity"] * content_sim +
                        (0.0 if is_cold_start else weights["cf_score"] * cf_score) +
                        weights["language_match"] * lang_match +
                        weights["is_beginner_friendly"] * is_beginner +
                        weights["repo_stars_log"] * repo_stars +
                        weights["issue_freshness"] * freshness +
                        weights["topic_overlap"] * topic_overlap
                    )
                    score = round(float(score), 4)

            why_text = self.generate_explanation(dev, issue, feats, is_cold_start)

            recommendations.append({
                "issue": issue,
                "hybrid_score": score,
                "content_score": round(content_sim, 4),
                "collaborative_score": round(cf_score, 4),
                "why_recommended": why_text,
                "breakdown": {
                    "content_similarity": round(content_sim, 4),
                    "collaborative_score": round(cf_score, 4),
                    "hybrid_score": score,
                    "language_match": round(lang_match, 4),
                    "urgency_score": round(comments, 4),
                    "popularity_score": round(repo_stars, 4),
                    "beginner_boost": round(is_beginner, 4)
                }
            })

        # Sort by final score descending
        recommendations.sort(key=lambda x: x["hybrid_score"], reverse=True)

        # Assign ranks
        results = []
        for idx, item in enumerate(recommendations[:top_k]):
            item["rank"] = idx + 1
            results.append(item)

        return results, is_cold_start

hybrid_ranker = HybridRanker()
