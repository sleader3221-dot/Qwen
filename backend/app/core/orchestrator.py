import json
import logging
import time
from typing import Optional, Dict, Any, List, Generator
from datetime import datetime

from app.config import settings
from app.services.qwen_service import qwen_service
from app.core.task_planner import task_planner
from app.core.confidence_scorer import ConfidenceScorer
from app.core.error_handler import error_handler
from app.core.memory_system import MemorySystem
from app.db.models import Workflow, WorkflowStep, WorkflowStatus
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)


class WorkflowOrchestrator:
    def __init__(self):
        self.memory = MemorySystem("orchestrator")
        self.confidence_scorer = ConfidenceScorer()
        self.agent_map = self._init_agents()

    def _init_agents(self):
        from app.agents import EmailAgent, DocumentAgent, SchedulerAgent, CRMAgent, DataAgent, NotificationAgent, CodeReviewAgent, ReportAgent
        return {
            "email_agent": EmailAgent(),
            "document_agent": DocumentAgent(),
            "scheduler_agent": SchedulerAgent(),
            "crm_agent": CRMAgent(),
            "data_agent": DataAgent(),
            "notification_agent": NotificationAgent(),
            "code_review_agent": CodeReviewAgent(),
            "report_agent": ReportAgent(),
            "orchestrator": self,
        }

    def execute_workflow(self, workflow: Workflow) -> Generator[Dict, None, None]:
        try:
            session = SessionLocal()
            try:
                db_wf = session.query(Workflow).filter(Workflow.id == workflow.id).first()
                db_wf.status = WorkflowStatus.RUNNING.value
                db_wf.total_tokens_used = 0
                session.commit()
                workflow = db_wf
            finally:
                session.close()

            plan = task_planner.create_plan(workflow.input_data.get("task", ""), workflow.input_data)
            workflow.total_steps = len(plan)

            session = SessionLocal()
            try:
                db_wf = session.query(Workflow).filter(Workflow.id == workflow.id).first()
                db_wf.total_steps = len(plan)
                session.commit()
            finally:
                session.close()

            yield {"type": "plan_created", "plan": plan, "total_steps": len(plan)}

            context_summary = self.memory.get_context_summary()
            step_results = {}
            workflow.human_intervention_count = 0

            for i, step_def in enumerate(plan):
                session = SessionLocal()
                try:
                    db_wf = session.query(Workflow).filter(Workflow.id == workflow.id).first()
                    if db_wf.status == WorkflowStatus.CANCELLED.value:
                        workflow.status = db_wf.status
                        break
                finally:
                    session.close()

                step = self._create_step(workflow.id, step_def, i)

                yield {"type": "step_started", "step_index": i, "step": step_def}

                try:
                    result = self._execute_step(workflow, step, step_def, context_summary)
                    step_results[str(i)] = result

                    if isinstance(result, dict) and result.get("status") == "awaiting_human":
                        session = SessionLocal()
                        try:
                            db_wf = session.query(Workflow).filter(Workflow.id == workflow.id).first()
                            db_wf.status = WorkflowStatus.AWAITING_HUMAN.value
                            db_wf.human_intervention_count = (db_wf.human_intervention_count or 0) + 1
                            session.commit()
                        finally:
                            session.close()
                        yield {"type": "waiting_human", "step_index": i, "reason": result.get("reason", "")}

                    if isinstance(result, dict) and "tokens_used" in result:
                        session = SessionLocal()
                        try:
                            db_wf = session.query(Workflow).filter(Workflow.id == workflow.id).first()
                            db_wf.total_tokens_used = (db_wf.total_tokens_used or 0) + result["tokens_used"]
                            session.commit()
                        finally:
                            session.close()

                    yield {"type": "step_completed", "step_index": i, "result": result}

                except Exception as e:
                    logger.error(f"Step {i} failed: {str(e)}")
                    self._fail_step(step.id, str(e))
                    yield {"type": "step_failed", "step_index": i, "error": str(e)}

                    fallback = step_def.get("fallback_strategy", "abort")
                    if fallback == "abort":
                        session = SessionLocal()
                        try:
                            db_wf = session.query(Workflow).filter(Workflow.id == workflow.id).first()
                            db_wf.status = WorkflowStatus.FAILED.value
                            db_wf.error_message = f"Step {i} failed: {str(e)}"
                            session.commit()
                        finally:
                            session.close()
                        yield {"type": "workflow_failed", "error": db_wf.error_message if 'db_wf' in dir() else str(e)}
                        return
                    elif fallback == "skip":
                        continue
                    elif fallback == "alternative":
                        alt_result = self._execute_fallback(step_def, e, context_summary)
                        step_results[str(i)] = alt_result
                        yield {"type": "step_fallback_completed", "step_index": i, "result": alt_result}

            session = SessionLocal()
            try:
                db_wf = session.query(Workflow).filter(Workflow.id == workflow.id).first()
                db_wf.status = WorkflowStatus.COMPLETED.value
                db_wf.completed_at = datetime.utcnow()
                db_wf.output_data = self._synthesize_output(workflow, step_results)
                session.commit()
            finally:
                session.close()

            self.memory.store(
                key=f"workflow_{workflow.id}",
                value={
                    "task": workflow.input_data.get("task", ""),
                    "status": workflow.status,
                    "success_rate": len([r for r in step_results.values() if isinstance(r, dict) and r.get("status") == "completed"]) / max(len(step_results), 1),
                    "total_steps": len(step_results),
                },
                context={"workflow_type": workflow.agent_type},
                importance=0.6,
            )

            session = SessionLocal()
            try:
                db_wf = session.query(Workflow).filter(Workflow.id == workflow.id).first()
                yield {
                    "type": "workflow_completed",
                    "output": db_wf.output_data if db_wf else workflow.output_data,
                    "total_tokens": db_wf.total_tokens_used if db_wf else 0,
                }
            finally:
                session.close()

        except Exception as e:
            logger.error(f"Workflow execution failed: {str(e)}")
            session = SessionLocal()
            try:
                db_wf = session.query(Workflow).filter(Workflow.id == workflow.id).first()
                if db_wf:
                    db_wf.status = WorkflowStatus.FAILED.value
                    db_wf.error_message = str(e)
                    session.commit()
            finally:
                session.close()
            yield {"type": "workflow_failed", "error": str(e)}

    def _execute_step(self, workflow: Workflow, step: WorkflowStep, step_def: Dict, context: str) -> Dict:
        agent_type = step_def.get("agent_type", "orchestrator")
        agent = self.agent_map.get(agent_type)

        if not agent:
            agent = self

        input_data = {
            "task": step_def.get("description", ""),
            "workflow_id": workflow.id,
            "workflow_input": workflow.input_data,
            "step_input": step_def.get("input_schema", {}),
            "context": context,
        }

        result = agent.process(workflow, input_data)
        if isinstance(result, dict):
            confidence = result.get("confidence", 0.5)
            if self.confidence_scorer.needs_human_review(confidence):
                session = SessionLocal()
                try:
                    s = session.query(WorkflowStep).filter(WorkflowStep.id == step.id).first()
                    if s:
                        s.requires_human = True
                        s.status = "awaiting_human"
                        s.step_metadata = {**(s.step_metadata or {}), "confidence": confidence, "human_reason": f"Low confidence: {confidence:.2f}"}
                        session.commit()
                finally:
                    session.close()
                return {"status": "awaiting_human", "reason": f"Confidence {confidence:.2f} below threshold", "agent_result": result}

            tokens_used = result.get("tokens_used", 0)
            session = SessionLocal()
            try:
                s = session.query(WorkflowStep).filter(WorkflowStep.id == step.id).first()
                if s:
                    s.status = "completed"
                    s.output_data = result
                    s.completed_at = datetime.utcnow()
                    s.confidence_score = confidence
                    s.tokens_used = tokens_used
                    session.commit()
            finally:
                session.close()
            return {"status": "completed", "data": result, "tokens_used": tokens_used, "confidence": confidence}

        return {"status": "completed", "data": {"content": str(result)}}

    def _execute_fallback(self, step_def: Dict, error: Exception, context: str) -> Dict:
        try:
            messages = [{
                "role": "user",
                "content": f"The planned step '{step_def.get('description')}' failed with: {str(error)}.\nSuggest an alternative approach to accomplish the same goal."
            }]
            response = qwen_service.chat_completion(
                messages=messages,
                system_prompt="You are a fallback planner. Suggest alternative approaches when a planned step fails.",
                temperature=0.3,
            )
            return {"status": "fallback_completed", "alternative": response.get("content", ""), "tokens_used": response.get("usage", {}).get("total_tokens", 0)}
        except Exception as e:
            return {"status": "fallback_failed", "error": str(e)}

    def _synthesize_output(self, workflow: Workflow, step_results: Dict) -> Dict:
        try:
            messages = [{
                "role": "user",
                "content": f"Task: {workflow.input_data.get('task', '')}\n\nStep results:\n{json.dumps(step_results, indent=2, default=str)}\n\nSynthesize a final comprehensive output summarizing what was accomplished."
            }]
            response = qwen_service.chat_completion(
                messages=messages,
                system_prompt="Synthesize the final output from all workflow step results into a clear, actionable summary.",
                temperature=0.2,
            )
            return {"summary": response.get("content", ""), "steps_completed": len(step_results), "steps": step_results}
        except Exception:
            return {"summary": "Workflow completed", "steps": step_results}

    def _create_step(self, workflow_id: str, step_def: Dict, index: int) -> WorkflowStep:
        session = SessionLocal()
        try:
            step = WorkflowStep(
                workflow_id=workflow_id,
                step_order=index,
                step_type=step_def.get("step_type", "task"),
                agent_type=step_def.get("agent_type", "orchestrator"),
                status="running",
                input_data=step_def,
                started_at=datetime.utcnow(),
                requires_human=step_def.get("requires_human", False),
            )
            session.add(step)
            session.commit()
            session.refresh(step)
            return step
        finally:
            session.close()

    def _fail_step(self, step_id: str, error: str):
        session = SessionLocal()
        try:
            step = session.query(WorkflowStep).filter(WorkflowStep.id == step_id).first()
            if step:
                step.status = "failed"
                step.error_message = str(error)
                step.completed_at = datetime.utcnow()
                session.commit()
        finally:
            session.close()

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict]:
        session = SessionLocal()
        try:
            wf = session.query(Workflow).filter(Workflow.id == workflow_id).first()
            if not wf:
                return None
            steps = session.query(WorkflowStep).filter(
                WorkflowStep.workflow_id == workflow_id
            ).order_by(WorkflowStep.step_order).all()
            return {
                "id": wf.id,
                "name": wf.name,
                "status": wf.status,
                "confidence": wf.confidence_score,
                "progress": f"{wf.completed_steps}/{wf.total_steps}",
                "total_tokens": wf.total_tokens_used,
                "human_interventions": wf.human_intervention_count,
                "error": wf.error_message,
                "steps": [
                    {
                        "order": s.step_order,
                        "type": s.step_type,
                        "agent": s.agent_type,
                        "status": s.status,
                        "confidence": s.confidence_score,
                        "requires_human": s.requires_human,
                        "human_approved": s.human_approved,
                        "error": s.error_message,
                    }
                    for s in steps
                ],
                "created_at": wf.created_at.isoformat() if wf.created_at else None,
                "completed_at": wf.completed_at.isoformat() if wf.completed_at else None,
            }
        finally:
            session.close()

    def cancel_workflow(self, workflow_id: str) -> bool:
        session = SessionLocal()
        try:
            wf = session.query(Workflow).filter(Workflow.id == workflow_id).first()
            if wf and wf.status in (WorkflowStatus.RUNNING.value, WorkflowStatus.AWAITING_HUMAN.value, WorkflowStatus.PENDING.value):
                wf.status = WorkflowStatus.CANCELLED.value
                session.commit()
                return True
            return False
        finally:
            session.close()

    def approve_step(self, workflow_id: str, step_order: int, approved: bool, feedback: Optional[str] = None) -> bool:
        session = SessionLocal()
        try:
            step = session.query(WorkflowStep).filter(
                WorkflowStep.workflow_id == workflow_id,
                WorkflowStep.step_order == step_order,
            ).first()
            if step and step.status == "awaiting_human":
                step.human_approved = approved
                step.status = "running" if approved else "cancelled"
                step.step_metadata = {**(step.step_metadata or {}), "human_feedback": feedback}
                session.commit()
                if approved:
                    wf = session.query(Workflow).filter(Workflow.id == workflow_id).first()
                    if wf:
                        wf.status = WorkflowStatus.RUNNING.value
                        session.commit()
                return True
            return False
        finally:
            session.close()

    def process(self, workflow: Workflow, input_data: Dict) -> Dict:
        result = self._call_qwen(
            messages=[{"role": "user", "content": json.dumps(input_data)}],
            enable_thinking=True,
        )
        confidence = self.confidence_scorer.score(result, "orchestration", {"input": input_data})
        result["confidence"] = confidence
        return result

    def _call_qwen(self, messages, **kwargs):
        return qwen_service.chat_completion(messages=messages, **kwargs)


orchestrator = WorkflowOrchestrator()
