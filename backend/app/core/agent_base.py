import json
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from app.services.qwen_service import qwen_service
from app.core.memory_system import MemorySystem
from app.core.tool_registry import ToolRegistry
from app.db.models import Workflow, WorkflowStep, WorkflowStatus
from app.db.session import SessionLocal
from app.core.confidence_scorer import ConfidenceScorer

logger = logging.getLogger(__name__)


class BaseAgent:
    name: str = "base"
    description: str = ""
    system_prompt: str = ""
    tools: list = None

    def __init__(self):
        self.memory = MemorySystem(self.name)
        self.confidence_scorer = ConfidenceScorer()
        self.tools = self.tools or []

    def process(self, workflow: Workflow, input_data: Any, context: Optional[Dict] = None) -> Dict:
        raise NotImplementedError

    def _call_qwen(
        self,
        messages: list,
        temperature: float = 0.1,
        max_tokens: int = 4096,
        enable_thinking: bool = None,
        enable_search: bool = None,
        tools: list = None,
        response_format: dict = None,
    ) -> dict:
        all_tools = (self.tools or []) + (tools or [])
        openai_tools = []
        for t in all_tools:
            if hasattr(t, "to_openai_tool"):
                openai_tools.append(t.to_openai_tool())
            elif isinstance(t, dict):
                openai_tools.append(t)

        return qwen_service.chat_completion(
            messages=messages,
            system_prompt=self.system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            enable_thinking=enable_thinking,
            enable_search=enable_search,
            tools=openai_tools if openai_tools else None,
            response_format=response_format,
        )

    def _create_step(self, workflow_id: str, step_type: str, input_data: Any, order: int) -> WorkflowStep:
        session = SessionLocal()
        try:
            step = WorkflowStep(
                workflow_id=workflow_id,
                step_order=order,
                step_type=step_type,
                agent_type=self.name,
                status="running",
                input_data=input_data if isinstance(input_data, dict) else {"data": str(input_data)},
                started_at=datetime.utcnow(),
            )
            session.add(step)
            session.commit()
            session.refresh(step)
            return step
        finally:
            session.close()

    def _complete_step(self, step_id: str, output: Any, confidence: float = None, tokens: int = 0):
        session = SessionLocal()
        try:
            step = session.query(WorkflowStep).filter(WorkflowStep.id == step_id).first()
            if step:
                step.status = "completed"
                step.output_data = output if isinstance(output, dict) else {"data": str(output)}
                step.completed_at = datetime.utcnow()
                step.confidence_score = confidence
                step.tokens_used = tokens
                session.commit()
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

    def _needs_human(self, step: WorkflowStep, reason: str) -> bool:
        from app.config import settings
        if not settings.enable_human_in_loop:
            return False
        session = SessionLocal()
        try:
            s = session.query(WorkflowStep).filter(WorkflowStep.id == step.id).first()
            if s:
                s.requires_human = True
                s.status = "awaiting_human"
                s.step_metadata = {**(s.step_metadata or {}), "human_reason": reason}
                session.commit()
            return True
        finally:
            session.close()
