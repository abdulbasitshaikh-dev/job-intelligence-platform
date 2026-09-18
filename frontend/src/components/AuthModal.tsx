import React, { useState } from 'react';
import { X, Lock, Mail, User as UserIcon, Sparkles } from 'lucide-react';
import { ApiClient } from '../lib/api';
import { User } from '../types';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAuthSuccess: (user: User) => void;
}

export const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose, onAuthSuccess }) => {
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isRegister) {
        await ApiClient.fetch('/auth/register', {
          method: 'POST',
          body: JSON.stringify({ email, password, full_name: fullName }),
        });
      }

      // Login to obtain tokens
      const tokenRes: any = await ApiClient.fetch('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      });

      ApiClient.setTokens(tokenRes.access_token, tokenRes.refresh_token);
      const userRes: User = await ApiClient.fetch('/auth/me');
      onAuthSuccess(userRes);
      onClose();
    } catch (err: any) {
      setError(err.message || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
      <div className="glass-panel rounded-2xl w-full max-w-md p-6 relative border border-slate-700 shadow-2xl">
        <button
          onClick={onClose}
          className="absolute right-4 top-4 text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800"
        >
          <X className="w-5 h-5" />
        </button>

        <div className="text-center mb-6">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-cyan-500 to-sky-400 flex items-center justify-center text-white mx-auto mb-3 shadow-lg shadow-cyan-500/30">
            <Sparkles className="w-6 h-6" />
          </div>
          <h2 className="text-2xl font-bold text-white font-['Outfit']">
            {isRegister ? 'Create an Account' : 'Welcome Back'}
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            {isRegister ? 'Start tracking & matching job opportunities' : 'Sign in to access your dashboard'}
          </p>
        </div>




        {error && (
          <div className="mb-4 p-3 bg-rose-500/10 border border-rose-500/30 rounded-xl text-xs text-rose-400">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {isRegister && (
            <div>
              <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
                Full Name
              </label>
              <div className="relative">
                <UserIcon className="w-4 h-4 absolute left-3 top-3 text-slate-500" />
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="Basit Ali"
                  className="w-full bg-slate-900 text-sm text-slate-100 placeholder-slate-500 rounded-xl pl-10 pr-4 py-2.5 border border-slate-800 focus:outline-none focus:border-cyan-500"
                />
              </div>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
              Email Address
            </label>
            <div className="relative">
              <Mail className="w-4 h-4 absolute left-3 top-3 text-slate-500" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="user@example.com"
                className="w-full bg-slate-900 text-sm text-slate-100 placeholder-slate-500 rounded-xl pl-10 pr-4 py-2.5 border border-slate-800 focus:outline-none focus:border-cyan-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1">
              Password
            </label>
            <div className="relative">
              <Lock className="w-4 h-4 absolute left-3 top-3 text-slate-500" />
              <input
                type="password"
                required
                minLength={8}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-slate-900 text-sm text-slate-100 placeholder-slate-500 rounded-xl pl-10 pr-4 py-2.5 border border-slate-800 focus:outline-none focus:border-cyan-500"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full mt-2 py-3 rounded-xl font-bold bg-gradient-to-r from-cyan-600 to-sky-500 hover:from-cyan-500 hover:to-sky-400 text-white shadow-lg shadow-cyan-500/25 transition-all text-sm disabled:opacity-50"
          >
            {loading ? 'Processing...' : isRegister ? 'Register Account' : 'Sign In'}
          </button>
        </form>

        <div className="text-center mt-4 text-xs text-slate-400">
          {isRegister ? 'Already have an account?' : "Don't have an account?"}{' '}
          <button
            type="button"
            onClick={() => {
              setIsRegister(!isRegister);
              setError('');
            }}
            className="text-cyan-400 hover:underline font-semibold"
          >
            {isRegister ? 'Sign In' : 'Register'}
          </button>
        </div>
      </div>
    </div>
  );
};
