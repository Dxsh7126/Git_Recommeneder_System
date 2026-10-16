import React from 'react';
import { Search, Filter, Zap } from 'lucide-react';

interface FilterBarProps {
  searchQuery: string;
  onSearchChange: (q: string) => void;
  selectedLanguage: string;
  onLanguageChange: (lang: string) => void;
  beginnerOnly: boolean;
  onToggleBeginnerOnly: () => void;
  latencyMs: number;
  totalFound: number;
}

const LANGUAGES = ['All', 'Python', 'TypeScript', 'Rust', 'Go'];

export const FilterBar: React.FC<FilterBarProps> = ({
  searchQuery,
  onSearchChange,
  selectedLanguage,
  onLanguageChange,
  beginnerOnly,
  onToggleBeginnerOnly,
  latencyMs,
  totalFound
}) => {
  return (
    <div className="bg-[#161b22] border border-[#30363d] rounded-2xl p-4 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">
      {/* Search Bar */}
      <div className="relative flex-1 max-w-md">
        <Search className="w-4 h-4 text-[#8b949e] absolute left-3 top-1/2 -translate-y-1/2" />
        <input
          type="text"
          placeholder="Filter recommendations by title, keywords or repo..."
          value={searchQuery}
          onChange={(e) => onSearchChange(e.target.value)}
          className="w-full pl-9 pr-4 py-2 bg-[#0d1117] border border-[#30363d] focus:border-emerald-500 rounded-xl text-xs text-white placeholder-[#484f58] focus:outline-none transition-all"
        />
      </div>

      {/* Language filter pills */}
      <div className="flex flex-wrap items-center gap-1.5">
        <span className="text-[11px] text-[#8b949e] mr-1 flex items-center gap-1">
          <Filter className="w-3 h-3" /> Lang:
        </span>
        {LANGUAGES.map((lang) => (
          <button
            key={lang}
            onClick={() => onLanguageChange(lang === 'All' ? '' : lang)}
            className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-all ${
              (lang === 'All' && !selectedLanguage) || selectedLanguage.toLowerCase() === lang.toLowerCase()
                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/50'
                : 'bg-[#0d1117] text-[#8b949e] border border-[#30363d] hover:text-[#c9d1d9]'
            }`}
          >
            {lang}
          </button>
        ))}
      </div>

      {/* Beginner filter & Latency tag */}
      <div className="flex items-center space-x-3 shrink-0">
        <button
          onClick={onToggleBeginnerOnly}
          className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-medium border transition-all ${
            beginnerOnly
              ? 'bg-amber-500/20 text-amber-300 border-amber-500/50 shadow-sm'
              : 'bg-[#0d1117] text-[#8b949e] border-[#30363d] hover:text-[#c9d1d9]'
          }`}
        >
          <span>🌱 Good First Issues Only</span>
        </button>

        <div className="hidden sm:flex items-center space-x-1 text-[11px] text-[#8b949e] bg-[#0d1117] px-2.5 py-1.5 rounded-xl border border-[#30363d]">
          <Zap className="w-3 h-3 text-emerald-400" />
          <span>{latencyMs}ms</span>
          <span className="text-[#484f58]">|</span>
          <span>{totalFound} ranked</span>
        </div>
      </div>
    </div>
  );
};
