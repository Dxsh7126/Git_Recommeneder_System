import logging
from typing import List, Dict, Any, Tuple
import numpy as np
from sqlalchemy.orm import Session
from backend.app.models import Developer, Issue, Interaction
from backend.app.config import settings

logger = logging.getLogger(__name__)

class ImplicitALSRecommender:
    """
    Alternating Least Squares (ALS) Matrix Factorization for Implicit Feedback Datasets
    Based on Hu, Koren, and Volinsky (2008): 'Collaborative Filtering for Implicit Feedback Datasets'.
    
    Why ALS over simple SGD for implicit feedback?
    1. Implicit datasets have no true negative ratings—only varying confidence in positive signals
       (stars, comments, PRs) while unobserved entries could mean 'dislike' or simply 'unseen'.
    2. ALS allows efficient closed-form optimization across all unobserved pairs using precomputed
       Gram matrices (Y^T Y and X^T X), avoiding expensive negative sampling needed by SGD.
    """
    def __init__(
        self,
        factors: int = settings.ALS_FACTORS,
        regularization: float = settings.ALS_REGULARIZATION,
        iterations: int = settings.ALS_ITERATIONS,
        alpha: float = settings.ALS_ALPHA
    ):
        self.factors = factors
        self.regularization = regularization
        self.iterations = iterations
        self.alpha = alpha

        self.user_factors: np.ndarray = np.array([])
        self.item_factors: np.ndarray = np.array([])
        self.user_to_idx: Dict[int, int] = {}
        self.idx_to_user: Dict[int, int] = {}
        self.item_to_idx: Dict[int, int] = {}
        self.idx_to_item: Dict[int, int] = {}
        self.is_trained: bool = False

    def build_interaction_matrix(self, interactions: List[Interaction], all_issues: List[Issue], all_devs: List[Developer]):
        # Map user and item IDs to 0-indexed contiguous indices
        self.user_to_idx = {dev.id: idx for idx, dev in enumerate(all_devs)}
        self.idx_to_user = {idx: dev_id for dev_id, idx in self.user_to_idx.items()}

        self.item_to_idx = {issue.id: idx for idx, issue in enumerate(all_issues)}
        self.idx_to_item = {idx: item_id for item_id, idx in self.item_to_idx.items()}

        n_users = len(self.user_to_idx)
        n_items = len(self.item_to_idx)

        # Raw interaction count / weight matrix R
        R = np.zeros((n_users, n_items), dtype=np.float32)

        weight_map = {
            "view": 0.5,
            "like": 1.5,
            "star": 2.0,
            "comment": 3.0,
            "commit": 4.0,
            "pr_merge": 5.0
        }

        for inter in interactions:
            u_idx = self.user_to_idx.get(inter.developer_id)
            i_idx = self.item_to_idx.get(inter.issue_id)
            if u_idx is not None and i_idx is not None:
                w = inter.weight or weight_map.get(inter.interaction_type, 1.0)
                R[u_idx, i_idx] += w

        return R

    def fit(self, interactions: List[Interaction], all_issues: List[Issue], all_devs: List[Developer]) -> None:
        if not interactions or not all_issues or not all_devs:
            return

        R = self.build_interaction_matrix(interactions, all_issues, all_devs)
        n_users, n_items = R.shape

        if n_users == 0 or n_items == 0:
            return

        # Preference matrix P: 1 if R > 0 else 0
        P = (R > 0).astype(np.float32)

        # Confidence matrix C: 1 + alpha * R
        C = 1.0 + self.alpha * R

        # Initialize latent factor matrices randomly with small variance
        np.random.seed(42)
        self.user_factors = np.random.normal(0, 0.01, size=(n_users, self.factors)).astype(np.float32)
        self.item_factors = np.random.normal(0, 0.01, size=(n_items, self.factors)).astype(np.float32)

        lambda_eye = self.regularization * np.eye(self.factors, dtype=np.float32)

        # Alternating Least Squares iterations
        for iteration in range(self.iterations):
            # 1. Update User Factors: X = (Y^T C_u Y + lambda I)^-1 Y^T C_u p_u
            YTY = self.item_factors.T @ self.item_factors
            for u in range(n_users):
                Cu = C[u, :]
                pu = P[u, :]
                
                # Non-zero confidence entries speedup: C_u - I
                Cu_minus_I = Cu - 1.0
                non_zero = np.nonzero(Cu_minus_I)[0]
                
                if len(non_zero) > 0:
                    Y_nz = self.item_factors[non_zero, :]
                    Cu_nz = Cu_minus_I[non_zero, None]
                    A = YTY + (Y_nz.T * Cu_nz.T) @ Y_nz + lambda_eye
                    b = (self.item_factors.T * Cu) @ pu
                else:
                    A = YTY + lambda_eye
                    b = (self.item_factors.T * Cu) @ pu

                self.user_factors[u] = np.linalg.solve(A, b)

            # 2. Update Item Factors: Y = (X^T C_i X + lambda I)^-1 X^T C_i p_i
            XTX = self.user_factors.T @ self.user_factors
            for i in range(n_items):
                Ci = C[:, i]
                pi = P[:, i]

                Ci_minus_I = Ci - 1.0
                non_zero = np.nonzero(Ci_minus_I)[0]

                if len(non_zero) > 0:
                    X_nz = self.user_factors[non_zero, :]
                    Ci_nz = Ci_minus_I[non_zero, None]
                    A = XTX + (X_nz.T * Ci_nz.T) @ X_nz + lambda_eye
                    b = (self.user_factors.T * Ci) @ pi
                else:
                    A = XTX + lambda_eye
                    b = (self.user_factors.T * Ci) @ pi

                self.item_factors[i] = np.linalg.solve(A, b)

        self.is_trained = True
        logger.info("Implicit ALS factorization completed (%d users, %d items, %d factors).",
                    n_users, n_items, self.factors)

    def predict_score(self, user_id: int, issue_id: int) -> float:
        if not self.is_trained:
            return 0.0
        u_idx = self.user_to_idx.get(user_id)
        i_idx = self.item_to_idx.get(issue_id)
        if u_idx is None or i_idx is None:
            # Cold-start fallback
            return 0.0
        # Dot product of user and item latent representations
        score = float(np.dot(self.user_factors[u_idx], self.item_factors[i_idx]))
        # Sigmoid or min-max normalization to [0, 1] range for stability
        normalized_score = 1.0 / (1.0 + np.exp(-score))
        return float(normalized_score)

    def recommend(self, user_id: int, db: Session, top_k: int = 10) -> List[Dict[str, Any]]:
        if not self.is_trained:
            all_devs = db.query(Developer).all()
            all_issues = db.query(Issue).filter(Issue.state == "open").all()
            all_interactions = db.query(Interaction).all()
            self.fit(all_interactions, all_issues, all_devs)

        u_idx = self.user_to_idx.get(user_id)
        if u_idx is None or not self.is_trained:
            return []

        user_vec = self.user_factors[u_idx]
        raw_scores = self.item_factors @ user_vec
        # Normalized scores between 0 and 1
        scores = 1.0 / (1.0 + np.exp(-raw_scores))

        ranked_indices = np.argsort(scores)[::-1]
        results = []
        for idx in ranked_indices[:top_k]:
            issue_id = self.idx_to_item[idx]
            issue = db.query(Issue).filter(Issue.id == issue_id).first()
            if issue:
                results.append({
                    "issue_id": issue_id,
                    "collaborative_score": round(float(scores[idx]), 4),
                    "score": round(float(scores[idx]), 4),
                    "issue": issue
                })
        return results

# Global singleton
collaborative_recommender = ImplicitALSRecommender()

def recommend_collaborative(user_id: int, top_k: int = 10, db: Session = None) -> List[Dict[str, Any]]:
    return collaborative_recommender.recommend(user_id=user_id, db=db, top_k=top_k)
