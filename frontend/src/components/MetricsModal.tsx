import React from 'react';
import { EvaluationMetrics } from '../types';
import { X, Award, BarChart2, TrendingUp, Layers, HelpCircle, CheckCircle2 } from 'lucide-react';

interface MetricsModalProps {
  isOpen: boolean;
  onClose: () => void;
  metrics: EvaluationMetrics | null;
  isLoading: boolean;
}

export const MetricsModal: React.FC<MetricsModalProps> = ({
  isOpen,
  onClose,
  metrics,
  isLoading
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-fade-in">
      <div className="bg-[#161b22] border border-[#30363d] rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
        {/* Header */}
        <div className="p-6 border-b border-[#30363d] flex items-center justify-between sticky top-0 bg-[#161b22]/95 backdrop-blur z-10">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
              <Award className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white tracking-tight">Offline Evaluation & Model Benchmarks</h2>
              <p className="text-xs text-[#8b949e]">Time-based holdout evaluation across NDCG@10, Recall@K, and MRR</p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 text-[#8b949e] hover:text-white rounded-lg hover:bg-[#21262d] transition-all"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 space-y-6">
          {isLoading || !metrics ? (
            <div className="py-16 text-center text-[#8b949e] flex flex-col items-center justify-center space-y-3">
              <div className="w-8 h-8 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin"></div>
              <p className="text-xs">Computing offline holdout metrics across test split...</p>
            </div>
          ) : (
            <>
              {/* Metric Highlights Grid */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <div className="bg-[#0d1117] border border-[#30363d] rounded-xl p-4">
                  <div className="text-[11px] font-medium text-[#8b949e] uppercase tracking-wider mb-1">
                    NDCG@10
                  </div>
                  <div className="text-2xl font-bold text-emerald-400 font-mono">
                    {metrics.ndcg_at_10.toFixed(4)}
                  </div>
                  <div className="text-[10px] text-[#8b949e] mt-1">Ranking order fidelity</div>
                </div>

                <div className="bg-[#0d1117] border border-[#30363d] rounded-xl p-4">
                  <div className="text-[11px] font-medium text-[#8b949e] uppercase tracking-wider mb-1">
                    Recall@5
                  </div>
                  <div className="text-2xl font-bold text-blue-400 font-mono">
                    {metrics.recall_at_5.toFixed(4)}
                  </div>
                  <div className="text-[10px] text-[#8b949e] mt-1">Hits in top 5 suggestions</div>
                </div>

                <div className="bg-[#0d1117] border border-[#30363d] rounded-xl p-4">
                  <div className="text-[11px] font-medium text-[#8b949e] uppercase tracking-wider mb-1">
                    Recall@10
                  </div>
                  <div className="text-2xl font-bold text-purple-400 font-mono">
                    {metrics.recall_at_10.toFixed(4)}
                  </div>
                  <div className="text-[10px] text-[#8b949e] mt-1">Coverage in top 10</div>
                </div>

                <div className="bg-[#0d1117] border border-[#30363d] rounded-xl p-4">
                  <div className="text-[11px] font-medium text-[#8b949e] uppercase tracking-wider mb-1">
                    MRR
                  </div>
                  <div className="text-2xl font-bold text-amber-400 font-mono">
                    {metrics.mrr.toFixed(4)}
                  </div>
                  <div className="text-[10px] text-[#8b949e] mt-1">Mean Reciprocal Rank</div>
                </div>
              </div>

              {/* Model Comparison Table */}
              <div className="bg-[#0d1117] border border-[#30363d] rounded-xl overflow-hidden">
                <div className="px-4 py-3 border-b border-[#30363d] flex items-center justify-between">
                  <span className="text-xs font-semibold text-white uppercase tracking-wider flex items-center gap-2">
                    <BarChart2 className="w-4 h-4 text-emerald-400" />
                    Model Comparison on Holdout Test Split
                  </span>
                  <span className="text-[11px] text-[#8b949e] font-mono">
                    {metrics.total_eval_samples} evaluation interactions
                  </span>
                </div>

                <table className="w-full text-xs text-left">
                  <thead className="bg-[#161b22] text-[#8b949e] uppercase text-[10px] border-b border-[#30363d]">
                    <tr>
                      <th className="py-2.5 px-4 font-semibold">Algorithm</th>
                      <th className="py-2.5 px-4 font-semibold text-right">NDCG@10</th>
                      <th className="py-2.5 px-4 font-semibold text-right">Recall@5</th>
                      <th className="py-2.5 px-4 font-semibold text-right">Recall@10</th>
                      <th className="py-2.5 px-4 font-semibold text-right">MRR</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-[#30363d]/60">
                    {metrics.model_comparison.map((row, idx) => (
                      <tr
                        key={row.model}
                        className={idx === 0 ? 'bg-emerald-950/20 font-semibold' : 'text-[#8b949e]'}
                      >
                        <td className="py-3 px-4 flex items-center gap-2 text-white">
                          {idx === 0 && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />}
                          <span>{row.model}</span>
                        </td>
                        <td className="py-3 px-4 text-right font-mono text-emerald-400">{row.ndcg_at_10.toFixed(4)}</td>
                        <td className="py-3 px-4 text-right font-mono text-blue-400">{row.recall_at_5.toFixed(4)}</td>
                        <td className="py-3 px-4 text-right font-mono text-purple-400">{row.recall_at_10.toFixed(4)}</td>
                        <td className="py-3 px-4 text-right font-mono text-amber-400">{row.mrr.toFixed(4)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Feature Importance Distribution */}
              <div className="bg-[#0d1117] border border-[#30363d] rounded-xl p-4">
                <h3 className="text-xs font-semibold text-white uppercase tracking-wider mb-3 flex items-center gap-2">
                  <TrendingUp className="w-4 h-4 text-emerald-400" />
                  LightGBM GBDT Feature Importance Weights
                </h3>
                <div className="space-y-2.5 text-xs">
                  {Object.entries(metrics.feature_importances)
                    .sort(([, a], [, b]) => b - a)
                    .map(([name, weight]) => (
                      <div key={name}>
                        <div className="flex justify-between items-center text-[#8b949e] text-[11px] mb-1">
                          <span className="font-mono text-[#c9d1d9]">{name}</span>
                          <span className="font-mono font-semibold text-white">{(weight * 100).toFixed(1)}%</span>
                        </div>
                        <div className="w-full bg-[#21262d] h-2 rounded-full overflow-hidden">
                          <div
                            className="bg-gradient-to-r from-emerald-500 to-cyan-500 h-full rounded-full transition-all duration-500"
                            style={{ width: `${Math.min(100, weight * 100)}%` }}
                          ></div>
                        </div>
                      </div>
                    ))}
                </div>
              </div>

              {/* Theoretical Talking Points for Professor */}
              <div className="bg-[#161b22] border border-[#30363d] rounded-xl p-4 text-xs text-[#8b949e] space-y-2">
                <div className="font-semibold text-white flex items-center gap-1.5 text-xs">
                  <HelpCircle className="w-4 h-4 text-emerald-400" />
                  Key Theoretical Highlights for Interview / Professor
                </div>
                <ul className="list-disc list-inside space-y-1.5 leading-relaxed text-[11px]">
                  <li>
                    <strong className="text-white">Why Hybrid beats single models:</strong> Content-based excels at cold start and language matching but suffers from popularity bias and cannot model latent community affinity. Collaborative filtering discovers unexpected relevant projects but fails completely on new users (cold start). The LightGBM hybrid ranker fuses both with non-linear tree splits.
                  </li>
                  <li>
                    <strong className="text-white">Implicit ALS formulation:</strong> Uses confidence weighting <code className="text-emerald-300">c_ui = 1 + α * r_ui</code> (with α = 40) where unobserved interactions are treated as low confidence negatives rather than true zeros.
                  </li>
                  <li>
                    <strong className="text-white">Cold-start fallback:</strong> When interaction count ≤ 1, collaborative latent factor scoring is zeroed, and ranking smoothly transitions to pure semantic cosine similarity + beginner friendliness boost.
                  </li>
                </ul>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};
