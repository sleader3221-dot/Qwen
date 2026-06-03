import React, { useEffect, useState, useRef } from 'react';
import { api } from '../services/api';
import type { Workflow, WorkflowEvent } from '../types';

export default function WorkflowViewer({ workflowId }: { workflowId: string }) {
  const [workflow, setWorkflow] = useState<Workflow | null>(null);
  const [events, setEvents] = useState<WorkflowEvent[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [loading, setLoading] = useState(true);
  const eventsEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadWorkflow();
  }, [workflowId]);

  useEffect(() => {
    eventsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [events]);

  const loadWorkflow = async () => {
    try {
      const result = await api.getWorkflow(workflowId);
      if (result.status === 'success') {
        setWorkflow(result.data);
      }
    } catch (err) {
      console.error('Failed to load workflow:', err);
    } finally {
      setLoading(false);
    }
  };

  const runWorkflow = async () => {
    setIsRunning(true);
    setEvents([]);
    try {
      const result = await api.runWorkflowSync(workflowId);
      if (result.status === 'success') {
        setEvents(prev => [...prev, { type: 'workflow_completed', ...result.data }]);
      }
      await loadWorkflow();
    } catch (err: any) {
      setEvents(prev => [...prev, { type: 'workflow_failed', error: err.message }]);
    } finally {
      setIsRunning(false);
    }
  };

  if (loading) return <div className="text-center py-12 text-gray-500">Loading workflow...</div>;
  if (!workflow) return <div className="text-center py-12 text-gray-500">Workflow not found</div>;

  const statusColors: Record<string, string> = {
    completed: 'text-emerald-400',
    running: 'text-blue-400',
    failed: 'text-red-400',
    pending: 'text-gray-400',
    awaiting_human: 'text-amber-400',
    cancelled: 'text-gray-400',
  };

  return (
    <div className="space-y-6">
      <div className="bg-gray-900 rounded-xl border border-gray-800 p-6">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold">{workflow.name}</h2>
            <p className={`text-sm mt-1 ${statusColors[workflow.status] || 'text-gray-400'}`}>
              Status: {workflow.status}
            </p>
          </div>
          <button
            onClick={runWorkflow}
            disabled={isRunning || workflow.status === 'running'}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 rounded-lg text-sm font-medium"
          >
            {isRunning ? 'Running...' : 'Run Workflow'}
          </button>
        </div>

        <div className="grid grid-cols-4 gap-4 text-sm">
          <div className="bg-gray-800/50 rounded-lg p-3">
            <div className="text-gray-400">Progress</div>
            <div className="font-medium">{workflow.progress}</div>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-3">
            <div className="text-gray-400">Confidence</div>
            <div className="font-medium">{workflow.confidence !== null ? `${(workflow.confidence * 100).toFixed(1)}%` : 'N/A'}</div>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-3">
            <div className="text-gray-400">Tokens Used</div>
            <div className="font-medium">{workflow.total_tokens?.toLocaleString()}</div>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-3">
            <div className="text-gray-400">Human Interventions</div>
            <div className="font-medium">{workflow.human_interventions}</div>
          </div>
        </div>

        {workflow.error && (
          <div className="mt-4 bg-red-900/30 border border-red-800 rounded-lg p-3 text-sm text-red-300">
            Error: {workflow.error}
          </div>
        )}
      </div>

      <div className="bg-gray-900 rounded-xl border border-gray-800 p-6">
        <h3 className="text-sm font-medium text-gray-400 mb-4">Execution Steps</h3>
        <div className="space-y-2">
          {workflow.steps?.map((step, i) => (
            <div key={i} className="flex items-center gap-3 bg-gray-800/30 rounded-lg p-3 text-sm">
              <span className={`w-2 h-2 rounded-full ${
                step.status === 'completed' ? 'bg-emerald-400' :
                step.status === 'running' ? 'bg-blue-400 animate-pulse' :
                step.status === 'failed' ? 'bg-red-400' :
                step.status === 'awaiting_human' ? 'bg-amber-400' :
                'bg-gray-600'
              }`} />
              <span className="text-gray-500 w-6">{i + 1}.</span>
              <span className="flex-1">{step.type}</span>
              <span className="text-xs text-gray-500 capitalize">{step.agent}</span>
              {step.confidence !== null && (
                <span className="text-xs text-gray-500">{(step.confidence * 100).toFixed(0)}%</span>
              )}
              <span className={`text-xs capitalize ${
                step.status === 'completed' ? 'text-emerald-400' :
                step.status === 'failed' ? 'text-red-400' :
                step.status === 'running' ? 'text-blue-400' :
                'text-gray-500'
              }`}>{step.status}</span>
              {step.requires_human && (
                <span className="text-xs text-amber-400">⚠ Needs review</span>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="bg-gray-900 rounded-xl border border-gray-800 p-6">
        <h3 className="text-sm font-medium text-gray-400 mb-4">Event Stream</h3>
        <div className="max-h-64 overflow-y-auto space-y-1">
          {events.map((event, i) => (
            <div key={i} className="text-xs font-mono text-gray-500">
              <span className="text-blue-400">[{event.type}]</span>
              {event.error && <span className="text-red-400"> {event.error}</span>}
              {event.total_tokens && <span className="text-green-400"> tokens: {event.total_tokens}</span>}
              {event.step_index !== undefined && <span> step: {event.step_index}</span>}
            </div>
          ))}
          <div ref={eventsEndRef} />
        </div>
      </div>
    </div>
  );
}
