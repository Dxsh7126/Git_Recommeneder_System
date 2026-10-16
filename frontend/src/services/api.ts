import { Developer, Issue, RecommendationResponse, EvaluationMetrics } from '../types';

const API_BASE = '/api';

export const api = {
  async getDevelopers(): Promise<Developer[]> {
    const res = await fetch(`${API_BASE}/developers`);
    if (!res.ok) throw new Error('Failed to fetch developers');
    return res.json();
  },

  async addGithubDeveloper(username: string): Promise<Developer> {
    const res = await fetch(`${API_BASE}/developers/github/${username}`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error('Failed to import GitHub user');
    return res.json();
  },

  async getRecommendations(
    userId: number,
    algorithm: string = 'hybrid',
    topK: number = 10,
    language?: string,
    beginnerOnly?: boolean
  ): Promise<RecommendationResponse> {
    const params = new URLSearchParams({
      model_type: algorithm,
      top_k: topK.toString(),
    });
    if (language) params.append('language', language);
    if (beginnerOnly) params.append('beginner_only', 'true');

    const res = await fetch(`${API_BASE}/recommendations/${userId}?${params.toString()}`);
    if (!res.ok) throw new Error('Failed to fetch recommendations');
    return res.json();
  },

  async sendFeedback(
    developerId: number,
    issueId: number,
    action: 'like' | 'dislike' | 'saved' | 'applied'
  ): Promise<any> {
    const res = await fetch(`${API_BASE}/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ developer_id: developerId, issue_id: issueId, action })
    });
    if (!res.ok) throw new Error('Failed to record feedback');
    return res.json();
  },

  async getMetrics(): Promise<EvaluationMetrics> {
    const res = await fetch(`${API_BASE}/metrics`);
    if (!res.ok) throw new Error('Failed to fetch evaluation metrics');
    return res.json();
  },

  async retrain(): Promise<any> {
    const res = await fetch(`${API_BASE}/retrain`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to retrain models');
    return res.json();
  },

  async reseed(): Promise<any> {
    const res = await fetch(`${API_BASE}/seed?force=true`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to reseed database');
    return res.json();
  }
};
