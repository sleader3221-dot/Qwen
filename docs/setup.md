# Enterprise AI Autopilot - Setup Guide

## Prerequisites

- Python 3.12+
- Node.js 20+
- Docker & Docker Compose (optional, for containerized deployment)
- Alibaba Cloud / Qwen Cloud API Key

## Quick Start (Development)

### 1. Get Qwen Cloud API Key

1. Sign up at [Qwen Cloud](https://www.qwencloud.com)
2. Navigate to API Keys section
3. Generate a new API key (format: `sk-xxx`)
4. Request hackathon credits via the coupon form

### 2. Backend Setup

```bash
# Clone the repository
cd enterprise-autopilot-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and set your DASHSCOPE_API_KEY

# Run the server
cd backend
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/api/v1/health

## Docker Deployment

```bash
docker-compose up -d
```

## Seeding Sample Data

```bash
cd scripts
python seed_data.py
```

## Running Benchmarks

```bash
cd scripts
python benchmark.py
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DASHSCOPE_API_KEY` | Qwen Cloud API Key | Required |
| `QWEN_MODEL` | Model to use | `qwen3.6-plus` |
| `DATABASE_URL` | Database connection | `sqlite+aiosqlite:///./autopilot.db` |
| `REDIS_URL` | Redis connection | `redis://localhost:6379/0` |
| `SECRET_KEY` | JWT secret key | auto-generated |
| `ENABLE_THINKING_MODE` | Enable deep reasoning | `true` |
| `ENABLE_WEB_SEARCH` | Enable web search | `true` |
| `ENABLE_CODE_INTERPRETER` | Enable code execution | `true` |
| `ENABLE_HUMAN_IN_LOOP` | Enable human review | `true` |
| `CONFIDENCE_THRESHOLD` | Human review threshold | `0.85` |
| `TOKEN_BUDGET_DAILY` | Daily token limit | `1000000` |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| POST | `/api/v1/workflows` | Create workflow |
| GET | `/api/v1/workflows` | List workflows |
| GET | `/api/v1/workflows/{id}` | Get workflow details |
| POST | `/api/v1/workflows/{id}/run-sync` | Execute workflow (sync) |
| POST | `/api/v1/workflows/{id}/cancel` | Cancel workflow |
| POST | `/api/v1/workflows/{id}/approve` | Approve/reject human step |
| GET | `/api/v1/token-usage` | Get token usage stats |
| GET | `/api/v1/analytics/dashboard` | Dashboard analytics |
| GET | `/api/v1/analytics/timeline` | Workflow timeline |
| GET | `/api/v1/audit-logs` | Audit log trail |
| GET | `/api/v1/alibaba-cloud-proof` | Alibaba Cloud deployment proof |
| WS | `/ws/workflows/{id}` | Real-time workflow stream |
| WS | `/ws/dashboard` | Real-time dashboard updates |
