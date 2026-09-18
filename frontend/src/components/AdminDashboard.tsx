import React, { useState, useEffect } from 'react';
import { Shield, Play, Activity, Database, CheckCircle, AlertTriangle, Clock } from 'lucide-react';
import { Source, ScraperRun, SystemStats } from '../types';
import { ApiClient } from '../lib/api';

export const AdminDashboard: React.FC = () => {
  const [sources, setSources] = useState<Source[]>([]);
  const [runs, setRuns] = useState<ScraperRun[]>([]);
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [srcRes, runsRes, statsRes] = await Promise.all([
        ApiClient.fetch<Source[]>('/admin/sources'),
        ApiClient.fetch<any>('/admin/scraper-runs?page_size=10'),
        ApiClient.fetch<SystemStats>('/admin/stats'),
      ]);
      setSources(srcRes);
      setRuns(runsRes.items || []);
      setStats(statsRes);
    } catch (err: any) {
      alert(err.message || 'Failed to fetch admin data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleToggleSource = async (sourceId: number, currentEnabled: boolean) => {
    try {
      await ApiClient.fetch(`/admin/sources/${sourceId}`, {
        method: 'PUT',
        body: JSON.stringify({ enabled: !currentEnabled }),
      });
      fetchData();
    } catch (err: any) {
      alert(err.message || 'Failed to toggle source');
    }
  };

  const handleTriggerScrape = async (sourceId: number, name: string) => {
    try {
      const res: any = await ApiClient.fetch(`/admin/sources/${sourceId}/scrape`, {
        method: 'POST',
      });
      alert(res.message || `Scrape task triggered for ${name}`);
      setTimeout(fetchData, 2000);
    } catch (err: any) {
      alert(err.message || 'Failed to trigger scrape task');
    }
  };

  if (loading) {
    return (
      <div className="py-12 text-center text-slate-400">
        <Activity className="w-8 h-8 animate-spin mx-auto mb-2 text-cyan-400" />
        <p className="text-sm font-medium">Loading administrative dashboard metrics...</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-white font-['Outfit'] flex items-center space-x-2">
          <Shield className="w-6 h-6 text-cyan-400" />
          <span>System Administration Portal</span>
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Monitor discovery engine health, trigger automated scrapers, inspect run telemetry
        </p>
      </div>

      {/* Stats Grid */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="glass-panel rounded-xl p-4 border border-slate-800">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Discovered Jobs</span>
            <div className="text-2xl font-extrabold text-white mt-1">{stats.total_jobs.toLocaleString()}</div>
          </div>
          <div className="glass-panel rounded-xl p-4 border border-slate-800">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Active Listings</span>
            <div className="text-2xl font-extrabold text-emerald-400 mt-1">{stats.active_jobs.toLocaleString()}</div>
          </div>
          <div className="glass-panel rounded-xl p-4 border border-slate-800">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Configured Sources</span>
            <div className="text-2xl font-extrabold text-sky-400 mt-1">{stats.total_sources}</div>
          </div>
          <div className="glass-panel rounded-xl p-4 border border-slate-800">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Scraper Runs</span>
            <div className="text-2xl font-extrabold text-purple-400 mt-1">{stats.total_scraper_runs}</div>
          </div>
        </div>
      )}

      {/* Source Management */}
      <div>
        <h3 className="text-lg font-bold text-slate-200 mb-4">Job Source Adapters</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {sources.map((src) => (
            <div key={src.id} className="glass-card rounded-xl p-5 flex flex-col justify-between">
              <div>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold uppercase tracking-wider text-cyan-400">{src.source_type}</span>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleToggleSource(src.id, src.enabled)}
                      className={`px-3 py-1 rounded-full text-xs font-bold border transition-colors ${
                        src.enabled
                          ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                          : 'bg-slate-800 text-slate-400 border-slate-700'
                      }`}
                    >
                      {src.enabled ? 'Enabled' : 'Disabled'}
                    </button>
                  </div>
                </div>

                <h4 className="text-lg font-bold text-white mt-2">{src.name}</h4>
                <p className="text-xs text-slate-400 truncate mt-0.5">{src.base_url}</p>

                <div className="mt-4 grid grid-cols-2 gap-2 text-xs text-slate-400 bg-slate-900/60 p-3 rounded-lg border border-slate-800">
                  <div>
                    <span className="block text-[10px] text-slate-500 uppercase font-semibold">Adapter</span>
                    <span className="font-mono text-slate-200">{src.scraper_type}</span>
                  </div>
                  <div>
                    <span className="block text-[10px] text-slate-500 uppercase font-semibold">Failures</span>
                    <span className={`font-bold ${src.consecutive_failures > 0 ? 'text-rose-400' : 'text-slate-300'}`}>
                      {src.consecutive_failures}
                    </span>
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between">
                <span className="text-xs text-slate-500 flex items-center space-x-1">
                  <Clock className="w-3.5 h-3.5" />
                  <span>
                    {src.last_run_at ? new Date(src.last_run_at).toLocaleTimeString() : 'Never run'}
                  </span>
                </span>
                <button
                  onClick={() => handleTriggerScrape(src.id, src.name)}
                  className="flex items-center space-x-1 px-3 py-1.5 rounded-lg text-xs font-semibold bg-cyan-600 hover:bg-cyan-500 text-white transition-all shadow-md shadow-cyan-600/20"
                >
                  <Play className="w-3.5 h-3.5 fill-white" />
                  <span>Trigger Scrape</span>
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Execution Telemetry Log Table */}
      <div>
        <h3 className="text-lg font-bold text-slate-200 mb-4">Recent Scraper Run Telemetry</h3>
        <div className="glass-panel rounded-2xl overflow-hidden border border-slate-800">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs text-slate-300">
              <thead className="bg-slate-900 text-slate-400 uppercase font-semibold border-b border-slate-800">
                <tr>
                  <th className="p-3">Run ID</th>
                  <th className="p-3">Source ID</th>
                  <th className="p-3">Status</th>
                  <th className="p-3">Jobs Found</th>
                  <th className="p-3">New Jobs</th>
                  <th className="p-3">Duplicates</th>
                  <th className="p-3">Duration</th>
                  <th className="p-3">Started At</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {runs.map((r) => (
                  <tr key={r.id} className="hover:bg-slate-900/50">
                    <td className="p-3 font-mono font-medium text-cyan-400">#{r.id}</td>
                    <td className="p-3 font-mono">Source-{r.source_id}</td>
                    <td className="p-3">
                      <span
                        className={`inline-flex items-center space-x-1 px-2 py-0.5 rounded text-[11px] font-bold uppercase ${
                          r.status === 'SUCCESS'
                            ? 'bg-emerald-500/10 text-emerald-400'
                            : r.status === 'FAILED'
                            ? 'bg-rose-500/10 text-rose-400'
                            : 'bg-sky-500/10 text-sky-400'
                        }`}
                      >
                        {r.status === 'SUCCESS' ? (
                          <CheckCircle className="w-3 h-3" />
                        ) : (
                          <AlertTriangle className="w-3 h-3" />
                        )}
                        <span>{r.status}</span>
                      </span>
                    </td>
                    <td className="p-3 font-semibold">{r.jobs_found}</td>
                    <td className="p-3 font-semibold text-emerald-400">+{r.jobs_created}</td>
                    <td className="p-3 text-slate-400">{r.duplicates_found}</td>
                    <td className="p-3 font-mono">{r.duration_seconds ? `${r.duration_seconds}s` : '-'}</td>
                    <td className="p-3 text-slate-400">{new Date(r.started_at).toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
