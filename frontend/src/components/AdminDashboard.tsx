import React, { useState, useEffect } from 'react';
import { Shield, Play, Activity, Database, CheckCircle, AlertTriangle, Clock, RefreshCw, Server, Zap, CheckCircle2 } from 'lucide-react';
import { Source, ScraperRun, SystemStats, SystemHealth } from '../types';
import { ApiClient } from '../lib/api';

export const AdminDashboard: React.FC = () => {
  const [sources, setSources] = useState<Source[]>([]);
  const [runs, setRuns] = useState<ScraperRun[]>([]);
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [syncingAll, setSyncingAll] = useState(false);
  const [actionNotice, setActionNotice] = useState<string | null>(null);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [srcRes, runsRes, statsRes, healthRes] = await Promise.all([
        ApiClient.fetch<Source[]>('/admin/sources'),
        ApiClient.fetch<any>('/admin/scraper-runs?page_size=10'),
        ApiClient.fetch<SystemStats>('/admin/stats'),
        ApiClient.fetch<SystemHealth>('/admin/health').catch(() => null),
      ]);
      setSources(srcRes);
      setRuns(runsRes.items || []);
      setStats(statsRes);
      if (healthRes) setHealth(healthRes);
    } catch (err: any) {
      setActionNotice('Failed to fetch admin data: ' + (err.message || 'Unknown error'));
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
      setActionNotice(res.message || `Scrape task triggered for ${name}`);
      setTimeout(fetchData, 2000);
      setTimeout(() => setActionNotice(null), 6000);
    } catch (err: any) {
      alert(err.message || 'Failed to trigger scrape task');
    }
  };

  const handleTriggerSyncAll = async () => {
    setSyncingAll(true);
    setActionNotice(null);
    try {
      const res: any = await ApiClient.fetch('/admin/sync-all', { method: 'POST' });
      setActionNotice(`✓ ${res.message || 'Scrape queued for all active sources'}`);
      setTimeout(fetchData, 3000);
    } catch (err: any) {
      setActionNotice(`✗ Sync failed: ${err.message || 'Unknown error'}`);
    } finally {
      setSyncingAll(false);
      setTimeout(() => setActionNotice(null), 8000);
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
      {/* Header & Global Sync Button */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-white font-['Outfit'] flex items-center space-x-2">
            <Shield className="w-6 h-6 text-cyan-400" />
            <span>System Administration Portal</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Monitor pipeline health, trigger scrapers, and inspect run telemetry
          </p>
        </div>

        <div className="flex items-center space-x-3">
          {actionNotice && (
            <span
              className={`text-xs px-3 py-1.5 rounded-lg border font-medium ${
                actionNotice.startsWith('✓')
                  ? 'text-emerald-400 bg-emerald-500/10 border-emerald-500/30'
                  : 'text-rose-400 bg-rose-500/10 border-rose-500/30'
              }`}
            >
              {actionNotice}
            </span>
          )}
          <button
            onClick={handleTriggerSyncAll}
            disabled={syncingAll}
            className="flex items-center space-x-2 px-4 py-2 rounded-xl text-xs font-semibold bg-cyan-600 hover:bg-cyan-500 text-white transition-all shadow-lg shadow-cyan-600/20 disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${syncingAll ? 'animate-spin' : ''}`} />
            <span>{syncingAll ? 'Triggering Sync...' : 'Trigger Sync All Sources'}</span>
          </button>
        </div>
      </div>

      {/* Services Health */}
      {health && (
        <div className="glass-panel rounded-2xl p-5 border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-bold text-slate-200 uppercase tracking-wider flex items-center space-x-2">
              <Server className="w-4 h-4 text-cyan-400" />
              <span>Platform Infrastructure &amp; Health</span>
            </h3>
            <span
              className={`inline-flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold ${
                health.status === 'operational'
                  ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30'
                  : 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
              }`}
            >
              <span className={`w-1.5 h-1.5 rounded-full ${health.status === 'operational' ? 'bg-emerald-400' : 'bg-amber-400'} animate-pulse`} />
              <span className="capitalize">{health.status}</span>
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
              <span className="text-[10px] uppercase font-semibold text-slate-500">PostgreSQL DB</span>
              <div className="mt-1 flex items-center space-x-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span className="text-xs font-semibold text-white capitalize">{health.components.database.status}</span>
              </div>
            </div>

            <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
              <span className="text-[10px] uppercase font-semibold text-slate-500">Redis Broker</span>
              <div className="mt-1 flex items-center space-x-1.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
                <span className="text-xs font-semibold text-white capitalize">{health.components.redis.status}</span>
              </div>
            </div>

            <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
              <span className="text-[10px] uppercase font-semibold text-slate-500">Celery Worker</span>
              <div className="mt-1 flex items-center space-x-1.5">
                <Zap className="w-3.5 h-3.5 text-cyan-400" />
                <span className="text-xs font-semibold text-white capitalize">{health.components.celery.status}</span>
              </div>
            </div>

            <div className="bg-slate-950/60 p-3 rounded-xl border border-slate-800/80">
              <span className="text-[10px] uppercase font-semibold text-slate-500">Beat Scheduler</span>
              <div className="mt-1 flex items-center space-x-1.5">
                <Clock className="w-3.5 h-3.5 text-purple-400" />
                <span className="text-xs font-semibold text-white">{health.components.scheduler.schedule}</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Stats Grid */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="glass-panel rounded-xl p-4 border border-slate-800">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Discovered</span>
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
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Successful Runs</span>
            <div className="text-2xl font-extrabold text-emerald-400 mt-1">{stats.successful_runs ?? stats.total_scraper_runs}</div>
          </div>
          <div className="glass-panel rounded-xl p-4 border border-slate-800">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Failed Runs</span>
            <div className={`text-2xl font-extrabold mt-1 ${(stats.failed_runs || 0) > 0 ? 'text-rose-400' : 'text-slate-400'}`}>
              {stats.failed_runs ?? 0}
            </div>
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
              <tbody className="divide-y border-slate-800/60">
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
