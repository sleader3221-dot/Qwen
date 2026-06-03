import logging
import asyncio
from typing import Optional, Callable, Awaitable, Any
from datetime import datetime

from app.config import settings

logger = logging.getLogger(__name__)


class ErrorHandler:
    def __init__(self):
        self.retry_count = 0
        self.max_retries = settings.max_retry_attempts

    async def execute_with_retry(
        self,
        func: Callable[..., Awaitable[Any]],
        *args,
        fallback_func: Optional[Callable[..., Awaitable[Any]]] = None,
        **kwargs,
    ) -> Any:
        last_error = None

        for attempt in range(1, self.max_retries + 2):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                last_error = e
                self.retry_count += 1
                logger.warning(f"Attempt {attempt}/{self.max_retries + 1} failed: {str(e)}")

                if attempt <= self.max_retries:
                    wait_time = min(2 ** attempt * 0.5, 30)
                    logger.info(f"Retrying in {wait_time:.1f}s...")
                    await asyncio.sleep(wait_time)
                elif fallback_func:
                    logger.info(f"Executing fallback after {attempt} failures")
                    try:
                        return await fallback_func(*args, **kwargs)
                    except Exception as fb_e:
                        logger.error(f"Fallback also failed: {str(fb_e)}")
                        raise fb_e

        raise last_error

    @staticmethod
    def classify_error(error: Exception) -> str:
        error_str = str(error).lower()

        if "rate limit" in error_str or "429" in error_str:
            return "rate_limit"
        if "timeout" in error_str or "timed out" in error_str:
            return "timeout"
        if "auth" in error_str or "unauthorized" in error_str or "401" in error_str:
            return "authentication"
        if "not found" in error_str or "404" in error_str:
            return "not_found"
        if "quota" in error_str or "insufficient" in error_str:
            return "quota_exceeded"
        if "invalid" in error_str or "bad request" in error_str or "400" in error_str:
            return "invalid_request"
        if "server error" in error_str or "500" in error_str:
            return "server_error"
        if "context length" in error_str or "context window" in error_str:
            return "context_overflow"

        return "unknown"

    @staticmethod
    def get_recovery_strategy(error_class: str) -> str:
        strategies = {
            "rate_limit": "BACKOFF",
            "timeout": "RETRY_SMALLER",
            "authentication": "FAIL_FAST",
            "not_found": "FAIL_FAST",
            "quota_exceeded": "PAUSE_AND_RETRY",
            "invalid_request": "FAIL_FAST",
            "server_error": "RETRY",
            "context_overflow": "SUMMARIZE_AND_RETRY",
            "unknown": "RETRY_ONCE",
        }
        return strategies.get(error_class, "FAIL_FAST")


error_handler = ErrorHandler()
