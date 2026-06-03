# Enterprise AI Autopilot - Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            ENTERPRISE AI AUTOPILOT                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────────────────────────────────────┐      │
│  │   Frontend   │    │              Backend (FastAPI)               │      │
│  │  (React +    │◄──►│                                              │      │
│  │   Tailwind)  │    │  ┌─────────┐  ┌──────────┐  ┌────────────┐  │      │
│  │              │    │  │  REST   │  │ WebSocket│  │  SSE Event │  │      │
│  │  Dashboard   │    │  │  API    │  │  Server  │  │   Stream   │  │      │
│  │  Workflow    │    │  └────┬────┘  └────┬─────┘  └─────┬──────┘  │      │
│  │  Viewer      │    │       │            │             │         │      │
│  │  AI Console  │    │       └────────────┴─────────────┘         │      │
│  └──────────────┘    │                    │                        │      │
│                      │         ┌──────────┴──────────┐             │      │
│                      │         │  Workflow Service   │             │      │
│                      │         └──────────┬──────────┘             │      │
│                      │                    │                        │      │
│                      │         ┌──────────┴──────────┐             │      │
│                      │         │  Workflow Service   │             │      │
│                      │         │  Orchestrator       │             │      │
│                      │         └──────────┬──────────┘             │      │
│                      │                    │                        │      │
│  ┌───────────────────────────────────────────────────────────────┐ │      │
│  │                    Multi-Agent System                         │ │      │
│  │                                                               │ │      │
│  │  ┌────────────┐ ┌───────────┐ ┌──────────┐ ┌───────────────┐ │ │      │
│  │  │  Email     │ │ Document  │ │Scheduler │ │    CRM        │ │ │      │
│  │  │  Agent     │ │ Agent     │ │ Agent    │ │   Agent       │ │ │      │
│  │  └────────────┘ └───────────┘ └──────────┘ └───────────────┘ │ │      │
│  │  ┌────────────┐ ┌───────────┐ ┌──────────┐ ┌───────────────┐ │ │      │
│  │  │  Data      │ │Notification│ │ Code     │ │   Report      │ │ │      │
│  │  │  Agent     │ │ Agent     │ │ Review   │ │   Agent       │ │ │      │
│  │  └────────────┘ └───────────┘ └──────────┘ └───────────────┘ │ │      │
│  └───────────────────────────────────────────────────────────────┘ │      │
│                      │                                             │      │
│         ┌────────────┴──────────────────────┐                      │      │
│         │         Qwen Cloud (DashScope)     │                     │      │
│         │  ┌─────────────────────────────┐  │                     │      │
│         │  │ qwen3.6-plus (Primary)      │  │                     │      │
│         │  │ qwen3.6-flash (Cost-opt)    │  │                     │      │
│         │  │ Chat Completions API        │  │                     │      │
│         │  │ Responses API               │  │                     │      │
│         │  │ Function Calling            │  │                     │      │
│         │  │ Built-in Tools              │  │                     │      │
│         │  │ (Web Search, Code Interp.)  │  │                     │      │
│         │  │ Thinking Mode               │  │                     │      │
│         │  │ Session Cache               │  │                     │      │
│         │  └─────────────────────────────┘  │                     │      │
│         └────────────────────────────────────┘                     │      │
│                      │                                             │      │
│  ┌──────────────────────────────────────────────────────────────┐  │      │
│  │                   Data Layer                                 │  │      │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐ │  │      │
│  │  │PostgreSQL│  │  Redis   │  │  SQLite  │  │ Agent Memory │ │  │      │
│  │  │(Primary) │  │ (Cache)  │  │ (Dev)    │  │  System      │ │  │      │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────────┘ │  │      │
│  └──────────────────────────────────────────────────────────────┘  │      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Key Architectural Decisions

### 1. Multi-Agent Orchestration
- **Orchestrator Agent**: Central coordinator that decomposes tasks, assigns work, monitors progress, and synthesizes results
- **Specialized Agents**: Each agent handles specific domains (email, documents, CRM, data, etc.)
- **Agent Communication**: via shared database and memory system

### 2. Qwen Cloud Integration
- **Primary Model**: `qwen3.6-plus` - balanced performance with 1M context, full tool support
- **Cost-Optimized**: `qwen3.6-flash` for high-volume, simple tasks
- **API**: OpenAI-compatible Chat Completions API for flexibility
- **Built-in Tools**: Web search, code interpreter, web extractor via Responses API
- **Thinking Mode**: Enabled for complex reasoning tasks
- **Session Cache**: Automatic context caching for multi-turn conversations

### 3. Memory System
- **Persistent Memory**: Cross-session storage in PostgreSQL via AgentMemory table
- **Importance Scoring**: Memories scored by relevance and pruned automatically
- **TTL-Based Forgetting**: Old, low-importance memories are periodically cleaned
- **Context Injection**: Relevant memories injected into agent context

### 4. Human-in-the-Loop
- **Confidence Scoring**: Each agent output is scored; low confidence triggers human review
- **Configurable Threshold**: Adjustable via `CONFIDENCE_THRESHOLD` setting
- **Awaiting State**: Workflows pause at human checkpoints
- **Approval API**: REST endpoints for human approval/rejection with feedback

### 5. Error Handling
- **Retry with Backoff**: Exponential backoff for transient failures
- **Fallback Strategies**: per-step fallback (retry, skip, abort, alternative)
- **Error Classification**: Automatic classification for targeted recovery
- **Graceful Degradation**: System continues despite partial failures

### 6. Token Budget Management
- **Daily Budget**: Configurable daily token limit
- **Usage Tracking**: Real-time tracking across all agents
- **Warning/Critical Thresholds**: Alerts at 80%/95% usage
- **Cost Optimization**: flash model for simple tasks, thinking disabled when not needed

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend Framework | FastAPI (Python) | Async API server |
| AI Provider | Qwen Cloud (DashScope) | LLM inference |
| Database | PostgreSQL (prod) / SQLite (dev) | Persistence |
| Cache | Redis | Session caching |
| Frontend | React + TypeScript + Tailwind | Dashboard UI |
| Real-time | WebSocket + SSE | Live updates |
| Container | Docker + Docker Compose | Deployment |
| Cloud | Alibaba Cloud ECS + OSS | Production hosting |
