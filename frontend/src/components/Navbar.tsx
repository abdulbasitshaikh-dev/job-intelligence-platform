import React from 'react';
import { Briefcase, Bookmark, CheckSquare, Sliders, Shield, LogOut, User as UserIcon, Sparkles } from 'lucide-react';
import { User } from '../types';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  currentUser: User | null;
  onLogout: () => void;
  onOpenAuth: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  activeTab,
  setActiveTab,
  currentUser,
  onLogout,
  onOpenAuth,
}) => {
  const navItems = [
    { id: 'feed', label: 'Job Feed', icon: Briefcase },
    { id: 'saved', label: 'Saved Jobs', icon: Bookmark },
    { id: 'applications', label: 'Applications', icon: CheckSquare },
    { id: 'preferences', label: 'Preferences', icon: Sliders },
  ];

  if (currentUser?.is_superuser) {
    navItems.push({ id: 'admin', label: 'Admin Portal', icon: Shield });
  }

  return (
    <header className="sticky top-0 z-40 glass-panel border-b border-slate-800 bg-slate-950/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Brand */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setActiveTab('feed')}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-cyan-600 to-sky-400 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <Sparkles className="w-6 h-6 text-white" />
            </div>
            <div>
              <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white via-slate-100 to-slate-400 font-['Outfit']">
                JobIntel
              </span>
              <span className="hidden sm:inline-block ml-2 px-2 py-0.5 text-xs font-medium bg-cyan-500/10 text-cyan-400 rounded-full border border-cyan-500/20">
                Platform
              </span>
            </div>
          </div>

          {/* Navigation Links */}
          {currentUser && (
            <nav className="hidden md:flex items-center space-x-1">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = activeTab === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveTab(item.id)}
                    className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                      isActive
                        ? 'bg-gradient-to-r from-cyan-600/20 to-sky-600/20 text-cyan-400 border border-cyan-500/30'
                        : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{item.label}</span>
                  </button>
                );
              })}
            </nav>
          )}

          {/* User Auth Section */}
          <div className="flex items-center space-x-4">
            {currentUser ? (
              <div className="flex items-center space-x-3">
                <div className="flex items-center space-x-2 text-sm text-slate-300 bg-slate-900/80 px-3 py-1.5 rounded-lg border border-slate-800">
                  <UserIcon className="w-4 h-4 text-cyan-400" />
                  <span className="font-medium">{currentUser.full_name}</span>
                  {currentUser.is_superuser && (
                    <span className="text-[10px] uppercase font-bold bg-amber-500/20 text-amber-400 px-1.5 py-0.5 rounded">
                      Admin
                    </span>
                  )}
                </div>
                <button
                  onClick={onLogout}
                  title="Log out"
                  className="p-2 text-slate-400 hover:text-rose-400 hover:bg-slate-900 rounded-lg transition-colors"
                >
                  <LogOut className="w-5 h-5" />
                </button>
              </div>
            ) : (
              <button
                onClick={onOpenAuth}
                className="px-5 py-2 rounded-lg text-sm font-medium bg-gradient-to-r from-cyan-600 to-sky-500 hover:from-cyan-500 hover:to-sky-400 text-white shadow-lg shadow-cyan-500/25 transition-all"
              >
                Sign In
              </button>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
