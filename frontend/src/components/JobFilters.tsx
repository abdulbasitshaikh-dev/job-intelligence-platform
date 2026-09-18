import React from 'react';
import { Search, Filter, RefreshCw, X } from 'lucide-react';

interface JobFiltersProps {
  searchQuery: string;
  setSearchQuery: (q: string) => void;
  workMode: string;
  setWorkMode: (wm: string) => void;
  employmentType: string;
  setEmploymentType: (et: string) => void;
  onSearch: () => void;
  onReset: () => void;
}

export const JobFilters: React.FC<JobFiltersProps> = ({
  searchQuery,
  setSearchQuery,
  workMode,
  setWorkMode,
  employmentType,
  setEmploymentType,
  onSearch,
  onReset,
}) => {
  return (
    <div className="glass-panel rounded-2xl p-4 mb-6 space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
        {/* Search input */}
        <div className="relative md:col-span-2">
          <Search className="w-5 h-5 absolute left-3.5 top-3 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && onSearch()}
            placeholder="Search title, company, skills (e.g. Python, Remote, FastAPI)..."
            className="w-full bg-slate-900/90 text-sm text-slate-100 placeholder-slate-500 rounded-xl pl-11 pr-4 py-2.5 border border-slate-800 focus:outline-none focus:border-cyan-500 transition-all"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery('')}
              className="absolute right-3 top-3 text-slate-500 hover:text-slate-300"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Work Mode */}
        <div>
          <select
            value={workMode}
            onChange={(e) => setWorkMode(e.target.value)}
            className="w-full bg-slate-900/90 text-sm text-slate-200 border border-slate-800 rounded-xl px-3 py-2.5 focus:outline-none focus:border-cyan-500"
          >
            <option value="">All Work Modes</option>
            <option value="Remote">Remote</option>
            <option value="Hybrid">Hybrid</option>
            <option value="On-site">On-site</option>
          </select>
        </div>

        {/* Employment Type */}
        <div>
          <select
            value={employmentType}
            onChange={(e) => setEmploymentType(e.target.value)}
            className="w-full bg-slate-900/90 text-sm text-slate-200 border border-slate-800 rounded-xl px-3 py-2.5 focus:outline-none focus:border-cyan-500"
          >
            <option value="">All Employment Types</option>
            <option value="Full-time">Full-time</option>
            <option value="Part-time">Part-time</option>
            <option value="Contract">Contract</option>
            <option value="Internship">Internship</option>
          </select>
        </div>
      </div>

      <div className="flex items-center justify-between pt-2 border-t border-slate-800/60 text-xs">
        <span className="text-slate-400 font-medium">Filter opportunities by matching preferences</span>
        <div className="flex items-center space-x-2">
          <button
            onClick={onReset}
            className="flex items-center space-x-1 px-3 py-1.5 rounded-lg text-slate-400 hover:text-slate-200 hover:bg-slate-800 transition-all"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Reset</span>
          </button>
          <button
            onClick={onSearch}
            className="flex items-center space-x-1 px-4 py-1.5 rounded-lg font-semibold bg-cyan-600 hover:bg-cyan-500 text-white shadow-md shadow-cyan-600/20 transition-all"
          >
            <Filter className="w-3.5 h-3.5" />
            <span>Apply Filters</span>
          </button>
        </div>
      </div>
    </div>
  );
};
