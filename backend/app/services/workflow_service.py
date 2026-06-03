import json
import logging
from typing import Optional, Dict, Any, Generator
from datetime import datetime

from app.db.models import Workflow, WorkflowStatus
from app.db.session import SessionLocal
from app.core.orchestrator import orchestrator
from app.config import settings

logger = logging.getLogger(__name__)


class WorkflowService:
    def create_workflow(
        self,
        name: str,
        task: str,
        created_by: str = "system",
        agent_type: Optional[str] = None,
        tags: Optional[list] = None,
    ) -> Workflow:
        session = SessionLocal()
        try:
            workflow = Workflow(
                name=name,
                description=f"Autonomous workflow: {task[:200]}",
                status=WorkflowStatus.PENDING.value,
                input_data={"task": task},
                created_by=created_by,
                agent_type=agent_type or "orchestrator",
                tags=tags or [],
            )
            session.add(workflow)
            session.commit()
            session.refresh(workflow)
            logger.info(f"Workflow created: {workflow.id} - {name}")
            return workflow
        finally:
            session.close()

    def run_workflow(self, workflow_id: str) -> Generator[Dict, None, None]:
        session = SessionLocal()
        try:
            workflow = session.query(Workflow).filter(Workflow.id == workflow_id).first()
            if not workflow:
                yield {"type": "error", "message": "Workflow not found"}
                return
        finally:
            session.close()

        for event in orchestrator.execute_workflow(workflow):
            yield event

    def get_workflow(self, workflow_id: str) -> Optional[Dict]:
        return orchestrator.get_workflow_status(workflow_id)

    def list_workflows(self, status: Optional[str] = None, limit: int = 20, offset: int = 0) -> Dict:
        session = SessionLocal()
        try:
            query = session.query(Workflow).order_by(Workflow.created_at.desc())
            if status:
                query = query.filter(Workflow.status == status)
            total = query.count()
            workflows = query.offset(offset).limit(limit).all()

            return {
                "total": total,
                "limit": limit,
                "offset": offset,
                "workflows": [
                    {
                        "id": w.id,
                        "name": w.name,
                        "status": w.status,
                        "progress": f"{w.completed_steps}/{w.total_steps}",
                        "confidence": w.confidence_score,
                        "total_tokens": w.total_tokens_used,
                        "error": w.error_message,
                        "created_at": w.created_at.isoformat() if w.created_at else None,
                        "completed_at": w.completed_at.isoformat() if w.completed_at else None,
                        "tags": w.tags,
                        "human_interventions": w.human_intervention_count,
                    }
                    for w in workflows
                ],
            }
        finally:
            session.close()

    def cancel_workflow(self, workflow_id: str) -> bool:
        return orchestrator.cancel_workflow(workflow_id)

    def approve_human_step(self, workflow_id: str, step_order: int, approved: bool, feedback: Optional[str] = None) -> bool:
        return orchestrator.approve_step(workflow_id, step_order, approved, feedback)

    def get_token_usage(self) -> Dict:
        from app.services.qwen_service import qwen_service
        return qwen_service.check_token_budget()

    def get_analytics(self) -> Dict:
        session = SessionLocal()
        try:
            all_wf = session.query(Workflow).all()
            total = len(all_wf)
            completed = sum(1 for w in all_wf if w.status == WorkflowStatus.COMPLETED.value)
            failed = sum(1 for w in all_wf if w.status == WorkflowStatus.FAILED.value)
            running = sum(1 for w in all_wf if w.status == WorkflowStatus.RUNNING.value)
            awaiting_human = sum(1 for w in all_wf if w.status == WorkflowStatus.AWAITING_HUMAN.value)

            total_tokens = sum(w.total_tokens_used or 0 for w in all_wf)
            total_steps = sum(w.total_steps or 0 for w in all_wf)
            total_completed_steps = sum(w.completed_steps or 0 for w in all_wf)
            total_human_interventions = sum(w.human_intervention_count or 0 for w in all_wf)

            avg_confidence = 0.0
            confident_wfs = [w for w in all_wf if w.confidence_score is not None]
            if confident_wfs:
                avg_confidence = sum(w.confidence_score for w in confident_wfs) / len(confident_wfs)

            return {
                "total_workflows": total,
                "completed": completed,
                "failed": failed,
                "running": running,
                "awaiting_human": awaiting_human,
                "success_rate": round(completed / max(total, 1) * 100, 2),
                "total_tokens_used": total_tokens,
                "total_steps_executed": total_completed_steps,
                "total_human_interventions": total_human_interventions,
                "avg_confidence": round(avg_confidence, 4),
                "avg_steps_per_workflow": round(total_steps / max(total, 1), 1),
            }
        finally:
            session.close()


workflow_service = WorkflowService()
