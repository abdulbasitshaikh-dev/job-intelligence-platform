import React from 'react';
import { Sparkles, X, CheckCircle } from 'lucide-react';
import { Job } from '../types';

interface MatchScoreModalProps {
  job: Job | null;
  onClose: () => void;
}

export const MatchScoreModal: React.FC<MatchScoreModalProps> = ({ job, onClose }) => {
  if (!job) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-fade-in">
      <div className="glass-panel rounded-2xl w-full max-w-lg p-6 relative border border-slate-700 shadow-2xl">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="flex items-center space-x-3 mb-4">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-cyan-500 to-sky-400 flex items-center justify-center text-white shadow-lg shadow-cyan-500/30">
            <Sparkles className="w-6 h-6" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-white font-['Outfit']">Match Score Analysis</h3>
            <p className="text-xs text-slate-400">{job.title} at {job.company}</p>
          </div>
        </div>

        <div className="bg-slate-900/90 rounded-xl p-4 border border-slate-800 text-center mb-5">
          <div className="text-4xl font-extrabold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-sky-300 to-emerald-400">
            {job.match_score || 0}%
          </div>
          <span className="text-xs font-medium text-slate-400 uppercase tracking-wider mt-1 inline-block">
            Match Compatibility Index
          </span>
        </div>

        <h4 className="text-sm font-semibold text-slate-200 mb-3">Score Breakdown:</h4>
        <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
          {job.match_reasons && job.match_reasons.length > 0 ? (
            job.match_reasons.map((reason, idx) => (
              <div key={idx} className="flex items-start space-x-3 bg-slate-900/50 p-3 rounded-lg border border-slate-800/80">
                <CheckCircle className="w-4 h-4 text-emerald-400 mt-0.5 shrink-0" />
                <span className="text-sm text-slate-300">{reason}</span>
              </div>
            ))
          ) : (
            <p className="text-sm text-slate-400 text-center py-3">
              Configure your preferences (keywords, location, work mode) to calculate score breakdowns.
            </p>
          )}
        </div>

        <button
          onClick={onClose}
          className="w-full mt-6 py-2.5 rounded-xl font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 transition-all text-sm"
        >
          Close
        </button>
      </div>
    </div>
  );
};
