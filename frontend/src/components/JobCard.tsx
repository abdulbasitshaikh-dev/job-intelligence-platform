import React, { useState } from 'react';
import { Bookmark, ExternalLink, MapPin, Building, Calendar, DollarSign, Sparkles, CheckCircle2, AlertCircle } from 'lucide-react';
import { Job } from '../types';

interface JobCardProps {
  job: Job;
  onSaveToggle: (jobId: number, isSaved: boolean) => void;
  onApplicationChange: (jobId: number, status: string) => void;
  onShowMatchDetails?: (job: Job) => void;
}

export const JobCard: React.FC<JobCardProps> = ({
  job,
  onSaveToggle,
  onApplicationChange,
  onShowMatchDetails,
}) => {
  const [isSaved, setIsSaved] = useState(job.is_saved || false);
  const [appStatus, setAppStatus] = useState(job.application_status || 'none');

  const handleSaveClick = () => {
    const nextSaved = !isSaved;
    setIsSaved(nextSaved);
    onSaveToggle(job.id, isSaved);
  };

  const handleStatusChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value;
    setAppStatus(val);
    if (val !== 'none') {
      onApplicationChange(job.id, val);
    }
  };

  const getMatchScoreBadge = (score?: number) => {
    if (score === undefined || score === null) return null;
    let colorClass = 'bg-slate-800 text-slate-400 border-slate-700';
    if (score >= 80) colorClass = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
    else if (score >= 60) colorClass = 'bg-amber-500/10 text-amber-400 border-amber-500/30';
    else if (score > 0) colorClass = 'bg-sky-500/10 text-sky-400 border-sky-500/30';

    return (
      <button
        onClick={() => onShowMatchDetails?.(job)}
        className={`flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold border transition-transform hover:scale-105 ${colorClass}`}
        title="Click to view match explanation"
      >
        <Sparkles className="w-3.5 h-3.5" />
        <span>Match {score}%</span>
      </button>
    );
  };

  return (
    <div className="glass-card rounded-xl p-5 relative flex flex-col justify-between group">
      <div>
        {/* Header line */}
        <div className="flex items-start justify-between gap-4">
          <div>
            <span className="text-xs font-semibold uppercase tracking-wider text-cyan-400">
              {job.source_id === 1 ? 'RemoteOK' : 'Verified Source'}
            </span>
            <h3 className="text-lg font-bold text-white group-hover:text-cyan-300 transition-colors mt-0.5 line-clamp-1">
              {job.title}
            </h3>
            <div className="flex items-center space-x-3 text-sm text-slate-400 mt-1">
              <span className="flex items-center space-x-1 font-medium text-slate-300">
                <Building className="w-4 h-4 text-slate-500" />
                <span>{job.company}</span>
              </span>
              <span className="flex items-center space-x-1">
                <MapPin className="w-4 h-4 text-slate-500" />
                <span>{job.location}</span>
              </span>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {getMatchScoreBadge(job.match_score)}
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
          {(job.salary_min || job.salary_max) && (
            <span className="px-2.5 py-1 rounded-md text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center space-x-1">
              <DollarSign className="w-3 h-3" />
              <span>
                {job.salary_min ? `$${job.salary_min.toLocaleString()}` : ''}
                {job.salary_min && job.salary_max ? ' - ' : ''}
                {job.salary_max ? `$${job.salary_max.toLocaleString()}` : ''}
              </span>
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
          {/* Application Tracker Selector */}
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
          </select>

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
