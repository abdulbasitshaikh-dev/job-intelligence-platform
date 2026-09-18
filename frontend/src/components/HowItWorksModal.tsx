import React from 'react';
import { X, Layers, Cpu, ShieldCheck, RefreshCw, Sparkles, CheckCircle2 } from 'lucide-react';

interface HowItWorksModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const HowItWorksModal: React.FC<HowItWorksModalProps> = ({ isOpen, onClose }) => {
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
          <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center text-cyan-400">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-xl sm:text-2xl font-bold text-white font-['Outfit']">How JobIntel Works</h2>
            <p className="text-xs text-slate-400">Architecture and pipeline powering intelligent job discovery</p>
          </div>
        </div>

        {/* Step Breakdown */}
        <div className="space-y-6 text-sm text-slate-300">
          <div className="flex gap-4 items-start">
            <div className="w-8 h-8 rounded-lg bg-cyan-500/20 text-cyan-400 flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">
              1
            </div>
            <div>
              <h3 className="text-white font-semibold text-sm flex items-center gap-1.5">
                <Layers className="w-4 h-4 text-cyan-400" />
                Live Ingestion &amp; Legal Adapters
              </h3>
              <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                We collect listings directly from authorized, public developer APIs (RemoteOK, Arbeitnow) using structured httpx adapters with strict rate limits, exponential backoff, and robust schema validation.
              </p>
            </div>
          </div>

          <div className="flex gap-4 items-start">
            <div className="w-8 h-8 rounded-lg bg-sky-500/20 text-sky-400 flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">
              2
            </div>
            <div>
              <h3 className="text-white font-semibold text-sm flex items-center gap-1.5">
                <Cpu className="w-4 h-4 text-sky-400" />
                Canonical Normalization &amp; Deduplication
              </h3>
              <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                Raw postings are cleaned: HTML tags stripped, salaries parsed with bound inversion correction, locations deduplicated (e.g. &ldquo;California, California, US&rdquo; &rarr; &ldquo;California, US&rdquo;), and assigned a SHA-256 fingerprint to eliminate cross-source duplicates.
              </p>
            </div>
          </div>

          <div className="flex gap-4 items-start">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">
              3
            </div>
            <div>
              <h3 className="text-white font-semibold text-sm flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                Two-Tier Relevance &amp; Deterministic Matching
              </h3>
              <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                <strong>Search Relevance</strong> ranks keyword matches (Title match &gt; Company match &gt; Description). In parallel, your <strong>Match Score</strong> evaluates 5 dimensions (Role, Skills, Work Mode, Location, Salary) out of 100 points with transparent explainability.
              </p>
            </div>
          </div>

          <div className="flex gap-4 items-start">
            <div className="w-8 h-8 rounded-lg bg-purple-500/20 text-purple-400 flex items-center justify-center font-bold text-xs shrink-0 mt-0.5">
              4
            </div>
            <div>
              <h3 className="text-white font-semibold text-sm flex items-center gap-1.5">
                <RefreshCw className="w-4 h-4 text-purple-400" />
                Lifecycle Management &amp; Secure Alerts
              </h3>
              <p className="text-xs text-slate-400 mt-1 leading-relaxed">
                Listings unseen for 30 days are automatically marked inactive. When new jobs match your preferences above your chosen threshold, SSRF-hardened webhook notifications (with HMAC signatures) or email digests keep you ahead.
              </p>
            </div>
          </div>
        </div>

        <div className="mt-8 pt-4 border-t border-slate-800 flex justify-end">
          <button
            onClick={onClose}
            className="px-5 py-2 rounded-xl text-xs font-semibold bg-cyan-600 hover:bg-cyan-500 text-white transition-all shadow-md shadow-cyan-600/20"
          >
            Got it, take me to jobs
          </button>
        </div>
      </div>
    </div>
  );
};
