import logging
import time
from typing import Callable
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        try:
            response = await call_next(request)
            duration = time.time() - start
            logger.info(f"{request.method} {request.url.path} - {response.status_code} - {duration:.3f}s")
            response.headers["X-Process-Time"] = str(duration)
            return response
        except Exception as e:
            duration = time.time() - start
            logger.error(f"{request.method} {request.url.path} - ERROR - {duration:.3f}s - {str(e)}")
            raise


class MetricsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.request_count = 0
        self.error_count = 0

    async def dispatch(self, request: Request, call_next):
        self.request_count += 1
        try:
            response = await call_next(request)
            if response.status_code >= 400:
                self.error_count += 1
            response.headers["X-Request-Id"] = str(self.request_count)
            return response
        except Exception:
            self.error_count += 1
            raise
