import React, { useState } from 'react';
import { RecommendationItem } from '../types';
import { 
  Star, 
  MessageSquare, 
  ThumbsUp, 
  ThumbsDown, 
  Bookmark, 
  ExternalLink, 
  ChevronDown, 
  ChevronUp, 
  CheckCircle2, 
  Sparkles,
  GitBranch,
  Clock
} from 'lucide-react';

interface IssueCardProps {
  item: RecommendationItem;
  onFeedback: (issueId: number, action: 'like' | 'dislike' | 'saved' | 'applied') => Promise<void>;
}

const LANGUAGE_COLORS: Record<string, string> = {
  python: '#3572A5',
  typescript: '#3178C6',
  javascript: '#f1e05a',
  rust: '#dea584',
  go: '#00ADD8',
  'c++': '#f34b7d',
};

export const IssueCard: React.FC<IssueCardProps> = ({ item, onFeedback }) => {
  const [showBreakdown, setShowBreakdown] = useState(false);
  const [feedbackGiven, setFeedbackGiven] = useState<'like' | 'dislike' | 'saved' | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const issue = item.issue;
  const repo = issue.repository;
  const matchPct = Math.round(item.hybrid_score * 100);

  const handleFeedbackClick = async (action: 'like' | 'dislike' | 'saved') => {
    if (isSubmitting) return;
    setIsSubmitting(true);
    try {
      await onFeedback(issue.id, action);
      setFeedbackGiven(action);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getRankBadgeStyle = (rank: number) => {
    if (rank === 1) return 'bg-amber-500/20 text-amber-300 border-amber-500/50';
    if (rank === 2) return 'bg-slate-300/20 text-slate-200 border-slate-400/50';
    if (rank === 3) return 'bg-amber-700/20 text-amber-400 border-amber-700/50';
    return 'bg-[#21262d] text-[#8b949e] border-[#30363d]';
  };

  const langKey = (repo?.language || '').toLowerCase();
  const langColor = LANGUAGE_COLORS[langKey] || '#8b949e';

  return (
    <div className="bg-[#161b22] border border-[#30363d] hover:border-[#8b949e]/60 rounded-2xl p-5 transition-all shadow-sm hover:shadow-lg flex flex-col justify-between group">
      <div>
        {/* Top Header: Rank, Repo Info, Match Score */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex items-center space-x-2.5">
            <span className={`text-xs font-bold px-2 py-0.5 rounded-md border ${getRankBadgeStyle(item.rank)}`}>
              #{item.rank}
            </span>

            {repo && (
              <a
                href={repo.url}
                target="_blank"
                rel="noreferrer"
                className="text-xs font-medium text-[#8b949e] hover:text-[#58a6ff] transition-colors flex items-center gap-1.5"
              >
                <GitBranch className="w-3.5 h-3.5" />
                <span className="font-semibold text-white">{repo.full_name}</span>
                <span className="text-[#8b949e] flex items-center gap-0.5">
                  <Star className="w-3 h-3 text-amber-400 fill-amber-400/80 inline" />
                  {repo.stars_count >= 1000 ? `${(repo.stars_count / 1000).toFixed(1)}k` : repo.stars_count}
                </span>
              </a>
            )}
          </div>

          {/* Match Score Badge */}
          <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-bold shrink-0">
            <Sparkles className="w-3 h-3" />
            <span>{matchPct}% Match</span>
          </div>
        </div>

        {/* Issue Title */}
        <h3 className="text-base font-semibold text-white group-hover:text-[#58a6ff] transition-colors mb-2 leading-snug">
          <a href={issue.html_url} target="_blank" rel="noreferrer" className="flex items-start gap-1.5">
            <span>{issue.title}</span>
            <ExternalLink className="w-3.5 h-3.5 shrink-0 opacity-0 group-hover:opacity-100 transition-opacity mt-1 text-[#58a6ff]" />
          </a>
        </h3>

        {/* Issue Body Preview */}
        <p className="text-xs text-[#8b949e] line-clamp-2 mb-3 leading-relaxed">
          {issue.body || 'No description provided.'}
        </p>

        {/* Labels & Tags */}
        <div className="flex flex-wrap items-center gap-1.5 mb-3.5">
          {repo?.language && (
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-[#21262d] text-[#c9d1d9] border border-[#30363d]">
              <span className="w-2 h-2 rounded-full" style={{ backgroundColor: langColor }}></span>
              {repo.language}
            </span>
          )}

          {issue.is_beginner_friendly && (
            <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-950/40 text-emerald-400 border border-emerald-600/40">
              🌱 Good First Issue
            </span>
          )}

          {(issue.labels || '').split(',').filter(l => l.trim() && !l.includes('good first issue')).slice(0, 3).map((lbl) => (
            <span
              key={lbl}
              className="px-2 py-0.5 rounded-full text-[10px] font-normal bg-[#21262d] text-[#8b949e] border border-[#30363d]"
            >
              {lbl.trim()}
            </span>
          ))}

          <span className="text-[11px] text-[#8b949e] flex items-center gap-1 ml-auto">
            <MessageSquare className="w-3 h-3" />
            {issue.comments_count} comments
          </span>
        </div>

        {/* "Why This Was Recommended" Explainability Banner */}
        <div className="bg-[#0d1117] border border-[#30363d] rounded-xl p-3 mb-3 text-xs">
          <div className="flex items-center justify-between text-[#c9d1d9] font-medium mb-1">
            <span className="text-emerald-400 flex items-center gap-1.5 font-semibold text-[11px] uppercase tracking-wider">
              <Sparkles className="w-3.5 h-3.5" /> Why recommended:
            </span>
            <button
              onClick={() => setShowBreakdown(!showBreakdown)}
              className="text-[11px] text-[#8b949e] hover:text-[#c9d1d9] flex items-center gap-0.5 transition-colors"
            >
              <span>{showBreakdown ? 'Hide Breakdown' : 'Feature Breakdown'}</span>
              {showBreakdown ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
            </button>
          </div>
          <p className="text-[11px] text-[#8b949e] leading-relaxed">
            {item.why_recommended}
          </p>

          {/* Detailed feature weights breakdown (collapsible) */}
          {showBreakdown && (
            <div className="mt-2.5 pt-2.5 border-t border-[#30363d] space-y-1.5 text-[10px]">
              <div className="flex justify-between items-center text-[#8b949e]">
                <span>Content Semantic Similarity:</span>
                <span className="font-mono text-white">{Math.round(item.breakdown.content_similarity * 100)}%</span>
              </div>
              <div className="w-full bg-[#21262d] h-1.5 rounded-full overflow-hidden">
                <div className="bg-blue-500 h-full rounded-full" style={{ width: `${Math.min(100, item.breakdown.content_similarity * 100)}%` }}></div>
              </div>

              <div className="flex justify-between items-center text-[#8b949e] pt-1">
                <span>Collaborative (ALS) Affinity:</span>
                <span className="font-mono text-white">{Math.round(item.breakdown.collaborative_score * 100)}%</span>
              </div>
              <div className="w-full bg-[#21262d] h-1.5 rounded-full overflow-hidden">
                <div className="bg-purple-500 h-full rounded-full" style={{ width: `${Math.min(100, item.breakdown.collaborative_score * 100)}%` }}></div>
              </div>

              <div className="grid grid-cols-2 gap-2 pt-1 text-[#8b949e]">
                <div>Language Match: <strong className="text-white font-mono">{item.breakdown.language_match > 0 ? 'Yes' : 'No'}</strong></div>
                <div>Repo Stars: <strong className="text-white font-mono">{Math.round(item.breakdown.popularity_score * 100)}%</strong></div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Action Footer: Feedback Buttons & View on GitHub */}
      <div className="pt-2 border-t border-[#30363d]/60 flex items-center justify-between">
        <div className="flex items-center space-x-1.5">
          <button
            onClick={() => handleFeedbackClick('like')}
            disabled={isSubmitting}
            className={`p-1.5 rounded-lg border text-xs font-medium transition-all flex items-center gap-1 ${
              feedbackGiven === 'like'
                ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/60'
                : 'bg-[#21262d] text-[#8b949e] border-[#30363d] hover:text-[#c9d1d9] hover:bg-[#30363d]'
            }`}
            title="Relevant & interesting (boosts future suggestions)"
          >
            <ThumbsUp className="w-3.5 h-3.5" />
            <span className="text-[11px] hidden sm:inline">Relevant</span>
          </button>

          <button
            onClick={() => handleFeedbackClick('dislike')}
            disabled={isSubmitting}
            className={`p-1.5 rounded-lg border text-xs font-medium transition-all flex items-center gap-1 ${
              feedbackGiven === 'dislike'
                ? 'bg-red-500/20 text-red-400 border-red-500/60'
                : 'bg-[#21262d] text-[#8b949e] border-[#30363d] hover:text-[#c9d1d9] hover:bg-[#30363d]'
            }`}
            title="Not interested"
          >
            <ThumbsDown className="w-3.5 h-3.5" />
          </button>

          <button
            onClick={() => handleFeedbackClick('saved')}
            disabled={isSubmitting}
            className={`p-1.5 rounded-lg border text-xs font-medium transition-all flex items-center gap-1 ${
              feedbackGiven === 'saved'
                ? 'bg-blue-500/20 text-blue-400 border-blue-500/60'
                : 'bg-[#21262d] text-[#8b949e] border-[#30363d] hover:text-[#c9d1d9] hover:bg-[#30363d]'
            }`}
            title="Save for later"
          >
            <Bookmark className="w-3.5 h-3.5" />
          </button>
        </div>

        <a
          href={issue.html_url}
          target="_blank"
          rel="noreferrer"
          className="flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-[#21262d] hover:bg-[#30363d] text-white text-xs font-medium border border-[#30363d] transition-all hover:border-[#8b949e]"
        >
          <span>Open on GitHub</span>
          <ExternalLink className="w-3 h-3 text-[#58a6ff]" />
        </a>
      </div>
    </div>
  );
};
