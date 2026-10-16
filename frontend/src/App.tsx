import React, { useEffect, useState, useMemo } from 'react';
import { Developer, RecommendationResponse, RecommendationItem, EvaluationMetrics } from './types';
import { api } from './services/api';
import { Navbar } from './components/Navbar';
import { DeveloperSelector } from './components/DeveloperSelector';
import { AlgorithmSelector } from './components/AlgorithmSelector';
import { FilterBar } from './components/FilterBar';
import { IssueCard } from './components/IssueCard';
import { MetricsModal } from './components/MetricsModal';
import { GitPullRequest, AlertCircle, Sparkles, RefreshCw } from 'lucide-react';

export const App: React.FC = () => {
  const [developers, setDevelopers] = useState<Developer[]>([]);
  const [selectedDeveloper, setSelectedDeveloper] = useState<Developer | null>(null);
  const [algorithm, setAlgorithm] = useState<'hybrid' | 'content' | 'collaborative'>('hybrid');
  const [recsData, setRecsData] = useState<RecommendationResponse | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedLanguage, setSelectedLanguage] = useState('');
  const [beginnerOnly, setBeginnerOnly] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isRetraining, setIsRetraining] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Metrics Modal state
  const [isMetricsOpen, setIsMetricsOpen] = useState(false);
  const [metrics, setMetrics] = useState<EvaluationMetrics | null>(null);
  const [isLoadingMetrics, setIsLoadingMetrics] = useState(false);

  // Load initial developers
  useEffect(() => {
    const fetchDevs = async () => {
      try {
        const devs = await api.getDevelopers();
        setDevelopers(devs);
        if (devs.length > 0) {
          // Default to Alex Chen (ML)
          setSelectedDeveloper(devs[0]);
        }
      } catch (err) {
        console.error('Error fetching developers:', err);
      }
    };
    fetchDevs();
  }, []);

  // Fetch recommendations whenever developer, algorithm, language, or beginner filter changes
  useEffect(() => {
    if (!selectedDeveloper) return;

    const fetchRecommendations = async () => {
      setIsLoading(true);
      try {
        const data = await api.getRecommendations(
          selectedDeveloper.id,
          algorithm,
          15,
          selectedLanguage,
          beginnerOnly
        );
        setRecsData(data);
      } catch (err) {
        console.error('Error fetching recommendations:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchRecommendations();
  }, [selectedDeveloper, algorithm, selectedLanguage, beginnerOnly]);

  // Handle live GitHub user import
  const handleImportGithubUser = async (username: string) => {
    const newDev = await api.addGithubDeveloper(username);
    setDevelopers((prev) => {
      const exists = prev.find((d) => d.id === newDev.id);
      if (exists) return prev;
      return [newDev, ...prev];
    });
    setSelectedDeveloper(newDev);
    showToast(`Loaded GitHub profile for @${username}!`);
  };

  // Feedback action handler
  const handleFeedback = async (
    issueId: number,
    action: 'like' | 'dislike' | 'saved' | 'applied'
  ) => {
    if (!selectedDeveloper) return;
    try {
      await api.sendFeedback(selectedDeveloper.id, issueId, action);
      const actionText =
        action === 'like'
          ? 'Marked as relevant 👍'
          : action === 'saved'
          ? 'Saved to bookmarks 🔖'
          : 'Dismissed 👎';
      showToast(`${actionText} — Preference recorded for future ranking.`);
    } catch (err) {
      console.error('Error sending feedback:', err);
    }
  };

  // Retrain model handler
  const handleRetrain = async () => {
    setIsRetraining(true);
    try {
      await api.retrain();
      showToast('LightGBM Ranker and ALS factorization retrained successfully!');
      // Refresh current recommendations
      if (selectedDeveloper) {
        const data = await api.getRecommendations(
          selectedDeveloper.id,
          algorithm,
          15,
          selectedLanguage,
          beginnerOnly
        );
        setRecsData(data);
      }
    } catch (err) {
      console.error('Error during retraining:', err);
    } finally {
      setIsRetraining(false);
    }
  };

  // Metrics Modal Open
  const handleOpenMetrics = async () => {
    setIsMetricsOpen(true);
    setIsLoadingMetrics(true);
    try {
      const m = await api.getMetrics();
      setMetrics(m);
    } catch (err) {
      console.error('Error fetching metrics:', err);
    } finally {
      setIsLoadingMetrics(false);
    }
  };

  const showToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => {
      setToastMessage(null);
    }, 4000);
  };

  // Client-side search filtering
  const filteredRecommendations = useMemo(() => {
    if (!recsData?.recommendations) return [];
    if (!searchQuery.trim()) return recsData.recommendations;

    const q = searchQuery.toLowerCase();
    return recsData.recommendations.filter((item) => {
      const issue = item.issue;
      const repo = issue.repository;
      return (
        issue.title.toLowerCase().includes(q) ||
        (issue.body && issue.body.toLowerCase().includes(q)) ||
        (repo && repo.full_name.toLowerCase().includes(q)) ||
        (issue.labels && issue.labels.toLowerCase().includes(q))
      );
    });
  }, [recsData, searchQuery]);

  return (
    <div className="min-h-screen bg-[#0d1117] text-[#c9d1d9] flex flex-col font-['Inter',sans-serif]">
      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-5 right-5 z-50 bg-emerald-600 text-white px-4 py-2.5 rounded-xl shadow-2xl flex items-center gap-2 text-xs font-medium animate-bounce border border-emerald-400">
          <Sparkles className="w-4 h-4" />
          <span>{toastMessage}</span>
        </div>
      )}

      {/* Top Navbar */}
      <Navbar
        onOpenMetrics={handleOpenMetrics}
        onRetrain={handleRetrain}
        isRetraining={isRetraining}
      />

      {/* Main Content Area */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 flex-1 w-full space-y-6">
        {/* Developer Persona Selector & Cold-start simulation */}
        <DeveloperSelector
          developers={developers}
          selectedDeveloper={selectedDeveloper}
          onSelectDeveloper={setSelectedDeveloper}
          onImportGithubUser={handleImportGithubUser}
          isLoading={isLoading}
        />

        {/* Algorithm Comparison Toggle */}
        <AlgorithmSelector
          currentAlgorithm={algorithm}
          onChangeAlgorithm={setAlgorithm}
          isColdStart={recsData?.is_cold_start ?? false}
        />

        {/* Filters & Search */}
        <FilterBar
          searchQuery={searchQuery}
          onSearchChange={setSearchQuery}
          selectedLanguage={selectedLanguage}
          onLanguageChange={setSelectedLanguage}
          beginnerOnly={beginnerOnly}
          onToggleBeginnerOnly={() => setBeginnerOnly(!beginnerOnly)}
          latencyMs={recsData?.computation_time_ms ?? 0}
          totalFound={filteredRecommendations.length}
        />

        {/* Recommendations Section */}
        {isLoading ? (
          <div className="py-24 text-center text-[#8b949e] flex flex-col items-center justify-center space-y-3">
            <div className="w-10 h-10 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="text-sm font-medium">Running {algorithm} recommender pipeline...</p>
          </div>
        ) : filteredRecommendations.length === 0 ? (
          <div className="py-20 text-center bg-[#161b22] border border-[#30363d] rounded-2xl p-8">
            <AlertCircle className="w-10 h-10 text-[#8b949e] mx-auto mb-3" />
            <h3 className="text-base font-semibold text-white">No matching issues found</h3>
            <p className="text-xs text-[#8b949e] mt-1">
              Try adjusting your language filters or toggle off "Good First Issues Only".
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {filteredRecommendations.map((item) => (
              <IssueCard
                key={item.issue.id}
                item={item}
                onFeedback={handleFeedback}
              />
            ))}
          </div>
        )}
      </main>

      {/* Metrics Modal */}
      <MetricsModal
        isOpen={isMetricsOpen}
        onClose={() => setIsMetricsOpen(false)}
        metrics={metrics}
        isLoading={isLoadingMetrics}
      />

      {/* Footer */}
      <footer className="border-t border-[#30363d] bg-[#161b22] py-6 text-center text-xs text-[#8b949e]">
        <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center space-x-2">
            <GitPullRequest className="w-4 h-4 text-emerald-400" />
            <span className="font-semibold text-white">GitMatch Recommender</span>
            <span>— 4-Week Capstone Engineering Project</span>
          </div>
          <div>
            Built with FastAPI, LightGBM, Implicit ALS, PostgreSQL/SQLite & React 18
          </div>
        </div>
      </footer>
    </div>
  );
};
