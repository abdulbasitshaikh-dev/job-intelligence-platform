import React, { useState, useEffect } from 'react';
import { X, Globe2, ExternalLink, CheckCircle, Clock, AlertTriangle, ShieldCheck } from 'lucide-react';
import { Source } from '../types';
import { ApiClient } from '../lib/api';

interface SourcesModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SourcesModal: React.FC<SourcesModalProps> = ({ isOpen, onClose }) => {
  const [sources, setSources] = useState<Source[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen) return;
    setLoading(true);
    setError(null);
    ApiClient.fetch<Source[]>('/sources')
      .then((data) => setSources(data))
      .catch((err) => setError(err.message || 'Failed to load sources'))
      .finally(() => setLoading(false));
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-2xl bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-6 sm:p-8 max-h-[90vh] overflow-y-auto">
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-5 right-5 text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Title */}
        <div className="flex items-center space-x-3 mb-6">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <Globe2 className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl sm:text-2xl font-bold text-white font-['Outfit']">Supported Job Sources</h2>
            <p className="text-xs text-slate-400">Public &amp; authorized data providers integrated into the platform</p>
          </div>
        </div>

        {/* Sources List */}
        {loading ? (
          <div className="space-y-3 py-8">
            <div className="h-20 bg-slate-800/50 rounded-xl animate-pulse" />
            <div className="h-20 bg-slate-800/50 rounded-xl animate-pulse" />
          </div>
        ) : error ? (
          <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs">
            {error}
          </div>
        ) : sources.length === 0 ? (
          <div className="text-center py-8 text-slate-500 text-sm">
            No public sources registered.
          </div>
        ) : (
          <div className="space-y-4">
            {sources.map((src) => (
              <div
                key={src.id}
                className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 hover:border-slate-700 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="text-sm font-bold text-white">{src.name}</span>
                    <span className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                      {src.source_type}
                    </span>
                  </div>
                  <span
                    className={`inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold ${
                      src.enabled
                        ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                        : 'bg-slate-800 text-slate-400'
                    }`}
                  >
                    {src.enabled ? (
                      <>
                        <CheckCircle className="w-3 h-3" />
                        <span>Active</span>
                      </>
                    ) : (
                      <span>Inactive</span>
                    )}
                  </span>
                </div>

                <div className="mt-2 flex items-center space-x-1 text-xs text-slate-400">
                  <span className="font-mono text-slate-300">{src.base_url}</span>
                  <a
                    href={src.base_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-slate-500 hover:text-cyan-400"
                  >
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>

                <div className="mt-3 flex items-center justify-between text-[11px] text-slate-500 border-t border-slate-900 pt-2">
                  <span className="flex items-center space-x-1">
                    <ShieldCheck className="w-3.5 h-3.5 text-slate-400" />
                    <span>Adapter: <code className="text-slate-300">{src.scraper_type}</code></span>
                  </span>
                  <span className="flex items-center space-x-1">
                    <Clock className="w-3.5 h-3.5" />
                    <span>
                      {src.last_run_at
                        ? `Last sync: ${new Date(src.last_run_at).toLocaleString()}`
                        : 'Scheduled for next cycle'}
                    </span>
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="mt-6 pt-4 border-t border-slate-800 flex justify-between items-center text-xs text-slate-500">
          <span>Integrates only with legal, public APIs with automated rate limiting.</span>
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
