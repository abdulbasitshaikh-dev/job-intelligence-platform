import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { JobCard } from './components/JobCard';
import { JobFilters } from './components/JobFilters';
import { MatchScoreModal } from './components/MatchScoreModal';
import { AuthModal } from './components/AuthModal';
import { HowItWorksModal } from './components/HowItWorksModal';
import { SourcesModal } from './components/SourcesModal';
import { ApplicationsBoard } from './components/ApplicationsBoard';
import { PreferencesForm } from './components/PreferencesForm';
import { AdminDashboard } from './components/AdminDashboard';
import { OnboardingModal } from './components/OnboardingModal';
import { ApiClient } from './lib/api';
import { Job, JobApplication, JobPreference, PaginatedResponse, PlatformStats, User } from './types';
import { Sparkles, Briefcase, ChevronLeft, ChevronRight, Bookmark, RefreshCw, Database, Globe } from 'lucide-react';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState('feed');
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [isAuthOpen, setIsAuthOpen] = useState(false);
  const [isHowItWorksOpen, setIsHowItWorksOpen] = useState(false);
  const [isSourcesOpen, setIsSourcesOpen] = useState(false);
  const [isOnboardingOpen, setIsOnboardingOpen] = useState(false);
  const [onboardingDismissed, setOnboardingDismissed] = useState(false);

  // Platform Telemetry
  const [platformStats, setPlatformStats] = useState<PlatformStats | null>(null);

  // Job feed state
  const [jobs, setJobs] = useState<Job[]>([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalJobs, setTotalJobs] = useState(0);
  const [loading, setLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [syncMessage, setSyncMessage] = useState<string | null>(null);

  // Filter state
  const [searchQuery, setSearchQuery] = useState('');
  const [workMode, setWorkMode] = useState('');
  const [employmentType, setEmploymentType] = useState('');

  // Modals & Tab state data
  const [selectedJobMatch, setSelectedJobMatch] = useState<Job | null>(null);
  const [savedJobs, setSavedJobs] = useState<Job[]>([]);
  const [applications, setApplications] = useState<JobApplication[]>([]);
  const [preference, setPreference] = useState<JobPreference | null>(null);

  // Fetch Current User & Platform Stats on Mount
  useEffect(() => {
    if (ApiClient.isAuthenticated()) {
      ApiClient.fetch<User>('/auth/me')
        .then((user) => setCurrentUser(user))
        .catch(() => ApiClient.clearTokens());
    }

    ApiClient.fetch<PlatformStats>('/stats')
      .then((data) => setPlatformStats(data))
      .catch((err) => console.warn('Could not load platform stats', err));
  }, []);

  // Check preferences and trigger onboarding if not configured
  useEffect(() => {
    if (currentUser) {
      ApiClient.fetch<JobPreference>('/preferences')
        .then((pref) => {
          setPreference(pref);
          if (!pref.is_configured && !onboardingDismissed) {
            setIsOnboardingOpen(true);
          }
        })
        .catch((err) => console.warn('Could not load preferences', err));
    }
  }, [currentUser, onboardingDismissed]);

  // Fetch Jobs Feed
  const fetchJobs = async () => {
    setLoading(true);
    try {
      let endpoint = `/jobs?page=${page}&page_size=12`;
      if (searchQuery) endpoint = `/jobs/search?q=${encodeURIComponent(searchQuery)}&page=${page}&page_size=12`;
      if (workMode) endpoint += `&work_mode=${workMode}`;
      if (employmentType) endpoint += `&employment_type=${employmentType}`;

      const data = await ApiClient.fetch<PaginatedResponse<Job>>(endpoint);
      setJobs(data.items);
      setTotalPages(data.pages);
      setTotalJobs(data.total);
    } catch (err: any) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // Fetch Tab Specific Data
  const fetchTabData = async () => {
    if (!currentUser) return;
    try {
      if (activeTab === 'saved') {
        const data = await ApiClient.fetch<Job[]>('/jobs/saved/me');
        setSavedJobs(data);
      } else if (activeTab === 'applications') {
        const data = await ApiClient.fetch<JobApplication[]>('/applications');
        setApplications(data);
      } else if (activeTab === 'preferences') {
        const data = await ApiClient.fetch<JobPreference>('/preferences');
        setPreference(data);
      }
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    if (activeTab === 'feed') {
      fetchJobs();
    } else {
      fetchTabData();
    }
  }, [activeTab, page, searchQuery, workMode, employmentType, currentUser]);

  const handleSaveToggle = async (jobId: number, currentlySaved: boolean) => {
    if (!currentUser) {
      setIsAuthOpen(true);
      return;
    }
    try {
      if (currentlySaved) {
        await ApiClient.fetch(`/jobs/${jobId}/save`, { method: 'DELETE' });
      } else {
        await ApiClient.fetch(`/jobs/${jobId}/save`, { method: 'POST' });
      }
      if (activeTab === 'saved') fetchTabData();
    } catch (err: any) {
      alert(err.message || 'Failed to update saved job');
    }
  };

  const handleApplicationChange = async (jobId: number, statusVal: string) => {
    if (!currentUser) {
      setIsAuthOpen(true);
      return;
    }
    try {
      await ApiClient.fetch('/applications', {
        method: 'POST',
        body: JSON.stringify({ job_id: jobId, status: statusVal }),
      });
    } catch {
      // If application already exists, patch status
      const existing = applications.find((a) => a.job_id === jobId);
      if (existing) {
        await ApiClient.fetch(`/applications/${existing.id}`, {
          method: 'PATCH',
          body: JSON.stringify({ status: statusVal }),
        });
      }
    }
  };

  const handleAdminSync = async () => {
    setSyncing(true);
    setSyncMessage(null);
    try {
      const result: any = await ApiClient.fetch('/jobs/sync', { method: 'POST' });
      setSyncMessage(`✓ Synced ${result.sources?.length ?? 0} sources — ${result.new_jobs} new jobs added`);
      setPage(1);
      fetchJobs();
      ApiClient.fetch<PlatformStats>('/stats').then(setPlatformStats).catch(() => {});
    } catch (err: any) {
      setSyncMessage('✗ Sync failed: ' + (err.message || 'Unknown error'));
    } finally {
      setSyncing(false);
      setTimeout(() => setSyncMessage(null), 8000);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 flex flex-col font-['Plus_Jakarta_Sans',sans-serif]">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        currentUser={currentUser}
        onLogout={() => {
          ApiClient.clearTokens();
          setCurrentUser(null);
          setPreference(null);
          setOnboardingDismissed(false);
          setActiveTab('feed');
        }}
        onOpenAuth={() => setIsAuthOpen(true)}
        onOpenHowItWorks={() => setIsHowItWorksOpen(true)}
        onOpenSources={() => setIsSourcesOpen(true)}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Banner Hero */}
        <div className="relative rounded-3xl overflow-hidden p-8 mb-8 bg-gradient-to-r from-cyan-950/60 via-slate-900 to-sky-950/60 border border-slate-800/80 shadow-2xl">
          <div className="relative z-10 max-w-3xl">
            <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 mb-3">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
              <span>
                {platformStats
                  ? `${platformStats.active_jobs} Active Jobs • ${platformStats.configured_sources} Configured Sources • RemoteOK & Arbeitnow`
                  : `${totalJobs || 'Hundreds of'} Active Opportunities • Live Ingestion`}
              </span>
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight font-['Outfit']">
              Find Jobs That Actually Match You
            </h1>
            <p className="text-sm text-slate-300 mt-2 leading-relaxed">
              Discover opportunities collected from public job sources, then personalize your results using your skills, location, work preferences and salary expectations.
            </p>
          </div>
        </div>

        {/* Tab 1: Job Feed */}
        {activeTab === 'feed' && (
          <div>
            <JobFilters
              searchQuery={searchQuery}
              setSearchQuery={setSearchQuery}
              workMode={workMode}
              setWorkMode={setWorkMode}
              employmentType={employmentType}
              setEmploymentType={setEmploymentType}
              onSearch={() => {
                setPage(1);
                fetchJobs();
              }}
              onReset={() => {
                setSearchQuery('');
                setWorkMode('');
                setEmploymentType('');
                setPage(1);
              }}
            />

            {/* Live Status Bar */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
              <div className="flex items-center gap-3 text-sm text-slate-400">
                <span className="flex items-center gap-1.5">
                  <Database className="w-3.5 h-3.5 text-cyan-500" />
                  <span><span className="text-white font-semibold">{totalJobs}</span> active opportunities</span>
                </span>
                <span className="text-slate-700">|</span>
                <span className="flex items-center gap-1.5">
                  <Globe className="w-3.5 h-3.5 text-emerald-500" />
                  <span className="text-emerald-400 font-medium text-xs">
                    {platformStats?.healthy_sources ?? 2} Healthy Sources
                  </span>
                </span>
              </div>

              <div className="flex items-center gap-2">
                {syncMessage && (
                  <span className={`text-xs px-2.5 py-1 rounded-lg ${syncMessage.startsWith('✓') ? 'text-emerald-400 bg-emerald-500/10 border border-emerald-500/20' : 'text-rose-400 bg-rose-500/10 border border-rose-500/20'}`}>
                    {syncMessage}
                  </span>
                )}
                {currentUser?.is_superuser ? (
                  <button
                    onClick={handleAdminSync}
                    disabled={syncing}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-cyan-500/10 text-cyan-400 hover:bg-cyan-500/20 border border-cyan-500/30 text-xs font-semibold transition-all disabled:opacity-50"
                  >
                    <RefreshCw className={`w-3.5 h-3.5 ${syncing ? 'animate-spin' : ''}`} />
                    {syncing ? 'Syncing...' : 'Sync Live Sources'}
                  </button>
                ) : (
                  <button
                    onClick={() => {
                      fetchJobs();
                      ApiClient.fetch<PlatformStats>('/stats').then(setPlatformStats).catch(() => {});
                    }}
                    disabled={loading}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 hover:text-white border border-slate-700 text-xs font-semibold transition-all disabled:opacity-50"
                  >
                    <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
                    <span>Refresh Listings</span>
                  </button>
                )}
              </div>
            </div>

            {loading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {[1, 2, 3, 4, 5, 6].map((i) => (
                  <div key={i} className="glass-panel rounded-xl h-64 animate-pulse p-5" />
                ))}
              </div>
            ) : jobs.length === 0 ? (
              <div className="glass-panel rounded-2xl p-12 text-center">
                <Briefcase className="w-12 h-12 text-slate-600 mx-auto mb-3" />
                <h3 className="text-lg font-semibold text-slate-300">No matching jobs found</h3>
                <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1">
                  Try adjusting your search query or filter settings above to discover available opportunities.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                {jobs.map((job) => (
                  <JobCard
                    key={job.id}
                    job={job}
                    currentUser={currentUser}
                    onSaveToggle={handleSaveToggle}
                    onApplicationChange={handleApplicationChange}
                    onShowMatchDetails={(j) => {
                      if (!preference?.is_configured) {
                        setIsOnboardingOpen(true);
                      } else {
                        setSelectedJobMatch(j);
                      }
                    }}
                    onRequireAuth={() => setIsAuthOpen(true)}
                  />
                ))}
              </div>
            )}

            {/* Pagination Controls */}
            {totalPages > 1 && (
              <div className="flex items-center justify-center space-x-3 mt-8">
                <button
                  disabled={page === 1}
                  onClick={() => setPage(page - 1)}
                  className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 disabled:opacity-40 hover:bg-slate-800"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
                <span className="text-xs font-semibold text-slate-400">
                  Page {page} of {totalPages}
                </span>
                <button
                  disabled={page === totalPages}
                  onClick={() => setPage(page + 1)}
                  className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-300 disabled:opacity-40 hover:bg-slate-800"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            )}
          </div>
        )}

        {/* Tab 2: Saved Jobs */}
        {activeTab === 'saved' && (
          <div>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-white font-['Outfit']">Saved Opportunities</h2>
              <span className="px-3 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/30">
                {savedJobs.length} Bookmarked
              </span>
            </div>

            {savedJobs.length === 0 ? (
              <div className="glass-panel rounded-2xl p-12 text-center">
                <Bookmark className="w-12 h-12 text-slate-600 mx-auto mb-3" />
                <h3 className="text-lg font-semibold text-slate-300">No saved jobs yet</h3>
                <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1">
                  Click the bookmark icon on any job card in the feed to save jobs for later review.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                {savedJobs.map((job) => (
                  <JobCard
                    key={job.id}
                    job={job}
                    currentUser={currentUser}
                    onSaveToggle={handleSaveToggle}
                    onApplicationChange={handleApplicationChange}
                    onShowMatchDetails={(j) => {
                      if (!preference?.is_configured) {
                        setIsOnboardingOpen(true);
                      } else {
                        setSelectedJobMatch(j);
                      }
                    }}
                    onRequireAuth={() => setIsAuthOpen(true)}
                  />
                ))}
              </div>
            )}
          </div>
        )}

        {/* Tab 3: Applications Tracker */}
        {activeTab === 'applications' && (
          <ApplicationsBoard applications={applications} onRefresh={fetchTabData} />
        )}

        {/* Tab 4: Preferences */}
        {activeTab === 'preferences' && (
          <PreferencesForm preference={preference} onRefresh={fetchTabData} />
        )}

        {/* Tab 5: Admin Dashboard */}
        {activeTab === 'admin' && currentUser?.is_superuser && <AdminDashboard />}
      </main>

      <MatchScoreModal job={selectedJobMatch} onClose={() => setSelectedJobMatch(null)} />
      <OnboardingModal
        isOpen={isOnboardingOpen}
        onClose={() => setIsOnboardingOpen(false)}
        onComplete={(newPref) => {
          setPreference(newPref);
          setIsOnboardingOpen(false);
          fetchJobs();
        }}
        onSkip={() => {
          setIsOnboardingOpen(false);
          setOnboardingDismissed(true);
        }}
      />
      <AuthModal isOpen={isAuthOpen} onClose={() => setIsAuthOpen(false)} onAuthSuccess={(user) => setCurrentUser(user)} />
      <HowItWorksModal isOpen={isHowItWorksOpen} onClose={() => setIsHowItWorksOpen(false)} />
      <SourcesModal isOpen={isSourcesOpen} onClose={() => setIsSourcesOpen(false)} />

      <footer className="border-t border-slate-800/80 py-6 text-center text-xs text-slate-500 mt-12">
        <p>Job Intelligence Platform &copy; 2026. Built with FastAPI, SQLAlchemy 2.x, Celery, Playwright &amp; React.</p>
      </footer>
    </div>
  );
};
