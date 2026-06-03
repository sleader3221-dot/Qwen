const API_BASE = '/api/v1';

async function fetchApi<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${endpoint}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) throw new Error(`API error: ${res.status} ${res.statusText}`);
  return res.json();
}

export const api = {
  health: () => fetchApi<any>('/health'),
  
  createWorkflow: (name: string, task: string, tags?: string[]) =>
    fetchApi<any>(`/workflows?name=${encodeURIComponent(name)}&task=${encodeURIComponent(task)}${tags ? `&tags=${encodeURIComponent(JSON.stringify(tags))}` : ''}`, { method: 'POST' }),

  getWorkflow: (id: string) => fetchApi<any>(`/workflows/${id}`),

  listWorkflows: (status?: string, limit = 20, offset = 0) =>
    fetchApi<any>(`/workflows?limit=${limit}&offset=${offset}${status ? `&status=${status}` : ''}`),

  runWorkflowSync: (id: string) =>
    fetchApi<any>(`/workflows/${id}/run-sync`, { method: 'POST' }),

  cancelWorkflow: (id: string) =>
    fetchApi<any>(`/workflows/${id}/cancel`, { method: 'POST' }),

  approveStep: (workflowId: string, stepOrder: number, approved: boolean, feedback?: string) =>
    fetchApi<any>(`/workflows/${workflowId}/approve?step_order=${stepOrder}&approved=${approved}${feedback ? `&feedback=${encodeURIComponent(feedback)}` : ''}`, { method: 'POST' }),

  getDashboard: () => fetchApi<any>('/analytics/dashboard'),
  
  getTimeline: (days = 7) => fetchApi<any>(`/analytics/timeline?days=${days}`),

  getTokenUsage: () => fetchApi<any>('/token-usage'),

  getAuditLogs: (workflowId?: string, limit = 50) =>
    fetchApi<any>(`/audit-logs?limit=${limit}${workflowId ? `&workflow_id=${workflowId}` : ''}`),

  getFeatures: () => fetchApi<any>('/features'),

  getAlibabaCloudProof: () => fetchApi<any>('/alibaba-cloud-proof'),
};
