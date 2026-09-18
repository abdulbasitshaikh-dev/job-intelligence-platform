import React, { useState } from 'react';
import { Briefcase, Bookmark, CheckSquare, Sliders, Shield, LogOut, User as UserIcon, Sparkles, HelpCircle, Globe2, Menu, X } from 'lucide-react';
import { User } from '../types';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  currentUser: User | null;
  onLogout: () => void;
  onOpenAuth: (isRegister?: boolean) => void;
  onOpenHowItWorks?: () => void;
  onOpenSources?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  currentUser,
  onLogout,
  onOpenAuth,
  onOpenHowItWorks,
  onOpenSources,
}) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const authNavItems = [
    { id: 'feed', label: 'Job Feed', icon: Briefcase },
    { id: 'saved', label: 'Saved Jobs', icon: Bookmark },
    { id: 'applications', label: 'Applications', icon: CheckSquare },
    { id: 'preferences', label: 'Preferences', icon: Sliders },
  ];

  if (currentUser?.is_superuser) {
    authNavItems.push({ id: 'admin', label: 'Admin Portal', icon: Shield });
  }

  return (
    <header className="sticky top-0 z-40 glass-panel border-b border-slate-800 bg-slate-950/85 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand */}
          <div
            className="flex items-center space-x-3 cursor-pointer select-none"
            onClick={() => {
              setActiveTab('feed');
              setMobileMenuOpen(false);
            }}
          >
            <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-gradient-to-tr from-cyan-600 to-sky-400 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <Sparkles className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
            </div>
            <div>
              <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-100 to-slate-400 font-['Outfit']">
                JobIntel
              </span>
              <span className="hidden sm:inline-block ml-2 px-2 py-0.5 text-[10px] uppercase tracking-wider font-semibold bg-cyan-500/10 text-cyan-400 rounded-full border border-cyan-500/20">
                Platform
              </span>
            </div>
          </div>

          {/* Desktop Navigation Links */}
          <nav className="hidden md:flex items-center space-x-1">
            {currentUser ? (
              authNavItems.map((item) => {
                const Icon = item.icon;
                const isActive = activeTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveTab(item.id)}
                    className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                      isActive
                        ? 'bg-gradient-to-r from-cyan-600/20 to-sky-600/20 text-cyan-400 border border-cyan-500/30 shadow-sm'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                    }`}
                  >
                    <Icon className="w-3.5 h-3.5" />
                    <span>{item.label}</span>
                  </button>
                );
              })
            ) : (
              <div className="flex items-center space-x-1">
                <button
                  onClick={() => setActiveTab('feed')}
                  className={`flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    activeTab === 'feed'
                      ? 'bg-cyan-600/20 text-cyan-400 border border-cyan-500/30'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                  }`}
                >
                  <Briefcase className="w-3.5 h-3.5" />
                  <span>Job Feed</span>
                </button>
                <button
                  onClick={onOpenHowItWorks}
                  className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 transition-all"
                >
                  <HelpCircle className="w-3.5 h-3.5" />
                  <span>How It Works</span>
                </button>
                <button
                  onClick={onOpenSources}
                  className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg text-xs font-semibold text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 transition-all"
                >
                  <Globe2 className="w-3.5 h-3.5" />
                  <span>Sources</span>
                </button>
              </div>
            )}
          </nav>

          {/* User Auth Actions */}
          <div className="hidden md:flex items-center space-x-3">
            {currentUser ? (
              <div className="flex items-center space-x-3">
                <div className="flex items-center space-x-2 text-xs text-slate-300 bg-slate-900/80 px-3 py-1.5 rounded-lg border border-slate-800">
                  <UserIcon className="w-3.5 h-3.5 text-cyan-400" />
                  <span className="font-semibold">{currentUser.full_name}</span>
                  {currentUser.is_superuser && (
                    <span className="text-[9px] uppercase font-extrabold bg-amber-500/20 text-amber-400 px-1.5 py-0.5 rounded border border-amber-500/30">
                      Admin
                    </span>
                  )}
                </div>
                <button
                  onClick={onLogout}
                  title="Log out"
                  className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-slate-900 rounded-lg transition-colors border border-transparent hover:border-slate-800"
                >
                  <LogOut className="w-4 h-4" />
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => onOpenAuth(false)}
                  className="px-4 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-800/60 border border-slate-800 transition-all"
                >
                  Sign In
                </button>
                <button
                  onClick={() => onOpenAuth(true)}
                  className="px-4 py-1.5 rounded-lg text-xs font-semibold bg-gradient-to-r from-cyan-600 to-sky-500 hover:from-cyan-500 hover:to-sky-400 text-white shadow-md shadow-cyan-500/25 transition-all"
                >
                  Get Started
                </button>
              </div>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 text-slate-400 hover:text-white rounded-lg bg-slate-900 border border-slate-800"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-slate-800 bg-slate-950/95 p-4 space-y-3">
          {currentUser ? (
            <>
              <div className="flex items-center space-x-2 text-xs text-slate-300 pb-2 border-b border-slate-800">
                <UserIcon className="w-4 h-4 text-cyan-400" />
                <span className="font-semibold">{currentUser.full_name}</span>
                {currentUser.is_superuser && (
                  <span className="text-[9px] uppercase font-bold bg-amber-500/20 text-amber-400 px-1 py-0.5 rounded">
                    Admin
                  </span>
                )}
              </div>
              <div className="grid grid-cols-2 gap-2">
                {authNavItems.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => {
                      setActiveTab(item.id);
                      setMobileMenuOpen(false);
                    }}
                    className={`flex items-center space-x-2 p-2 rounded-lg text-xs font-medium ${
                      activeTab === item.id ? 'bg-cyan-500/20 text-cyan-300' : 'text-slate-400 hover:bg-slate-900'
                    }`}
                  >
                    <item.icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </button>
                ))}
              </div>
              <button
                onClick={() => {
                  onLogout();
                  setMobileMenuOpen(false);
                }}
                className="w-full mt-2 py-2 text-xs font-semibold text-rose-400 bg-rose-500/10 rounded-lg text-center"
              >
                Log Out
              </button>
            </>
          ) : (
            <div className="space-y-2">
              <button
                onClick={() => {
                  setActiveTab('feed');
                  setMobileMenuOpen(false);
                }}
                className="w-full py-2 px-3 text-left text-xs font-semibold text-slate-300 hover:bg-slate-900 rounded-lg flex items-center space-x-2"
              >
                <Briefcase className="w-4 h-4 text-cyan-400" />
                <span>Job Feed</span>
              </button>
              <button
                onClick={() => {
                  setMobileMenuOpen(false);
                  onOpenHowItWorks?.();
                }}
                className="w-full py-2 px-3 text-left text-xs font-semibold text-slate-300 hover:bg-slate-900 rounded-lg flex items-center space-x-2"
              >
                <HelpCircle className="w-4 h-4 text-cyan-400" />
                <span>How It Works</span>
              </button>
              <button
                onClick={() => {
                  setMobileMenuOpen(false);
                  onOpenSources?.();
                }}
                className="w-full py-2 px-3 text-left text-xs font-semibold text-slate-300 hover:bg-slate-900 rounded-lg flex items-center space-x-2"
              >
                <Globe2 className="w-4 h-4 text-cyan-400" />
                <span>Job Sources</span>
              </button>
              <div className="pt-2 border-t border-slate-800 flex gap-2">
                <button
                  onClick={() => {
                    setMobileMenuOpen(false);
                    onOpenAuth(false);
                  }}
                  className="flex-1 py-2 text-xs font-semibold text-center text-slate-200 bg-slate-900 border border-slate-800 rounded-lg"
                >
                  Sign In
                </button>
                <button
                  onClick={() => {
                    setMobileMenuOpen(false);
                    onOpenAuth(true);
                  }}
                  className="flex-1 py-2 text-xs font-semibold text-center text-white bg-cyan-600 rounded-lg"
                >
                  Get Started
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </header>
  );
};

