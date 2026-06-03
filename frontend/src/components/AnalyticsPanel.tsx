import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import type { DashboardStats, AnalyticsTimeline } from '../types';

export default function AnalyticsPanel() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [timeline, setTimeline] = useState<AnalyticsTimeline[]>([]);

  useEffect(() => {
    Promise.all([api.getDashboard(), api.getTimeline(14)]).then(([dash, tl]) => {
      if (dash.status === 'success') setStats(dash.data);
      if (tl.status === 'success') setTimeline(Array.isArray(tl.data) ? tl.data : []);
    }).catch(console.error);
  }, []);

  if (!stats) return <div className="text-center py-12 text-gray-500">Loading analytics...</div>;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Completed', value: stats.completed, color: 'from-emerald-500' },
          { label: 'Failed', value: stats.failed, color: 'from-red-500' },
          { label: 'Running', value: stats.running, color: 'from-blue-500' },
          { label: 'Success Rate', value: `${stats.success_rate}%`, color: 'from-purple-500' },
        ].map(card => (
          <div key={card.label} className="bg-gray-900 rounded-xl border border-gray-800 p-4">
            <div className={`h-1 w-8 rounded-full bg-gradient-to-r ${card.color} to-transparent mb-3`} />
            <div className="text-2xl font-bold">{card.value}</div>
            <div className="text-sm text-gray-400 mt-1">{card.label}</div>
          </div>
        ))}
      </div>

      <div className="bg-gray-900 rounded-xl border border-gray-800 p-6">
        <h3 className="text-sm font-medium text-gray-400 mb-4">Workflow Timeline (14 days)</h3>
        <div className="space-y-2">
          {timeline.map(day => (
            <div key={day.date} className="flex items-center gap-4 text-sm">
              <span className="w-24 text-gray-500">{day.date}</span>
              <div className="flex-1 bg-gray-800 rounded-full h-3 overflow-hidden flex">
                {day.total > 0 && (
                  <>
                    <div
                      className="bg-emerald-500 h-full transition-all"
                      style={{ width: `${(day.completed / day.total) * 100}%` }}
                    />
                    <div
                      className="bg-red-500 h-full transition-all"
                      style={{ width: `${(day.failed / day.total) * 100}%` }}
                    />
                  </>
                )}
              </div>
              <span className="text-gray-500 w-32 text-right">{day.total} workflows</span>
              <span className="text-gray-500 w-24 text-right">{(day.tokens / 1000).toFixed(1)}k tokens</span>
            </div>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-6">
          <h3 className="text-sm font-medium text-gray-400 mb-3">Token Usage</h3>
          <div className="text-3xl font-bold">{stats.total_tokens_used.toLocaleString()}</div>
          <div className="text-sm text-gray-500 mt-1">Total tokens consumed</div>
          <div className="mt-3 bg-gray-800 rounded-full h-2 overflow-hidden">
            <div className="bg-gradient-to-r from-blue-500 to-purple-500 h-full rounded-full" style={{ width: `${Math.min((stats.tokens_today / Math.max(stats.total_tokens_used, 1)) * 100, 100)}%` }} />
          </div>
          <div className="text-xs text-gray-500 mt-1">{stats.tokens_today.toLocaleString()} today</div>
        </div>
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-6">
          <h3 className="text-sm font-medium text-gray-400 mb-3">Human in the Loop</h3>
          <div className="text-3xl font-bold">{stats.human_interventions}</div>
          <div className="text-sm text-gray-500 mt-1">Total human interventions</div>
          <div className="mt-3 text-xs text-gray-500">
            avg {(stats.human_interventions / Math.max(stats.total_workflows, 1)).toFixed(2)} per workflow
          </div>
        </div>
      </div>
    </div>
  );
}
