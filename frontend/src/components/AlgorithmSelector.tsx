import React from 'react';
import { Layers, FileText, Users2, Sparkles, HelpCircle } from 'lucide-react';

interface AlgorithmSelectorProps {
  currentAlgorithm: 'hybrid' | 'content' | 'collaborative';
  onChangeAlgorithm: (algo: 'hybrid' | 'content' | 'collaborative') => void;
  isColdStart: boolean;
}

export const AlgorithmSelector: React.FC<AlgorithmSelectorProps> = ({
  currentAlgorithm,
  onChangeAlgorithm,
  isColdStart
}) => {
  return (
    <div className="bg-[#161b22] border border-[#30363d] rounded-2xl p-4 shadow-md">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3">
        <div className="flex items-center space-x-2">
          <Layers className="w-4 h-4 text-emerald-400" />
          <span className="text-xs font-semibold text-white tracking-wide uppercase">Recommender Engine Model</span>
          <span className="text-[11px] text-[#8b949e]">(Toggle to compare algorithmic outputs)</span>
        </div>

        {isColdStart && currentAlgorithm === 'hybrid' && (
          <div className="flex items-center space-x-1.5 px-2.5 py-1 bg-amber-500/10 border border-amber-500/30 rounded-lg text-[11px] text-amber-300">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Cold-start detected: Engine fell back to semantic content ranking + beginner boost</span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
        {/* Hybrid Ranker */}
        <button
          onClick={() => onChangeAlgorithm('hybrid')}
          className={`p-3 rounded-xl border text-left transition-all relative ${
            currentAlgorithm === 'hybrid'
              ? 'bg-gradient-to-r from-emerald-950/40 to-[#161b22] border-emerald-500 text-white shadow-lg'
              : 'bg-[#0d1117] border-[#30363d] text-[#8b949e] hover:border-[#8b949e]'
          }`}
        >
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs font-bold flex items-center gap-1.5 text-white">
              <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
              Hybrid LightGBM Ranker
            </span>
            <span className="text-[10px] bg-emerald-500/20 text-emerald-300 font-semibold px-1.5 py-0.5 rounded">
              Recommended
            </span>
          </div>
          <p className="text-[11px] leading-relaxed opacity-85">
            Non-linear GBDT ensemble combining content cosine similarity, ALS matrix factors, and issue metadata.
          </p>
        </button>

        {/* Content-Based Only */}
        <button
          onClick={() => onChangeAlgorithm('content')}
          className={`p-3 rounded-xl border text-left transition-all ${
            currentAlgorithm === 'content'
              ? 'bg-gradient-to-r from-blue-950/40 to-[#161b22] border-blue-500 text-white shadow-lg'
              : 'bg-[#0d1117] border-[#30363d] text-[#8b949e] hover:border-[#8b949e]'
          }`}
        >
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs font-bold flex items-center gap-1.5 text-white">
              <FileText className="w-3.5 h-3.5 text-blue-400" />
              Content-Based Only
            </span>
          </div>
          <p className="text-[11px] leading-relaxed opacity-85">
            Hand-computed NumPy Cosine Similarity over TF-IDF vectors of issue text and developer repo summaries.
          </p>
        </button>

        {/* Collaborative Filtering Only */}
        <button
          onClick={() => onChangeAlgorithm('collaborative')}
          className={`p-3 rounded-xl border text-left transition-all ${
            currentAlgorithm === 'collaborative'
              ? 'bg-gradient-to-r from-purple-950/40 to-[#161b22] border-purple-500 text-white shadow-lg'
              : 'bg-[#0d1117] border-[#30363d] text-[#8b949e] hover:border-[#8b949e]'
          }`}
        >
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs font-bold flex items-center gap-1.5 text-white">
              <Users2 className="w-3.5 h-3.5 text-purple-400" />
              Collaborative Filtering (ALS)
            </span>
            <span className="text-[10px] bg-purple-500/20 text-purple-300 font-semibold px-1.5 py-0.5 rounded">
              Implicit Feedback
            </span>
          </div>
          <p className="text-[11px] leading-relaxed opacity-85">
            Alternating Least Squares (Hu, Koren & Volinsky) decomposing the developer-issue implicit interaction matrix.
          </p>
        </button>
      </div>
    </div>
  );
};
