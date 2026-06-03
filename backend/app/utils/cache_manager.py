import json
import logging
import hashlib
from typing import Optional, Any, Dict
from datetime import datetime, timedelta

from app.db.models import ConversationCache
from app.db.session import async_session
from sqlalchemy import select

logger = logging.getLogger(__name__)


class CacheManager:
    def __init__(self):
        self.default_ttl = 3600

    def _make_key(self, prefix: str, data: Any) -> str:
        raw = f"{prefix}:{json.dumps(data, sort_keys=True, default=str)}"
        return hashlib.sha256(raw.encode()).hexdigest()

    async def get(self, prefix: str, data: Any) -> Optional[Dict]:
        key = self._make_key(prefix, data)
        async with async_session() as session:
            result = await session.execute(
                select(ConversationCache).where(ConversationCache.id == key)
            )
            cache = result.scalar_one_or_none()
            if cache and cache.expires_at and cache.expires_at < datetime.utcnow():
                await session.delete(cache)
                await session.commit()
                return None
            if cache:
                return cache.messages if isinstance(cache.messages, dict) else {"data": cache.messages}
            return None

    async def set(self, prefix: str, data: Any, value: Any, ttl: Optional[int] = None):
        key = self._make_key(prefix, data)
        async with async_session() as session:
            cache = ConversationCache(
                id=key,
                session_id=f"{prefix}_{key[:16]}",
                messages=value if isinstance(value, (dict, list)) else {"data": value},
                context_summary=str(value)[:500],
                expires_at=datetime.utcnow() + timedelta(seconds=ttl or self.default_ttl),
                token_count=len(str(value)),
            )
            session.add(cache)
            await session.commit()

    async def invalidate(self, prefix: str, data: Any):
        key = self._make_key(prefix, data)
        async with async_session() as session:
            result = await session.execute(
                select(ConversationCache).where(ConversationCache.id == key)
            )
            cache = result.scalar_one_or_none()
            if cache:
                await session.delete(cache)
                await session.commit()


cache_manager = CacheManager()
