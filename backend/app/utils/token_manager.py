import logging
from typing import Dict
from app.config import settings

logger = logging.getLogger(__name__)


class TokenManager:
    def __init__(self):
        self.daily_budget = settings.token_budget_daily
        self.warning_threshold = 0.8
        self.critical_threshold = 0.95

    def check_budget(self, current_usage: int) -> Dict:
        usage_ratio = current_usage / max(self.daily_budget, 1)
        remaining = max(0, self.daily_budget - current_usage)

        status = "ok"
        if usage_ratio >= self.critical_threshold:
            status = "critical"
        elif usage_ratio >= self.warning_threshold:
            status = "warning"

        return {
            "status": status,
            "usage_ratio": round(usage_ratio, 4),
            "used": current_usage,
            "remaining": remaining,
            "budget": self.daily_budget,
        }

    def should_throttle(self, current_usage: int) -> bool:
        usage_ratio = current_usage / max(self.daily_budget, 1)
        return usage_ratio >= self.critical_threshold

    def estimate_tokens(self, text: str) -> int:
        return int(len(text) * 0.4) + 10


token_manager = TokenManager()
