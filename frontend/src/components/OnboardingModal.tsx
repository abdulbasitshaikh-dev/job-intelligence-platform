import React, { useState } from 'react';
import { Sparkles, Plus, X, ArrowRight, DollarSign, MapPin, Briefcase, SlidersHorizontal } from 'lucide-react';
import { JobPreference } from '../types';
import { ApiClient } from '../lib/api';

interface OnboardingModalProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete: (preference: JobPreference) => void;
  onSkip: () => void;
}

const COMMON_SKILLS = ['Python', 'FastAPI', 'React', 'TypeScript', 'Node.js', 'PostgreSQL', 'Docker', 'AWS'];

export const OnboardingModal: React.FC<OnboardingModalProps> = ({
  isOpen,
  onClose,
  onComplete,
  onSkip,
}) => {
  const [keywords, setKeywords] = useState<string[]>([]);
  const [newKeyword, setNewKeyword] = useState('');
  const [locations, setLocations] = useState<string[]>([]);
  const [newLocation, setNewLocation] = useState('');
  const [workModes, setWorkModes] = useState<string[]>([]);
  const [employmentTypes, setEmploymentTypes] = useState<string[]>([]);
  const [minSalary, setMinSalary] = useState('');
  const [maxSalary, setMaxSalary] = useState('');
  const [currency, setCurrency] = useState('USD');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const addKeyword = (kw?: string) => {
    const val = (kw || newKeyword).trim();
    if (val && !keywords.some((k) => k.toLowerCase() === val.toLowerCase())) {
      setKeywords([...keywords, val]);
      if (!kw) setNewKeyword('');
    }
  };

  const removeKeyword = (kw: string) => {
    setKeywords(keywords.filter((k) => k !== kw));
  };

  const addLocation = () => {
    const val = newLocation.trim();
    if (val && !locations.some((l) => l.toLowerCase() === val.toLowerCase())) {
      setLocations([...locations, val]);
      setNewLocation('');
    }
  };

  const removeLocation = (loc: string) => {
    setLocations(locations.filter((l) => l !== loc));
  };

  const toggleWorkMode = (mode: string) => {
    if (workModes.includes(mode)) {
      setWorkModes(workModes.filter((m) => m !== mode));
    } else {
      setWorkModes([...workModes, mode]);
    }
  };

  const toggleEmploymentType = (type: string) => {
    if (employmentTypes.includes(type)) {
      setEmploymentTypes(employmentTypes.filter((t) => t !== type));
    } else {
      setEmploymentTypes([...employmentTypes, type]);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const payload = {
        keywords,
        locations,
        work_modes: workModes,
        employment_types: employmentTypes,
        min_salary: minSalary ? parseFloat(minSalary) : null,
        max_salary: maxSalary ? parseFloat(maxSalary) : null,
        currency,
      };

      const updated = await ApiClient.fetch<JobPreference>('/preferences', {
        method: 'PUT',
        body: JSON.stringify(payload),
      });

      onComplete(updated);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to save preferences');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-md animate-fade-in">
      <div className="glass-panel rounded-2xl w-full max-w-2xl p-6 sm:p-8 relative border border-slate-700 shadow-2xl max-h-[92vh] overflow-y-auto">
        <div className="flex items-start justify-between mb-6">
          <div className="flex items-center space-x-3">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-cyan-500 to-sky-400 flex items-center justify-center text-white shadow-lg shadow-cyan-500/30">
              <Sparkles className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-xl sm:text-2xl font-bold text-white font-['Outfit']">
                Personalize Your Opportunity Feed
              </h2>
              <p className="text-xs sm:text-sm text-slate-400 mt-0.5">
                Set your target skills, locations, and expectations to calculate authentic match scores.
              </p>
            </div>
          </div>
          <button
            onClick={onSkip}
            className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition-colors"
            title="Skip for now"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {error && (
          <div className="mb-5 p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Section 1: Keywords */}
          <div>
            <label className="text-xs font-semibold text-slate-200 uppercase tracking-wider flex items-center space-x-1.5 mb-2">
              <Briefcase className="w-3.5 h-3.5 text-cyan-400" />
              <span>Target Role &amp; Technical Skills</span>
            </label>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={newKeyword}
                onChange={(e) => setNewKeyword(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addKeyword();
                  }
                }}
                placeholder="e.g. Python, FastAPI, Backend, React, Docker..."
                className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-3.5 py-2 text-sm text-white focus:outline-none focus:border-cyan-500 transition-colors"
              />
              <button
                type="button"
                onClick={() => addKeyword()}
                className="px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-cyan-400 text-xs font-semibold flex items-center space-x-1 transition-colors"
              >
                <Plus className="w-4 h-4" />
                <span>Add</span>
              </button>
            </div>

            {/* Suggestions */}
            <div className="flex flex-wrap gap-1.5 mb-2">
              <span className="text-[11px] text-slate-500 self-center mr-1">Popular:</span>
              {COMMON_SKILLS.map((skill) => (
                <button
                  key={skill}
                  type="button"
                  onClick={() => addKeyword(skill)}
                  className={`text-[11px] px-2 py-0.5 rounded-lg border transition-all ${
                    keywords.includes(skill)
                      ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40'
                      : 'bg-slate-900/60 text-slate-400 border-slate-800 hover:text-slate-200 hover:border-slate-700'
                  }`}
                >
                  +{skill}
                </button>
              ))}
            </div>

            {keywords.length > 0 && (
              <div className="flex flex-wrap gap-1.5 p-2.5 rounded-xl bg-slate-900/60 border border-slate-800">
                {keywords.map((kw) => (
                  <span
                    key={kw}
                    className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-lg text-xs font-medium bg-cyan-500/10 text-cyan-300 border border-cyan-500/30"
                  >
                    <span>{kw}</span>
                    <button type="button" onClick={() => removeKeyword(kw)} className="hover:text-rose-400 ml-1">
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Section 2: Locations */}
          <div>
            <label className="text-xs font-semibold text-slate-200 uppercase tracking-wider flex items-center space-x-1.5 mb-2">
              <MapPin className="w-3.5 h-3.5 text-cyan-400" />
              <span>Target Geographic Locations</span>
            </label>
            <p className="text-[11px] text-slate-400 mb-2">
              Enter target cities or countries. Remote work mode is configured independently below.
            </p>
            <div className="flex gap-2 mb-2">
              <input
                type="text"
                value={newLocation}
                onChange={(e) => setNewLocation(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    e.preventDefault();
                    addLocation();
                  }
                }}
                placeholder="e.g. Pakistan, Germany, United States, London..."
                className="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-3.5 py-2 text-sm text-white focus:outline-none focus:border-cyan-500 transition-colors"
              />
              <button
                type="button"
                onClick={addLocation}
                className="px-3 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-cyan-400 text-xs font-semibold flex items-center space-x-1 transition-colors"
              >
                <Plus className="w-4 h-4" />
                <span>Add</span>
              </button>
            </div>
            {locations.length > 0 && (
              <div className="flex flex-wrap gap-1.5 p-2.5 rounded-xl bg-slate-900/60 border border-slate-800">
                {locations.map((loc) => (
                  <span
                    key={loc}
                    className="inline-flex items-center space-x-1 px-2.5 py-1 rounded-lg text-xs font-medium bg-emerald-500/10 text-emerald-300 border border-emerald-500/30"
                  >
                    <span>{loc}</span>
                    <button type="button" onClick={() => removeLocation(loc)} className="hover:text-rose-400 ml-1">
                      <X className="w-3 h-3" />
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Section 3: Work Mode & Employment Type */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-semibold text-slate-200 uppercase tracking-wider block mb-2">
                Work Mode
              </label>
              <div className="flex flex-wrap gap-2">
                {['Remote', 'Hybrid', 'On-site'].map((mode) => (
                  <button
                    key={mode}
                    type="button"
                    onClick={() => toggleWorkMode(mode)}
                    className={`px-3 py-1.5 rounded-xl text-xs font-semibold border transition-all ${
                      workModes.includes(mode)
                        ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40 shadow-sm'
                        : 'bg-slate-900/80 text-slate-400 border-slate-800 hover:text-white'
                    }`}
                  >
                    {mode}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="text-xs font-semibold text-slate-200 uppercase tracking-wider block mb-2">
                Employment Type
              </label>
              <div className="flex flex-wrap gap-2">
                {['Full-time', 'Part-time', 'Contract', 'Internship'].map((type) => (
                  <button
                    key={type}
                    type="button"
                    onClick={() => toggleEmploymentType(type)}
                    className={`px-3 py-1.5 rounded-xl text-xs font-semibold border transition-all ${
                      employmentTypes.includes(type)
                        ? 'bg-sky-500/20 text-sky-300 border-sky-500/40 shadow-sm'
                        : 'bg-slate-900/80 text-slate-400 border-slate-800 hover:text-white'
                    }`}
                  >
                    {type}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Section 4: Target Compensation */}
          <div>
            <label className="text-xs font-semibold text-slate-200 uppercase tracking-wider flex items-center space-x-1.5 mb-2">
              <DollarSign className="w-3.5 h-3.5 text-cyan-400" />
              <span>Target Annual Compensation (Optional)</span>
            </label>
            <div className="grid grid-cols-3 gap-3">
              <div>
                <select
                  value={currency}
                  onChange={(e) => setCurrency(e.target.value)}
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-cyan-500"
                >
                  <option value="USD">USD ($)</option>
                  <option value="EUR">EUR (€)</option>
                  <option value="GBP">GBP (£)</option>
                  <option value="CAD">CAD ($)</option>
                  <option value="PKR">PKR (Rs)</option>
                  <option value="INR">INR (₹)</option>
                </select>
              </div>
              <div>
                <input
                  type="number"
                  min="0"
                  step="1000"
                  value={minSalary}
                  onChange={(e) => setMinSalary(e.target.value)}
                  placeholder="Min (e.g. 60000)"
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-500"
                />
              </div>
              <div>
                <input
                  type="number"
                  min="0"
                  step="1000"
                  value={maxSalary}
                  onChange={(e) => setMaxSalary(e.target.value)}
                  placeholder="Max (e.g. 120000)"
                  className="w-full bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-sm text-white focus:outline-none focus:border-cyan-500"
                />
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="pt-4 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-3">
            <button
              type="button"
              onClick={onSkip}
              className="text-xs text-slate-400 hover:text-slate-200 py-2 px-3 transition-colors"
            >
              Skip for now (Browse unpersonalized feed)
            </button>
            <button
              type="submit"
              disabled={loading}
              className="w-full sm:w-auto px-6 py-2.5 rounded-xl font-semibold bg-gradient-to-r from-cyan-600 to-sky-500 hover:from-cyan-500 hover:to-sky-400 text-white shadow-lg shadow-cyan-600/25 transition-all text-sm flex items-center justify-center space-x-2 disabled:opacity-50"
            >
              <span>{loading ? 'Saving...' : 'Save & Personalize Feed'}</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
