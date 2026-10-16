import React from 'react';
import { GitPullRequest, BarChart3, RefreshCw, ExternalLink, Sparkles } from 'lucide-react';

interface NavbarProps {
  onOpenMetrics: () => void;
  onRetrain: () => void;
  isRetraining: boolean;
}

export const Navbar: React.FC<NavbarProps> = ({ onOpenMetrics, onRetrain, isRetraining }) => {
  return (
    <header className="border-b border-[#30363d] bg-[#161b22]/90 backdrop-blur-md sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-emerald-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-emerald-500/20">
            <GitPullRequest className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-lg text-white tracking-tight">GitMatch</span>
              <span className="px-2 py-0.5 text-xs font-semibold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 flex items-center gap-1">
                <Sparkles className="w-3 h-3" /> v1.0 Production
              </span>
            </div>
            <p className="text-xs text-[#8b949e]">Personalized Open-Source Issue Recommendation Engine</p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={onOpenMetrics}
            className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg bg-[#21262d] hover:bg-[#30363d] text-[#c9d1d9] text-xs font-medium border border-[#30363d] transition-all hover:border-[#8b949e]"
          >
            <BarChart3 className="w-4 h-4 text-emerald-400" />
            <span>Evaluation Metrics & NDCG</span>
          </button>

          <button
            onClick={onRetrain}
            disabled={isRetraining}
            className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg bg-[#238636] hover:bg-[#2ea043] disabled:opacity-50 text-white text-xs font-medium transition-all shadow-sm"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRetraining ? 'animate-spin' : ''}`} />
            <span>{isRetraining ? 'Retraining...' : 'Retrain Ranker'}</span>
          </button>

          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noreferrer"
            className="flex items-center space-x-1 px-3 py-1.5 rounded-lg text-xs font-medium text-[#8b949e] hover:text-[#c9d1d9] hover:bg-[#21262d] transition-all"
          >
            <span>FastAPI Docs</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>
      </div>
    </header>
  );
};
