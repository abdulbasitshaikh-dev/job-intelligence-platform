import React, { useState } from 'react';
import { Bookmark, ExternalLink, MapPin, Building, Calendar, DollarSign, Sparkles, AlertCircle } from 'lucide-react';
import { Job, User } from '../types';

interface JobCardProps {
  job: Job;
  currentUser?: User | null;
  onSaveToggle: (jobId: number, isSaved: boolean) => void;
  onApplicationChange: (jobId: number, status: string) => void;
  onShowMatchDetails?: (job: Job) => void;
  onRequireAuth?: () => void;
}

export const JobCard: React.FC<JobCardProps> = ({
  job,
  currentUser,
  onSaveToggle,
  onApplicationChange,
  onShowMatchDetails,
  onRequireAuth,
}) => {
  const [isSaved, setIsSaved] = useState(job.is_saved || false);
  const [appStatus, setAppStatus] = useState(job.application_status || 'none');

  const handleSaveClick = () => {
    if (!currentUser) {
      onRequireAuth?.();
      return;
    }
    const nextSaved = !isSaved;
    setIsSaved(nextSaved);
    onSaveToggle(job.id, isSaved);
  };

  const handleStatusChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value;
    if (!currentUser) {
      onRequireAuth?.();
      return;
    }
    setAppStatus(val);
    if (val !== 'none') {
      onApplicationChange(job.id, val);
    }
  };

  const getCurrencySymbol = (curr?: string) => {
    if (!curr) return '$';
    const c = curr.toUpperCase();
    if (c === 'EUR') return '€';
    if (c === 'GBP') return '£';
    if (c === 'USD') return '$';
    return `${c} `;
  };

  const formatSalaryText = () => {
    const min = job.salary_min;
    const max = job.salary_max;
    if (!min && !max) return null;
    const symbol = getCurrencySymbol(job.currency);

    if (min && max) {
      return `${symbol}${Number(min).toLocaleString()} - ${symbol}${Number(max).toLocaleString()}`;
    }
    if (min) return `From ${symbol}${Number(min).toLocaleString()}`;
    if (max) return `Up to ${symbol}${Number(max).toLocaleString()}`;
    return null;
  };

  const getMatchScoreBadge = () => {
    if (!currentUser) return null;
    if (job.match_score === undefined || job.match_score === null) {
      return (
        <button
          onClick={() => onShowMatchDetails?.(job)}
          className="flex items-center space-x-1.5 px-3 py-1 rounded-full text-[11px] font-medium border border-slate-800 bg-slate-900/60 text-slate-400 hover:text-cyan-400 hover:border-cyan-500/30 transition-all"
          title="Configure preferences to see personalized match score"
        >
          <Sparkles className="w-3 h-3 text-slate-500" />
          <span>Set preferences to match</span>
        </button>
      );
    }

    const score = job.match_score;
    let colorClass = 'bg-slate-800 text-slate-400 border-slate-700';
    if (score >= 75) colorClass = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
    else if (score >= 50) colorClass = 'bg-amber-500/10 text-amber-400 border-amber-500/30';
    else if (score > 0) colorClass = 'bg-sky-500/10 text-sky-400 border-sky-500/30';

    return (
      <button
        onClick={() => onShowMatchDetails?.(job)}
        className={`flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold border transition-transform hover:scale-105 ${colorClass}`}
        title="Click to view match explanation"
      >
        <Sparkles className="w-3.5 h-3.5" />
        <span>{score > 0 ? `Match ${score}%` : 'Match 0%'}</span>
      </button>
    );
  };

  const salaryDisplay = formatSalaryText();

  return (
    <div className={`glass-card rounded-xl p-5 relative flex flex-col justify-between group ${!job.is_active ? 'opacity-75 border-slate-800/50' : ''}`}>
      <div>
        {/* Header line */}
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-cyan-400 truncate">
                Source: {job.source_name || 'Public Source'}
              </span>
              {!job.is_active && (
                <span className="px-2 py-0.2 rounded text-[10px] font-bold uppercase bg-rose-500/10 text-rose-400 border border-rose-500/30">
                  Inactive / Expired
                </span>
              )}
            </div>
            <h3 className="text-lg font-bold text-white group-hover:text-cyan-300 transition-colors mt-0.5 line-clamp-1">
              {job.title}
            </h3>
            <div className="flex items-center space-x-3 text-sm text-slate-400 mt-1">
              <span className="flex items-center space-x-1 font-medium text-slate-300 truncate">
                <Building className="w-4 h-4 text-slate-500 shrink-0" />
                <span className="truncate">{job.company}</span>
              </span>
              <span className="flex items-center space-x-1 shrink-0">
                <MapPin className="w-4 h-4 text-slate-500 shrink-0" />
                <span>{job.location}</span>
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-2 shrink-0">
            {getMatchScoreBadge()}
            <button
              onClick={handleSaveClick}
              className={`p-2 rounded-lg border transition-all ${
                isSaved
                  ? 'bg-amber-500/20 text-amber-400 border-amber-500/40'
                  : 'bg-slate-900/50 text-slate-400 border-slate-800 hover:text-white'
              }`}
              title={isSaved ? 'Unsave job' : 'Save job'}
            >
              <Bookmark className={`w-4 h-4 ${isSaved ? 'fill-amber-400' : ''}`} />
            </button>
          </div>
        </div>

        {/* Badges line */}
        <div className="flex flex-wrap items-center gap-2 mt-4">
          <span className="px-2.5 py-1 rounded-md text-xs font-medium bg-slate-800/80 text-slate-300 border border-slate-700/50">
            {job.work_mode}
          </span>
          <span className="px-2.5 py-1 rounded-md text-xs font-medium bg-slate-800/80 text-slate-300 border border-slate-700/50">
            {job.employment_type}
          </span>
          {salaryDisplay ? (
            <span className="px-2.5 py-1 rounded-md text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center space-x-1">
              <DollarSign className="w-3 h-3" />
              <span>{salaryDisplay}</span>
            </span>
          ) : (
            <span className="px-2.5 py-1 rounded-md text-xs font-medium bg-slate-900 text-slate-500 border border-slate-800">
              Salary not disclosed
            </span>
          )}
        </div>

        {/* Snippet Description */}
        <p className="text-sm text-slate-400 mt-3 line-clamp-2 leading-relaxed">
          {job.description}
        </p>
      </div>

      {/* Footer controls */}
      <div className="flex items-center justify-between pt-4 mt-4 border-t border-slate-800/80">
        <div className="flex items-center space-x-2">
          <span className="text-xs text-slate-500 flex items-center space-x-1">
            <Calendar className="w-3.5 h-3.5" />
            <span>
              {job.posted_at ? new Date(job.posted_at).toLocaleDateString() : 'Recently posted'}
            </span>
          </span>
        </div>

        <div className="flex items-center space-x-3">
          {/* Application Tracker Selector - authenticated only */}
          {currentUser ? (
            <select
              value={appStatus}
              onChange={handleStatusChange}
              className="bg-slate-900 text-xs font-medium text-slate-300 border border-slate-800 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-cyan-500 transition-colors"
            >
              <option value="none">Set Status...</option>
              <option value="interested">Interested</option>
              <option value="applied">Applied</option>
              <option value="interview">Interviewing</option>
              <option value="offer">Received Offer</option>
              <option value="rejected">Rejected</option>
              <option value="withdrawn">Withdrawn</option>
            </select>
          ) : (
            <button
              onClick={onRequireAuth}
              className="text-xs font-medium text-slate-400 hover:text-cyan-400 transition-colors"
            >
              Track Application
            </button>
          )}

          <a
            href={job.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center space-x-1 px-3 py-1.5 rounded-lg text-xs font-medium bg-cyan-600/20 text-cyan-400 hover:bg-cyan-600/30 border border-cyan-500/30 transition-all"
          >
            <span>Apply</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
      </div>
    </div>
  );
};

