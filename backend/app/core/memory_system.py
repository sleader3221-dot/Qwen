import json
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy import desc, and_

from app.db.models import AgentMemory
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)


class MemorySystem:
    def __init__(self, agent_type: str):
        self.agent_type = agent_type

    def store(
        self,
        key: str,
        value: Any,
        context: Optional[Dict] = None,
        importance: float = 0.5,
        ttl_seconds: Optional[int] = None,
    ) -> str:
        session = SessionLocal()
        try:
            memory = AgentMemory(
                agent_type=self.agent_type,
                memory_key=key,
                memory_value=value if isinstance(value, dict) else {"data": value},
                context=context or {},
                importance_score=importance,
                expires_at=datetime.utcnow() + timedelta(seconds=ttl_seconds) if ttl_seconds else None,
                ttl_seconds=ttl_seconds,
            )
            session.add(memory)
            session.commit()
            logger.info(f"Memory stored: {self.agent_type}/{key}")
            return memory.id
        finally:
            session.close()

    def retrieve(self, key: str) -> Optional[Dict]:
        session = SessionLocal()
        try:
            memory = session.query(AgentMemory).filter(
                AgentMemory.agent_type == self.agent_type,
                AgentMemory.memory_key == key,
            ).order_by(desc(AgentMemory.created_at)).first()
            if memory:
                if memory.expires_at and memory.expires_at < datetime.utcnow():
                    session.delete(memory)
                    session.commit()
                    return None
                memory.access_count += 1
                memory.last_accessed_at = datetime.utcnow()
                session.commit()
                return {
                    "id": memory.id,
                    "key": memory.memory_key,
                    "value": memory.memory_value,
                    "context": memory.context,
                    "importance": memory.importance_score,
                    "created_at": memory.created_at.isoformat(),
                    "access_count": memory.access_count,
                }
            return None
        finally:
            session.close()

    def search(self, query: str, limit: int = 10) -> List[Dict]:
        session = SessionLocal()
        try:
            memories = session.query(AgentMemory).filter(
                AgentMemory.agent_type == self.agent_type
            ).order_by(
                desc(AgentMemory.importance_score),
                desc(AgentMemory.last_accessed_at)
            ).limit(limit).all()
            return [
                {
                    "id": m.id,
                    "key": m.memory_key,
                    "value": m.memory_value,
                    "context": m.context,
                    "importance": m.importance_score,
                    "created_at": m.created_at.isoformat(),
                    "access_count": m.access_count,
                }
                for m in memories
                if not (m.expires_at and m.expires_at < datetime.utcnow())
            ]
        finally:
            session.close()

    def forget(self, key: str) -> bool:
        session = SessionLocal()
        try:
            memory = session.query(AgentMemory).filter(
                AgentMemory.agent_type == self.agent_type,
                AgentMemory.memory_key == key,
            ).first()
            if memory:
                session.delete(memory)
                session.commit()
                return True
            return False
        finally:
            session.close()

    def forget_old(self, max_age_hours: int = 72) -> int:
        session = SessionLocal()
        try:
            cutoff = datetime.utcnow() - timedelta(hours=max_age_hours)
            memories = session.query(AgentMemory).filter(
                AgentMemory.agent_type == self.agent_type,
                AgentMemory.created_at < cutoff,
                AgentMemory.importance_score < 0.3,
            ).all()
            for m in memories:
                session.delete(m)
            session.commit()
            logger.info(f"Forgot {len(memories)} old memories for {self.agent_type}")
            return len(memories)
        finally:
            session.close()

    def get_context_summary(self, limit: int = 5) -> str:
        memories = self.search("", limit=limit)
        if not memories:
            return ""
        lines = []
        for m in memories:
            val = m["value"]
            if isinstance(val, dict):
                val_str = json.dumps(val, ensure_ascii=False)[:200]
            else:
                val_str = str(val)[:200]
            lines.append(f"- [{m['importance']:.1f}] {m['key']}: {val_str}")
        return "Previous context:\n" + "\n".join(lines)
