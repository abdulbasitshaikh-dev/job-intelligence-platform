import React, { useState } from 'react';
import { CheckSquare, Trash2, Edit3, Building, MapPin, ExternalLink, Calendar } from 'lucide-react';
import { JobApplication } from '../types';
import { ApiClient } from '../lib/api';

interface ApplicationsBoardProps {
  applications: JobApplication[];
  onRefresh: () => void;
}

export const ApplicationsBoard: React.FC<ApplicationsBoardProps> = ({ applications, onRefresh }) => {
  const [editingNotesId, setEditingNotesId] = useState<number | null>(null);
  const [notesText, setNotesText] = useState('');

  const statuses = [
    { id: 'interested', label: 'Interested', color: 'bg-slate-500/20 text-slate-300 border-slate-700' },
    { id: 'applied', label: 'Applied', color: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/30' },
    { id: 'interview', label: 'Interviewing', color: 'bg-purple-500/20 text-purple-300 border-purple-500/30' },
    { id: 'offer', label: 'Received Offer', color: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30' },
    { id: 'rejected', label: 'Rejected', color: 'bg-rose-500/20 text-rose-300 border-rose-500/30' },
    { id: 'withdrawn', label: 'Withdrawn', color: 'bg-amber-500/20 text-amber-300 border-amber-500/30' },
  ];

  const handleStatusUpdate = async (appId: number, newStatus: string) => {
    try {
      await ApiClient.fetch(`/applications/${appId}`, {
        method: 'PATCH',
        body: JSON.stringify({ status: newStatus }),
      });
      onRefresh();
    } catch (err: any) {
      alert(err.message || 'Failed to update status');
    }
  };

  const handleSaveNotes = async (appId: number) => {
    try {
      await ApiClient.fetch(`/applications/${appId}`, {
        method: 'PATCH',
        body: JSON.stringify({ notes: notesText }),
      });
      setEditingNotesId(null);
      onRefresh();
    } catch (err: any) {
      alert(err.message || 'Failed to save notes');
    }
  };

  const handleDelete = async (appId: number) => {
    if (!confirm('Are you sure you want to remove this application record?')) return;
    try {
      await ApiClient.fetch(`/applications/${appId}`, { method: 'DELETE' });
      onRefresh();
    } catch (err: any) {
      alert(err.message || 'Failed to delete application');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white font-['Outfit']">Application Tracker</h2>
          <p className="text-xs text-slate-400 mt-1">Manage and track your active job application lifecycle</p>
        </div>
        <span className="px-3 py-1 rounded-full text-xs font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
          {applications.length} Tracked Applications
        </span>
      </div>

      {applications.length === 0 ? (
        <div className="glass-panel rounded-2xl p-12 text-center">
          <CheckSquare className="w-12 h-12 text-slate-600 mx-auto mb-3" />
          <h3 className="text-lg font-semibold text-slate-300">No applications tracked yet</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1">
            Browse the job feed and select status options on job cards to track your progress here.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {applications.map((app) => {
            const statusConfig = statuses.find((s) => s.id === app.status) || statuses[0];
            const job = app.job;

            return (
              <div key={app.id} className="glass-card rounded-xl p-5 flex flex-col justify-between">
                <div>
                  <div className="flex items-start justify-between gap-2">
                    <span className={`px-2.5 py-1 rounded-full text-xs font-bold border ${statusConfig.color}`}>
                      {statusConfig.label}
                    </span>
                    <button
                      onClick={() => handleDelete(app.id)}
                      className="text-slate-500 hover:text-rose-400 p-1"
                      title="Delete application"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>

                  <h3 className="text-base font-bold text-white mt-3 line-clamp-1">
                    {job?.title || 'Job Opportunity'}
                  </h3>
                  <div className="flex items-center space-x-2 text-xs text-slate-400 mt-1">
                    <span className="flex items-center space-x-1 font-medium text-slate-300">
                      <Building className="w-3.5 h-3.5 text-slate-500" />
                      <span>{job?.company || 'Company'}</span>
                    </span>
                    <span>•</span>
                    <span className="flex items-center space-x-1">
                      <MapPin className="w-3.5 h-3.5 text-slate-500" />
                      <span>{job?.location || 'Remote'}</span>
                    </span>
                  </div>

                  {/* Notes section */}
                  <div className="mt-4 pt-3 border-t border-slate-800/80">
                    <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
                      <span className="font-semibold uppercase tracking-wider text-[10px] text-slate-500">Notes & Logs</span>
                      {editingNotesId !== app.id && (
                        <button
                          onClick={() => {
                            setEditingNotesId(app.id);
                            setNotesText(app.notes || '');
                          }}
                          className="text-cyan-400 hover:underline flex items-center space-x-1"
                        >
                          <Edit3 className="w-3 h-3" />
                          <span>Edit</span>
                        </button>
                      )}
                    </div>

                    {editingNotesId === app.id ? (
                      <div className="space-y-2">
                        <textarea
                          value={notesText}
                          onChange={(e) => setNotesText(e.target.value)}
                          placeholder="Add interviewer names, interview dates, follow-up notes..."
                          rows={2}
                          className="w-full bg-slate-900 text-xs text-slate-100 p-2 rounded-lg border border-slate-700 focus:outline-none focus:border-cyan-500"
                        />
                        <div className="flex justify-end space-x-2">
                          <button
                            onClick={() => setEditingNotesId(null)}
                            className="px-2 py-1 text-xs text-slate-400 hover:text-white"
                          >
                            Cancel
                          </button>
                          <button
                            onClick={() => handleSaveNotes(app.id)}
                            className="px-3 py-1 bg-cyan-600 hover:bg-cyan-500 text-white font-semibold text-xs rounded-md"
                          >
                            Save Notes
                          </button>
                        </div>
                      </div>
                    ) : (
                      <p className="text-xs text-slate-300 italic bg-slate-900/50 p-2.5 rounded-lg border border-slate-800/60 min-h-[36px]">
                        {app.notes || 'No notes added yet.'}
                      </p>
                    )}
                  </div>
                </div>

                {/* Status Switcher Footer */}
                <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-xs">
                  <select
                    value={app.status}
                    onChange={(e) => handleStatusUpdate(app.id, e.target.value)}
                    className="bg-slate-900 text-xs font-semibold text-slate-300 border border-slate-800 rounded-lg px-2 py-1 focus:outline-none focus:border-cyan-500"
                  >
                    {statuses.map((s) => (
                      <option key={s.id} value={s.id}>
                        {s.label}
                      </option>
                    ))}
                  </select>

                  {job?.url && (
                    <a
                      href={job.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-cyan-400 hover:underline flex items-center space-x-1 font-medium"
                    >
                      <span>Link</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
