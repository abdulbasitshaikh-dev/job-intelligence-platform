import React, { useState, useEffect } from 'react';
import { Sliders, Plus, X, Save, Check, Bell, Globe } from 'lucide-react';
import { JobPreference, NotificationConfig } from '../types';
import { ApiClient } from '../lib/api';

interface PreferencesFormProps {
  preference: JobPreference | null;
  onRefresh: () => void;
}

export const PreferencesForm: React.FC<PreferencesFormProps> = ({ preference, onRefresh }) => {
  const [keywords, setKeywords] = useState<string[]>(preference?.keywords || []);
  const [newKeyword, setNewKeyword] = useState('');
  const [locations, setLocations] = useState<string[]>(preference?.locations || []);
  const [newLocation, setNewLocation] = useState('');
  const [workModes, setWorkModes] = useState<string[]>(preference?.work_modes || ['Remote']);
  const [employmentTypes, setEmploymentTypes] = useState<string[]>(preference?.employment_types || ['Full-time']);
  const [minSalary, setMinSalary] = useState<string>(preference?.min_salary ? String(preference.min_salary) : '');
  const [maxSalary, setMaxSalary] = useState<string>(preference?.max_salary ? String(preference.max_salary) : '');

  // Notification Config state
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [minMatchScore, setMinMatchScore] = useState(60);
  const [webhookUrl, setWebhookUrl] = useState('');

  const [savedSuccess, setSavedSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (preference) {
      setKeywords(preference.keywords || []);
      setLocations(preference.locations || []);
      setWorkModes(preference.work_modes || ['Remote']);
      setEmploymentTypes(preference.employment_types || ['Full-time']);
      setMinSalary(preference.min_salary ? String(preference.min_salary) : '');
      setMaxSalary(preference.max_salary ? String(preference.max_salary) : '');
    }

    // Fetch persisted notification settings
    ApiClient.fetch<NotificationConfig>('/preferences/notifications')
      .then((cfg) => {
        setEmailNotifications(cfg.email_notifications);
        setMinMatchScore(cfg.min_match_score || 60);
        setWebhookUrl(cfg.webhook_url || '');
      })
      .catch(() => {});
  }, [preference]);

  const addKeyword = () => {
    if (newKeyword.trim() && !keywords.includes(newKeyword.trim())) {
      setKeywords([...keywords, newKeyword.trim()]);
      setNewKeyword('');
    }
  };

  const removeKeyword = (kw: string) => {
    setKeywords(keywords.filter((k) => k !== kw));
  };

  const addLocation = () => {
    if (newLocation.trim() && !locations.includes(newLocation.trim())) {
      setLocations([...locations, newLocation.trim()]);
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
    setSavedSuccess(false);

    try {
      await Promise.all([
        ApiClient.fetch('/preferences', {
          method: 'PUT',
          body: JSON.stringify({
            keywords,
            locations,
            work_modes: workModes,
            employment_types: employmentTypes,
            min_salary: minSalary ? parseFloat(minSalary) : null,
            max_salary: maxSalary ? parseFloat(maxSalary) : null,
          }),
        }),
        ApiClient.fetch('/preferences/notifications', {
          method: 'PUT',
          body: JSON.stringify({
            email_notifications: emailNotifications,
            min_match_score: minMatchScore,
            webhook_url: webhookUrl.trim() || null,
          }),
        }),
      ]);

      setSavedSuccess(true);
      onRefresh();
      setTimeout(() => setSavedSuccess(false), 3500);
    } catch (err: any) {
      alert(err.message || 'Failed to save preferences');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white font-['Outfit'] flex items-center space-x-2">
            <Sliders className="w-6 h-6 text-cyan-400" />
            <span>Job Preference &amp; Match Engine</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Configure your targeting parameters and automated match notification thresholds
          </p>
        </div>
        {savedSuccess && (
          <span className="flex items-center space-x-1.5 text-xs font-bold text-emerald-400 bg-emerald-500/10 px-3.5 py-1.5 rounded-lg border border-emerald-500/30">
            <Check className="w-4 h-4" />
            <span>Preferences &amp; Notifications Saved!</span>
          </span>
        )}
      </div>

      <form onSubmit={handleSubmit} className="glass-panel rounded-2xl p-6 space-y-6">
        {/* Keywords */}
        <div>
          <label className="block text-sm font-semibold text-slate-200 mb-2">
            Target Keywords &amp; Tech Stack
          </label>
          <div className="flex items-center space-x-2 mb-3">
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
              placeholder="Add keyword (e.g. Python, FastAPI, Remote, Backend)..."
              className="flex-1 bg-slate-900 text-sm text-slate-100 placeholder-slate-500 rounded-xl px-4 py-2.5 border border-slate-800 focus:outline-none focus:border-cyan-500"
            />
            <button
              type="button"
              onClick={addKeyword}
              className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-cyan-400 font-semibold text-sm flex items-center space-x-1"
            >
              <Plus className="w-4 h-4" />
              <span>Add</span>
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {keywords.map((kw) => (
              <span
                key={kw}
                className="flex items-center space-x-1.5 px-3 py-1 rounded-lg text-xs font-semibold bg-cyan-500/10 text-cyan-300 border border-cyan-500/30"
              >
                <span>{kw}</span>
                <button type="button" onClick={() => removeKeyword(kw)} className="hover:text-rose-400">
                  <X className="w-3.5 h-3.5" />
                </button>
              </span>
            ))}
          </div>
        </div>

        {/* Locations */}
        <div className="pt-4 border-t border-slate-800/80">
          <label className="block text-sm font-semibold text-slate-200 mb-2">
            Preferred Target Locations
          </label>
          <div className="flex items-center space-x-2 mb-3">
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
              placeholder="Add location (e.g. Pakistan, Karachi, Remote)..."
              className="flex-1 bg-slate-900 text-sm text-slate-100 placeholder-slate-500 rounded-xl px-4 py-2.5 border border-slate-800 focus:outline-none focus:border-cyan-500"
            />
            <button
              type="button"
              onClick={addLocation}
              className="px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-cyan-400 font-semibold text-sm flex items-center space-x-1"
            >
              <Plus className="w-4 h-4" />
              <span>Add</span>
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {locations.map((loc) => (
              <span
                key={loc}
                className="flex items-center space-x-1.5 px-3 py-1 rounded-lg text-xs font-semibold bg-sky-500/10 text-sky-300 border border-sky-500/30"
              >
                <span>{loc}</span>
                <button type="button" onClick={() => removeLocation(loc)} className="hover:text-rose-400">
                  <X className="w-3.5 h-3.5" />
                </button>
              </span>
            ))}
          </div>
        </div>

        {/* Work Modes & Employment Types */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4 border-t border-slate-800/80">
          <div>
            <label className="block text-sm font-semibold text-slate-200 mb-3">Work Mode Preferences</label>
            <div className="flex flex-wrap gap-2">
              {['Remote', 'Hybrid', 'On-site'].map((mode) => {
                const isSelected = workModes.includes(mode);
                return (
                  <button
                    key={mode}
                    type="button"
                    onClick={() => toggleWorkMode(mode)}
                    className={`px-4 py-2 rounded-xl text-xs font-semibold border transition-all ${
                      isSelected
                        ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/50 shadow-md shadow-cyan-500/10'
                        : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-slate-200'
                    }`}
                  >
                    {mode}
                  </button>
                );
              })}
            </div>
          </div>

          <div>
            <label className="block text-sm font-semibold text-slate-200 mb-3">Employment Type</label>
            <div className="flex flex-wrap gap-2">
              {['Full-time', 'Part-time', 'Contract', 'Internship'].map((type) => {
                const isSelected = employmentTypes.includes(type);
                return (
                  <button
                    key={type}
                    type="button"
                    onClick={() => toggleEmploymentType(type)}
                    className={`px-4 py-2 rounded-xl text-xs font-semibold border transition-all ${
                      isSelected
                        ? 'bg-sky-500/20 text-sky-300 border-sky-500/50 shadow-md shadow-sky-500/10'
                        : 'bg-slate-900 text-slate-400 border-slate-800 hover:text-slate-200'
                    }`}
                  >
                    {type}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Salary Range */}
        <div className="pt-4 border-t border-slate-800/80">
          <label className="block text-sm font-semibold text-slate-200 mb-3">Expected Target Salary Range (USD)</label>
          <div className="grid grid-cols-2 gap-4">
            <input
              type="number"
              value={minSalary}
              onChange={(e) => setMinSalary(e.target.value)}
              placeholder="Minimum (e.g. 50000)"
              className="w-full bg-slate-900 text-sm text-slate-100 placeholder-slate-500 rounded-xl px-4 py-2.5 border border-slate-800 focus:outline-none focus:border-cyan-500"
            />
            <input
              type="number"
              value={maxSalary}
              onChange={(e) => setMaxSalary(e.target.value)}
              placeholder="Maximum (e.g. 120000)"
              className="w-full bg-slate-900 text-sm text-slate-100 placeholder-slate-500 rounded-xl px-4 py-2.5 border border-slate-800 focus:outline-none focus:border-cyan-500"
            />
          </div>
        </div>

        {/* Notification Settings Section */}
        <div className="pt-4 border-t border-slate-800/80 space-y-4">
          <div className="flex items-center space-x-2">
            <Bell className="w-5 h-5 text-cyan-400" />
            <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider">
              Notification &amp; Automation Channels
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between">
              <div>
                <span className="text-xs font-semibold text-white block">Email Match Alerts</span>
                <span className="text-[11px] text-slate-400">Receive periodic digests of matching opportunities</span>
              </div>
              <input
                type="checkbox"
                checked={emailNotifications}
                onChange={(e) => setEmailNotifications(e.target.checked)}
                className="w-5 h-5 accent-cyan-500 rounded cursor-pointer"
              />
            </div>

            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-white">Minimum Match Threshold</span>
                <span className="text-xs font-bold text-cyan-400">{minMatchScore}%</span>
              </div>
              <input
                type="range"
                min={10}
                max={95}
                step={5}
                value={minMatchScore}
                onChange={(e) => setMinMatchScore(parseInt(e.target.value))}
                className="w-full accent-cyan-500 cursor-pointer"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
              External Webhook URL (n8n / Slack / Automation Integration)
            </label>
            <div className="relative">
              <Globe className="w-4 h-4 absolute left-3 top-3 text-slate-500" />
              <input
                type="url"
                value={webhookUrl}
                onChange={(e) => setWebhookUrl(e.target.value)}
                placeholder="https://n8n.yourdomain.com/webhook/job-events"
                className="w-full bg-slate-900 text-xs text-slate-100 placeholder-slate-500 rounded-xl pl-10 pr-4 py-2.5 border border-slate-800 focus:outline-none focus:border-cyan-500"
              />
            </div>
            <p className="text-[11px] text-slate-500 mt-1">
              Structured JSON payloads will be dispatched when newly ingested jobs meet your minimum match score.
            </p>
          </div>
        </div>

        <div className="pt-4 flex justify-end">
          <button
            type="submit"
            disabled={loading}
            className="flex items-center space-x-2 px-6 py-3 rounded-xl font-bold bg-gradient-to-r from-cyan-600 to-sky-500 hover:from-cyan-500 hover:to-sky-400 text-white shadow-lg shadow-cyan-500/25 transition-all text-sm"
          >
            <Save className="w-4 h-4" />
            <span>{loading ? 'Saving Settings...' : 'Save Preferences & Notifications'}</span>
          </button>
        </div>
      </form>
    </div>
  );
};

