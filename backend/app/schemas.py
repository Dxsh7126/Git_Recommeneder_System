from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class DeveloperBase(BaseModel):
    username: str
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    languages: Optional[str] = ""
    repos_summary: Optional[str] = ""
    is_persona: Optional[bool] = False

class DeveloperCreate(DeveloperBase):
    github_id: Optional[int] = None

class DeveloperOut(DeveloperBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class RepositoryOut(BaseModel):
    id: int
    full_name: str
    owner: str
    name: str
    description: Optional[str] = ""
    language: Optional[str] = ""
    topics: Optional[str] = ""
    stars_count: int = 0
    forks_count: int = 0
    open_issues_count: int = 0
    url: str

    class Config:
        from_attributes = True

class IssueOut(BaseModel):
    id: int
    repo_id: int
    number: int
    title: str
    body: Optional[str] = ""
    state: str
    labels: Optional[str] = ""
    comments_count: int = 0
    is_beginner_friendly: bool
    html_url: str
    created_at: datetime
    repository: Optional[RepositoryOut] = None

    class Config:
        from_attributes = True

class ScoreBreakdown(BaseModel):
    content_similarity: float
    collaborative_score: float
    hybrid_score: float
    language_match: float
    urgency_score: float
    popularity_score: float
    beginner_boost: float

class RecommendationItem(BaseModel):
    rank: int
    issue: IssueOut
    hybrid_score: float
    content_score: float
    collaborative_score: float
    why_recommended: str
    breakdown: ScoreBreakdown

class RecommendationResponse(BaseModel):
    user_id: int
    username: str
    algorithm: str  # "hybrid_ranker", "content_based", "collaborative"
    is_cold_start: bool
    total_returned: int
    recommendations: List[RecommendationItem]
    computation_time_ms: float

class FeedbackCreate(BaseModel):
    developer_id: int
    issue_id: int
    action: str  # 'like', 'dislike', 'saved', 'applied'

class FeedbackOut(BaseModel):
    id: int
    developer_id: int
    issue_id: int
    action: str
    created_at: datetime

    class Config:
        from_attributes = True

class ModelComparison(BaseModel):
    model: str
    ndcg_at_10: float
    recall_at_5: float
    recall_at_10: float
    mrr: float

class EvaluationMetricsOut(BaseModel):
    split_method: str
    holdout_ratio: float
    total_eval_samples: int
    ndcg_at_10: float
    recall_at_5: float
    recall_at_10: float
    mrr: float
    model_comparison: List[ModelComparison]
    feature_importances: Dict[str, float]
