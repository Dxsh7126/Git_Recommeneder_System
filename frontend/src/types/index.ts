export interface Developer {
  id: number;
  username: string;
  name?: string;
  avatar_url?: string;
  bio?: string;
  languages?: string;
  repos_summary?: string;
  is_persona?: boolean;
}

export interface Repository {
  id: number;
  full_name: string;
  owner: string;
  name: string;
  description?: string;
  language?: string;
  topics?: string;
  stars_count: number;
  forks_count: number;
  open_issues_count: number;
  url: string;
}

export interface Issue {
  id: number;
  repo_id: number;
  number: number;
  title: string;
  body?: string;
  state: string;
  labels?: string;
  comments_count: number;
  is_beginner_friendly: boolean;
  html_url: string;
  created_at: string;
  repository?: Repository;
}

export interface ScoreBreakdown {
  content_similarity: number;
  collaborative_score: number;
  hybrid_score: number;
  language_match: number;
  urgency_score: number;
  popularity_score: number;
  beginner_boost: number;
}

export interface RecommendationItem {
  rank: number;
  issue: Issue;
  hybrid_score: number;
  content_score: number;
  collaborative_score: number;
  why_recommended: string;
  breakdown: ScoreBreakdown;
}

export interface RecommendationResponse {
  user_id: number;
  username: string;
  algorithm: 'hybrid' | 'content' | 'collaborative';
  is_cold_start: boolean;
  total_returned: number;
  recommendations: RecommendationItem[];
  computation_time_ms: number;
}

export interface ModelComparison {
  model: string;
  ndcg_at_10: number;
  recall_at_5: number;
  recall_at_10: number;
  mrr: number;
}

export interface EvaluationMetrics {
  split_method: string;
  holdout_ratio: number;
  total_eval_samples: number;
  ndcg_at_10: number;
  recall_at_5: number;
  recall_at_10: number;
  mrr: number;
  model_comparison: ModelComparison[];
  feature_importances: Record<string, number>;
}
