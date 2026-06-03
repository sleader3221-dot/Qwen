import sys
import os
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
_backend = _root / "backend"
if str(_backend) not in sys.path:
    sys.path.insert(0, str(_backend))

os.environ.setdefault("DATABASE_URL", "sqlite:////tmp/autopilot.db")
os.environ.setdefault("DASHSCOPE_API_KEY", "sk-placeholder-for-vercel")
os.environ.setdefault("ENABLE_THINKING_MODE", "True")
os.environ.setdefault("ENABLE_WEB_SEARCH", "True")
os.environ.setdefault("ENABLE_CODE_INTERPRETER", "True")
os.environ.setdefault("ENABLE_MCP_INTEGRATION", "True")
os.environ.setdefault("ENABLE_HUMAN_IN_LOOP", "True")
os.environ.setdefault("CONFIDENCE_THRESHOLD", "0.85")
os.environ.setdefault("MAX_RETRY_ATTEMPTS", "3")
os.environ.setdefault("WORKFLOW_TIMEOUT_SECONDS", "60")
os.environ.setdefault("TOKEN_BUDGET_DAILY", "1000000")
os.environ.setdefault("QWEN_MODEL", "qwen3.6-plus")
os.environ.setdefault("SECRET_KEY", "change-this-in-vercel-dashboard")

from app.main import app
