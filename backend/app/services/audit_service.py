import logging
from typing import Optional, Dict
from datetime import datetime

from app.db.models import AuditLog
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)


class AuditService:
    @staticmethod
    def log(
        action: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        actor: Optional[str] = None,
        details: Optional[Dict] = None,
        severity: str = "info",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> str:
        session = SessionLocal()
        try:
            audit = AuditLog(
                workflow_id=workflow_id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                actor=actor,
                details=details or {},
                severity=severity,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            session.add(audit)
            session.commit()
            session.refresh(audit)
            return audit.id
        finally:
            session.close()

    @staticmethod
    def get_logs(
        workflow_id: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> Dict:
        session = SessionLocal()
        try:
            query = session.query(AuditLog).order_by(AuditLog.created_at.desc())
            if workflow_id:
                query = query.filter(AuditLog.workflow_id == workflow_id)
            if action:
                query = query.filter(AuditLog.action == action)
            total = query.count()
            logs = query.offset(offset).limit(limit).all()

            return {
                "total": total,
                "limit": limit,
                "offset": offset,
                "logs": [
                    {
                        "id": log.id,
                        "action": log.action,
                        "entity_type": log.entity_type,
                        "entity_id": log.entity_id,
                        "workflow_id": log.workflow_id,
                        "actor": log.actor,
                        "details": log.details,
                        "severity": log.severity,
                        "created_at": log.created_at.isoformat() if log.created_at else None,
                    }
                    for log in logs
                ],
            }
        finally:
            session.close()


audit_service = AuditService()
