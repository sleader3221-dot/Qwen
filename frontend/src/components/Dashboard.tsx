import React, { useEffect, useState, useCallback } from 'react';
import { api } from '../services/api';
import WorkflowViewer from './WorkflowViewer';
import AnalyticsPanel from './AnalyticsPanel';
import ChatInterface from './ChatInterface';
import type { DashboardStats, Workflow } from '../types';

type Tab = 'dashboard' | 'workflows' | 'analytics' | 'chat' | 'settings';

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<Tab>('dashboard');
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [selectedWorkflow, setSelectedWorkflow] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const refreshData = useCallback(async () => {
    try {
      const [dashResult, wfResult] = await Promise.all([
        api.getDashboard(),
        api.listWorkflows(),
      ]);
      if (dashResult.status === 'success') setStats(dashResult.data);
      if (wfResult.status === 'success') setWorkflows(wfResult.data.workflows || wfResult.data);
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => { refreshData(); const interval = setInterval(refreshData, 15000); return () => clearInterval(interval); }, [refreshData]);

  const tabs: { id: Tab; label: string; icon: string }[] = [
    { id: 'dashboard', label: 'Dashboard', icon: '◉' },
    { id: 'workflows', label: 'Workflows', icon: '⚡' },
    { id: 'analytics', label: 'Analytics', icon: '📊' },
    { id: 'chat', label: 'AI Console', icon: '💬' },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 py-6">
      <div className="flex gap-6 mb-6 border-b border-gray-800 pb-4">
        {tabs.map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              activeTab === tab.id
                ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30'
                : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800/50'
            }`}
          >
            <span>{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {activeTab === 'workflows' || activeTab === 'dashboard' ? (
        selectedWorkflow ? (
          <div>
            <button
              onClick={() => setSelectedWorkflow(null)}
              className="mb-4 text-sm text-blue-400 hover:text-blue-300 flex items-center gap-1"
            >
              ← Back to workflows
            </button>
            <WorkflowViewer workflowId={selectedWorkflow} />
          </div>
        ) : (
          <div className="space-y-6">
            {activeTab === 'dashboard' && stats && <DashboardStatsCard stats={stats} />}
            <WorkflowList
              workflows={workflows}
              isLoading={isLoading}
              onSelect={setSelectedWorkflow}
              onRefresh={refreshData}
            />
          </div>
        )
      ) : activeTab === 'analytics' ? (
        <AnalyticsPanel />
      ) : activeTab === 'chat' ? (
        <ChatInterface />
      ) : null}
    </div>
  );
}

function DashboardStatsCard({ stats }: { stats: DashboardStats }) {
  const cards = [
    { label: 'Total Workflows', value: stats.total_workflows, color: 'from-blue-500 to-blue-600' },
    { label: 'Success Rate', value: `${stats.success_rate}%`, color: 'from-emerald-500 to-emerald-600' },
    { label: 'Running Now', value: stats.running, color: 'from-amber-500 to-amber-600' },
    { label: 'Tokens Today', value: stats.tokens_today.toLocaleString(), color: 'from-purple-500 to-purple-600' },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
      {cards.map(card => (
        <div key={card.label} className="bg-gray-900 rounded-xl border border-gray-800 p-4">
          <div className={`h-1 w-12 rounded-full bg-gradient-to-r ${card.color} mb-3`} />
          <div className="text-2xl font-bold">{card.value}</div>
          <div className="text-sm text-gray-400 mt-1">{card.label}</div>
        </div>
      ))}
    </div>
  );
}

function WorkflowList({
  workflows,
  isLoading,
  onSelect,
  onRefresh,
}: {
  workflows: Workflow[];
  isLoading: boolean;
  onSelect: (id: string) => void;
  onRefresh: () => void;
}) {
  const [taskName, setTaskName] = useState('');
  const [taskDesc, setTaskDesc] = useState('');
  const [creating, setCreating] = useState(false);

  const createWorkflow = async () => {
    if (!taskName.trim() || !taskDesc.trim()) return;
    setCreating(true);
    try {
      await api.createWorkflow(taskName, taskDesc);
      setTaskName('');
      setTaskDesc('');
      onRefresh();
    } catch (err) {
      console.error('Failed to create workflow:', err);
    } finally {
      setCreating(false);
    }
  };

  const statusColors: Record<string, string> = {
    completed: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30',
    running: 'bg-blue-500/20 text-blue-400 border-blue-500/30 animate-pulse',
    failed: 'bg-red-500/20 text-red-400 border-red-500/30',
    pending: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
    awaiting_human: 'bg-amber-500/20 text-amber-400 border-amber-500/30',
    cancelled: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
  };

  return (
    <div>
      <div className="bg-gray-900 rounded-xl border border-gray-800 p-4 mb-6">
        <h3 className="text-sm font-medium text-gray-300 mb-3">New Autonomous Workflow</h3>
        <div className="flex gap-3">
          <input
            value={taskName}
            onChange={e => setTaskName(e.target.value)}
            placeholder="Workflow name..."
            className="flex-1 bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
          />
          <input
            value={taskDesc}
            onChange={e => setTaskDesc(e.target.value)}
            placeholder="Describe the task to automate..."
            className="flex-[2] bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500"
          />
          <button
            onClick={createWorkflow}
            disabled={creating || !taskName.trim() || !taskDesc.trim()}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 rounded-lg text-sm font-medium transition-colors"
          >
            {creating ? 'Creating...' : 'Create & Run'}
          </button>
        </div>
      </div>

      <div className="space-y-2">
        {workflows.map(wf => (
          <div
            key={wf.id}
            onClick={() => onSelect(wf.id)}
            className="bg-gray-900 border border-gray-800 rounded-lg p-4 hover:border-gray-700 cursor-pointer transition-colors group"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className={`px-2 py-0.5 rounded text-xs font-medium border ${statusColors[wf.status] || statusColors.pending}`}>
                  {wf.status}
                </span>
                <div>
                  <div className="font-medium">{wf.name}</div>
                  <div className="text-xs text-gray-500 mt-0.5">ID: {wf.id.slice(0, 12)}…</div>
                </div>
              </div>
              <div className="flex items-center gap-4 text-xs text-gray-500">
                <span>{wf.progress} steps</span>
                <span>{wf.total_tokens?.toLocaleString()} tokens</span>
                {wf.confidence !== null && <span>{(wf.confidence * 100).toFixed(0)}% confidence</span>}
                <span className="text-blue-400 opacity-0 group-hover:opacity-100 transition-opacity">View →</span>
              </div>
            </div>
          </div>
        ))}
        {isLoading && <div className="text-center py-8 text-gray-500">Loading workflows...</div>}
        {!isLoading && workflows.length === 0 && (
          <div className="text-center py-8 text-gray-500">No workflows yet. Create one above!</div>
        )}
      </div>
    </div>
  );
}
