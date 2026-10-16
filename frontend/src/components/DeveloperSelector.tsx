import React, { useState } from 'react';
import { Developer } from '../types';
import { User, Sparkles, Plus, Check, AlertCircle, Code2, Globe } from 'lucide-react';

interface DeveloperSelectorProps {
  developers: Developer[];
  selectedDeveloper: Developer | null;
  onSelectDeveloper: (dev: Developer) => void;
  onImportGithubUser: (username: string) => Promise<void>;
  isLoading: boolean;
}

export const DeveloperSelector: React.FC<DeveloperSelectorProps> = ({
  developers,
  selectedDeveloper,
  onSelectDeveloper,
  onImportGithubUser,
  isLoading
}) => {
  const [customUsername, setCustomUsername] = useState('');
  const [isImporting, setIsImporting] = useState(false);
  const [importError, setImportError] = useState('');

  const handleImport = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!customUsername.trim()) return;
    setIsImporting(true);
    setImportError('');
    try {
      await onImportGithubUser(customUsername.trim());
      setCustomUsername('');
    } catch (err: any) {
      setImportError('Failed to import user profile. Try another handle.');
    } finally {
      setIsImporting(false);
    }
  };

  return (
    <div className="bg-[#161b22] border border-[#30363d] rounded-2xl p-5 shadow-xl">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-5">
        <div>
          <h2 className="text-sm font-semibold text-white tracking-wide uppercase flex items-center gap-2">
            <User className="w-4 h-4 text-emerald-400" />
            Developer Profile & Cold-Start Simulation
          </h2>
          <p className="text-xs text-[#8b949e] mt-0.5">
            Switch between developer personas to demonstrate how the recommender tailors issues across languages, skills, and cold-start newcomers.
          </p>
        </div>

        {/* Live GitHub handle fetcher */}
        <form onSubmit={handleImport} className="flex items-center gap-2">
          <div className="relative">
            <span className="absolute left-3 top-1/2 -translate-y-1/2 text-xs text-[#8b949e]">@</span>
            <input
              type="text"
              placeholder="github_username"
              value={customUsername}
              onChange={(e) => setCustomUsername(e.target.value)}
              className="pl-7 pr-3 py-1.5 bg-[#0d1117] border border-[#30363d] focus:border-emerald-500 rounded-lg text-xs text-white placeholder-[#484f58] focus:outline-none w-44"
            />
          </div>
          <button
            type="submit"
            disabled={isImporting || !customUsername.trim()}
            className="px-3 py-1.5 bg-[#21262d] hover:bg-[#30363d] disabled:opacity-40 text-xs font-medium text-emerald-400 border border-[#30363d] rounded-lg transition-all flex items-center gap-1"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>{isImporting ? 'Importing...' : 'Simulate'}</span>
          </button>
        </form>
      </div>

      {importError && (
        <div className="mb-4 text-xs text-red-400 bg-red-950/30 border border-red-800/40 px-3 py-2 rounded-lg flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{importError}</span>
        </div>
      )}

      {/* Personas Carousel / Grid */}
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2.5">
        {developers.map((dev) => {
          const isSelected = selectedDeveloper?.id === dev.id;
          const isElenaCold = dev.username.includes('elena') || dev.username.includes('newbie');

          return (
            <button
              key={dev.id}
              onClick={() => onSelectDeveloper(dev)}
              className={`relative p-3 rounded-xl border text-left transition-all flex flex-col justify-between ${
                isSelected
                  ? 'bg-emerald-950/20 border-emerald-500/80 shadow-md shadow-emerald-500/10'
                  : 'bg-[#0d1117] border-[#30363d] hover:border-[#8b949e]/60 hover:bg-[#161b22]'
              }`}
            >
              <div className="flex items-center space-x-2.5 mb-2">
                <img
                  src={dev.avatar_url || `https://github.com/${dev.username}.png`}
                  alt={dev.name || dev.username}
                  className="w-8 h-8 rounded-full border border-[#30363d] object-cover shrink-0"
                  onError={(e) => {
                    (e.target as HTMLElement).style.display = 'none';
                  }}
                />
                <div className="min-w-0">
                  <div className="text-xs font-semibold text-white truncate flex items-center gap-1">
                    {dev.name?.split(' ')[0] || dev.username}
                    {isSelected && <Check className="w-3 h-3 text-emerald-400 inline" />}
                  </div>
                  <div className="text-[10px] text-[#8b949e] truncate">@{dev.username}</div>
                </div>
              </div>

              {isElenaCold && (
                <span className="text-[9px] font-bold text-amber-300 bg-amber-500/10 border border-amber-500/30 px-1.5 py-0.5 rounded-full inline-block mb-1.5 text-center">
                  ❄️ Cold Start
                </span>
              )}

              <div className="flex flex-wrap gap-1 mt-auto">
                {(dev.languages || '').split(',').slice(0, 2).map((lang) => (
                  <span
                    key={lang}
                    className="text-[9px] px-1.5 py-0.5 rounded bg-[#21262d] text-[#c9d1d9] border border-[#30363d]"
                  >
                    {lang.trim()}
                  </span>
                ))}
              </div>
            </button>
          );
        })}
      </div>

      {/* Selected profile detail bar */}
      {selectedDeveloper && (
        <div className="mt-4 pt-4 border-t border-[#30363d]/60 flex flex-col md:flex-row md:items-center justify-between text-xs text-[#8b949e] gap-3">
          <div className="flex items-start md:items-center gap-3">
            <span className="font-medium text-white">{selectedDeveloper.name || selectedDeveloper.username}:</span>
            <span className="line-clamp-1 italic text-[#8b949e]">{selectedDeveloper.bio}</span>
          </div>
          <div className="flex items-center gap-3 shrink-0">
            <span className="flex items-center gap-1 text-[#c9d1d9]">
              <Code2 className="w-3.5 h-3.5 text-emerald-400" />
              Stack: <strong className="text-white font-mono">{selectedDeveloper.languages || 'General'}</strong>
            </span>
          </div>
        </div>
      )}
    </div>
  );
};
