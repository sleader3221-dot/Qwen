export interface Workflow {
  id: string;
  name: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'paused' | 'cancelled' | 'awaiting_human';
  progress: string;
  confidence: number | null;
  total_tokens: number;
  error: string | null;
  created_at: string;
  completed_at: string | null;
  tags: string[];
  human_interventions: number;
  steps: WorkflowStep[];
}

export interface WorkflowStep {
  order: number;
  type: string;
  agent: string;
  status: string;
  confidence: number | null;
  requires_human: boolean;
  human_approved: boolean | null;
  error: string | null;
}

export interface DashboardStats {
  total_workflows: number;
  workflows_today: number;
  completed: number;
  failed: number;
  running: number;
  success_rate: number;
  total_tokens_used: number;
  tokens_today: number;
  avg_tokens_per_workflow: number;
  human_interventions: number;
}

export interface WorkflowEvent {
  type: string;
  plan?: any;
  total_steps?: number;
  step_index?: number;
  step?: any;
  result?: any;
  error?: string;
  output?: any;
  total_tokens?: number;
  reason?: string;
}

export interface AnalyticsTimeline {
  date: string;
  total: number;
  completed: number;
  failed: number;
  tokens: number;
}

export interface ApiResponse<T> {
  status: 'success' | 'error';
  message?: string;
  data: T;
  pagination?: {
    total: number;
    limit: number;
    offset: number;
    has_more: boolean;
  };
  timestamp: string;
}
