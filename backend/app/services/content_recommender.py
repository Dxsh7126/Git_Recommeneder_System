import logging
from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sqlalchemy.orm import Session

from backend.app.models import Developer, Issue, Repository

logger = logging.getLogger(__name__)

def manual_cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """
    Computes cosine similarity between two 1D vectors strictly by hand with NumPy.
    Formula:
        cos(theta) = (a . b) / (||a|| * ||b||)
                   = sum(a_i * b_i) / (sqrt(sum(a_i^2)) * sqrt(sum(b_i^2)))
    Range: [-1.0, 1.0] (or [0.0, 1.0] for non-negative TF-IDF representations).
    A score of 1.0 indicates identical directional orientation in semantic space.
    """
    dot_product = float(np.dot(a, b))
    norm_a = float(np.linalg.norm(a))
    norm_b = float(np.linalg.norm(b))
    
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
        
    return max(0.0, min(1.0, dot_product / (norm_a * norm_b)))

class ContentBasedRecommender:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=5000,
            ngram_range=(1, 2)
        )
        self.issue_ids: List[int] = []
        self.issue_vectors: np.ndarray = np.array([])
        self.is_fitted: bool = False

    def build_issue_corpus(self, issues: List[Issue]) -> List[str]:
        corpus = []
        for issue in issues:
            repo_info = ""
            if issue.repository:
                repo = issue.repository
                repo_info = f"{repo.name} {repo.language} {repo.topics.replace(',', ' ')} {repo.description}"
            labels_clean = issue.labels.replace(",", " ") if issue.labels else ""
            doc = f"{issue.title} {issue.title} {issue.body} {labels_clean} {repo_info}"
            corpus.append(doc.lower())
        return corpus

    def build_developer_profile_text(self, dev: Developer) -> str:
        langs = dev.languages.replace(",", " ") if dev.languages else ""
        text = f"{dev.bio or ''} {langs} {langs} {dev.repos_summary or ''}"
        return text.lower()

    def fit(self, issues: List[Issue]) -> None:
        if not issues:
            return
        corpus = self.build_issue_corpus(issues)
        tfidf_matrix = self.vectorizer.fit_transform(corpus)
        # Convert sparse matrix to dense array for manual numpy computations
        self.issue_vectors = tfidf_matrix.toarray()
        self.issue_ids = [issue.id for issue in issues]
        self.is_fitted = True
        logger.info("Content-based model fitted on %d issues with vocabulary size %d", 
                    len(issues), len(self.vectorizer.vocabulary_))

    def get_issue_vector(self, issue_id: int) -> np.ndarray:
        if not self.is_fitted or issue_id not in self.issue_ids:
            return np.zeros(self.issue_vectors.shape[1] if self.is_fitted else 100)
        idx = self.issue_ids.index(issue_id)
        return self.issue_vectors[idx]

    def recommend(
        self, 
        user_id: int, 
        db: Session, 
        top_k: int = 10,
        candidate_issues: List[Issue] = None
    ) -> List[Dict[str, Any]]:
        dev = db.query(Developer).filter(Developer.id == user_id).first()
        if not dev:
            return []

        if candidate_issues is None or not self.is_fitted:
            candidate_issues = db.query(Issue).filter(Issue.state == "open").all()
            self.fit(candidate_issues)

        if not self.is_fitted or len(self.issue_ids) == 0:
            return []

        # Vectorize developer profile
        dev_text = self.build_developer_profile_text(dev)
        dev_vec_sparse = self.vectorizer.transform([dev_text])
        dev_vec = dev_vec_sparse.toarray()[0]

        scores = []
        issue_lookup = {issue.id: issue for issue in candidate_issues}

        for idx, issue_id in enumerate(self.issue_ids):
            if issue_id not in issue_lookup:
                continue
            issue = issue_lookup[issue_id]
            issue_vec = self.issue_vectors[idx]

            # Compute manual cosine similarity using our pure numpy function
            sim_score = manual_cosine_similarity(dev_vec, issue_vec)

            # Language boost if developer explicitly knows the repository language
            repo_lang = issue.repository.language if issue.repository else ""
            dev_langs = [l.strip().lower() for l in dev.languages.split(",") if l.strip()]
            lang_match = 1.0 if repo_lang.lower() in dev_langs else 0.0

            # Slightly reward beginner friendly issues if matched
            beginner_boost = 0.05 if issue.is_beginner_friendly else 0.0

            total_content_score = round(0.85 * sim_score + 0.15 * lang_match + beginner_boost, 4)

            scores.append({
                "issue_id": issue.id,
                "content_similarity": round(sim_score, 4),
                "language_match": lang_match,
                "score": total_content_score,
                "issue": issue
            })

        scores.sort(key=lambda x: x["score"], reverse=True)
        return scores[:top_k]

# Global singleton
content_recommender = ContentBasedRecommender()

def recommend_content_based(user_id: int, top_k: int = 10, db: Session = None) -> List[Dict[str, Any]]:
    return content_recommender.recommend(user_id=user_id, db=db, top_k=top_k)
