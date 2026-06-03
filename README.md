# Enterprise AI Autopilot

> **Track 4: Autopilot Agent** — Global AI Hackathon Series with Qwen Cloud

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Qwen Cloud](https://img.shields.io/badge/Powered%20by-Qwen%20Cloud-blueviolet)](https://www.qwencloud.com)
[![Python](https://img.shields.io/badge/Python-3.12+-green)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-teal)](https://fastapi.tiangolo.com)

An **intelligent, autonomous business workflow automation platform** that uses Qwen Cloud's advanced AI to plan, execute, and manage complex business processes end-to-end — with human oversight at critical decision points.

## ✨ 30+ Advanced Features

### Core Engine
1. **Multi-Agent Orchestrator** — Hierarchical agent system with specialized sub-agents
2. **Autonomous Task Decomposition** — Breaks complex workflows into atomic steps
3. **Confidence-Based Escalation** — Human-in-the-loop when confidence is low
4. **Self-Healing Error Recovery** — Automatic retry with backoff and alternative paths
5. **Persistent Agent Memory** — Cross-session learning from past decisions
6. **MCP Tool Integration** — Model Context Protocol for standardized tool access
7. **Built-in Tools** — Web search, code interpreter, web extractor via Responses API
8. **Qwen Thinking Mode** — Deep reasoning for complex business decisions
9. **Structured Output** — JSON mode for programmatic data extraction
10. **Real-Time Streaming** — SSE-based workflow progress updates

### Business Automation
11. **Intelligent Email Processing** — Auto-classify, prioritize, route, and respond
12. **Document Understanding & Generation** — Parse and generate business documents
13. **Smart Scheduling** — Automated calendar management and meeting coordination
14. **CRM Integration** — Contact management, lead tracking, pipeline optimization
15. **Natural Language Data Queries** — NL-to-SQL for business intelligence
16. **Code Review Automation** — PR analysis, security audit, fix suggestions
17. **Automated Report Generation** — Business intelligence with visualizations
18. **Multi-Channel Notifications** — Email, Slack, Teams integration
19. **Workflow Templates** — Pre-built business process templates
20. **Custom Workflow Builder** — Create workflows via natural language

### Intelligence & Reliability
21. **Confidence Scoring** — ML-based confidence estimation for every decision
22. **Token Budget Optimization** — Intelligent cost management across agents
23. **Multi-Modal Input** — Process text, images, documents, and code
24. **Web Search Augmented Decisions** — Real-time data for informed actions
25. **Vector Memory Retrieval** — Semantic search across past interactions
26. **Anomaly Detection & Alerting** — Proactive system monitoring
27. **Session Cache** — Qwen Cloud's automatic context caching
28. **Batch Processing** — Async bulk processing at 50% cost

### Observability & Control
29. **Human-in-the-Loop Checkpoints** — Review before critical decisions
30. **Real-Time Dashboard** — Live workflow visualization with WebSocket updates
31. **Comprehensive Audit Trail** — Full transaction history with compliance logging
32. **Analytics & Insights Engine** — Performance metrics, bottleneck detection
33. **Role-Based Access Control** — Multi-tenant with granular permissions
34. **Graceful Degradation** — System continues despite partial failures
35. **Plugin Architecture** — Extensible tool/connector system

## 🎯 Track Focus: Autopilot Agent

This project is submitted for **Track 4: Autopilot Agent**, which emphasizes:

- **Production-readiness** over toy demos
- **Real-world business workflow automation** end-to-end
- **Human-in-the-loop** checkpoints at critical decision points
- **Ambiguous input handling** and external tool invocation

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Enterprise AI Autopilot                  │
│  ┌──────────┐  ┌──────────────────────────────────────┐    │
│  │ Frontend │  │           Backend (FastAPI)          │    │
│  │ (React)  │◄─┤  ┌────────┐ ┌─────────┐ ┌─────────┐ │    │
│  │          │  │  │  REST  │ │WebSocket│ │   SSE   │ │    │
│  └──────────┘  │  │  API   │ │ Server  │ │ Stream  │ │    │
│                │  └────────┘ └─────────┘ └─────────┘ │    │
│                │         ┌──────────────────┐         │    │
│                │         │   Orchestrator   │         │    │
│                │         └────────┬─────────┘         │    │
│                │    ┌─────────────┼─────────────┐     │    │
│                │  ┌─┴──┐ ┌───┴───┐ ┌──┴──┐ ┌───┴──┐ │    │
│                │  │Email│ │Document│ │ CRM │ │ Data │...│    │
│                │  └────┘ └───────┘ └─────┘ └──────┘ │    │
│                │         ┌──────────────────┐         │    │
│                │         │  Qwen Cloud API  │         │    │
│                │         │ (qwen3.6-plus)   │         │    │
│                │         └──────────────────┘         │    │
│                │  ┌────────┐ ┌────────┐ ┌──────────┐ │    │
│                │  │Postgres│ │ Redis  │ │ Memory   │ │    │
│                │  └────────┘ └────────┘ └──────────┘ │    │
│                └──────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Local Development
```bash
# 1. Backend
pip install -r requirements.txt
cd backend && uvicorn app.main:app --reload --port 8000

# 2. Frontend (new terminal)
cd frontend && npm install && npm run dev

# 3. Open http://localhost:3000
```

### One-Click Vercel Deploy

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2FUSER%2Fenterprise-autopilot-agent&env=DASHSCOPE_API_KEY,SECRET_KEY&envDescription=Get%20your%20Qwen%20Cloud%20API%20key%20at%20https%3A%2F%2Fwww.qwencloud.com&project-name=enterprise-autopilot-agent&repository-name=enterprise-autopilot-agent)

```bash
# Or deploy from the command line:
.\setup-vercel.ps1                    # preview deploy
.\setup-vercel.ps1 -Prod              # production deploy
```

After deploying, set these environment variables in your Vercel dashboard:
- `DASHSCOPE_API_KEY` — Your Qwen Cloud API key
- `SECRET_KEY` — A random secret string for session security

Your app will be live at `https://your-project.vercel.app` with:
- **Frontend**: React dashboard at `/`
- **Backend API**: FastAPI at `/api/v1/*`
- **API Docs**: Swagger UI at `/api/docs`
- **WebSocket**: Real-time updates at `/ws/*`

### Vercel Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                        Vercel Edge Network                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  https://your-project.vercel.app                        │   │
│  │  ┌──────────────┐        ┌─────────────────────────┐   │   │
│  │  │  / (static)  │        │  /api/* (serverless)    │   │   │
│  │  │  React SPA   │───────▶│  FastAPI + Qwen Cloud   │   │   │
│  │  │  dashboard   │        │  ┌───────────────────┐  │   │   │
│  │  └──────────────┘        │  │  8 AI Agents      │  │   │   │
│  │                          │  │  Multi-Orchestrator│  │   │   │
│  │                          │  │  Task Planner     │  │   │   │
│  │                          │  │  Memory System    │  │   │   │
│  │                          │  │  Qwen Cloud API   │  │   │   │
│  │                          │  └───────────────────┘  │   │   │
│  │                          └─────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────┘   │
│    ┌──────────────────────────────────────────────────┐        │
│    │  Environment Variables (Vercel Dashboard)         │        │
│    │  DASHSCOPE_API_KEY | DATABASE_URL | SECRET_KEY    │        │
│    └──────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

## 💻 Demo

### Create a Workflow
```bash
curl -X POST "http://localhost:8000/api/v1/workflows?name=Q4+Review&task=Send+Q4+email+to+team+and+schedule+meeting"
```

### Execute Autonomously
```bash
curl -X POST "http://localhost:8000/api/v1/workflows/{id}/run-sync"
```

### Approve Human Step
```bash
curl -X POST "http://localhost:8000/api/v1/workflows/{id}/approve?step_order=2&approved=true"
```

## 🧠 Qwen Cloud Integration

| Capability | Implementation |
|------------|---------------|
| **Model** | `qwen3.6-plus` (primary), `qwen3.6-flash` (cost-optimized) |
| **API** | OpenAI-compatible Chat Completions |
| **Thinking Mode** | Enabled for complex reasoning |
| **Function Calling** | 10+ custom tools registered |
| **Built-in Tools** | Web search, code interpreter |
| **Session Cache** | Automatic context caching |
| **Conversations API** | Multi-turn context management |
| **Structured Output** | JSON mode for data extraction |

## 🏆 Why This Wins

| Judging Criterion | Score Weight | How We Excel |
|------------------|--------------|-------------|
| **Technical Depth & Engineering** | 30% | Sophisticated multi-agent orchestration, MCP-ready, advanced error recovery, confidence scoring |
| **Innovation & AI Creativity** | 30% | Novel autonomous task decomposition, self-healing workflows, intelligent memory management |
| **Problem Value & Impact** | 25% | Solves real enterprise automation pain, production-ready architecture, immediate business value |
| **Presentation & Documentation** | 15% | Clear architecture, comprehensive API docs, live dashboard, video demo |

## 🔗 Submission Requirements

- **Track**: Track 4: Autopilot Agent
- **Code Repository**: This repository (public, MIT license)
- **Architecture Diagram**: See [docs/architecture.md](docs/architecture.md)
- **Alibaba Cloud Proof**: See [backend/app/alibaba_cloud_deployment.py](backend/app/alibaba_cloud_deployment.py) and `/api/v1/alibaba-cloud-proof` endpoint
- **Demo Video**: [YouTube Link - to be added]
- **Blog Post**: [Link - to be added]

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [Qwen Cloud](https://www.qwencloud.com) for the AI platform
- [Alibaba Cloud](https://www.alibabacloud.com) for cloud infrastructure
- [Devpost](https://qwencloud-hackathon.devpost.com) for the hackathon platform
