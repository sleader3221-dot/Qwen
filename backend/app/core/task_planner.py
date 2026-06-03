import json
import logging
from typing import List, Dict, Optional

from app.services.qwen_service import qwen_service

logger = logging.getLogger(__name__)


class TaskPlanner:
    def __init__(self):
        self.system_prompt = """You are an advanced AI task planner for an Enterprise Autopilot Agent system.
Your role is to decompose complex business workflows into atomic, executable steps."""

    def create_plan(self, task_description: str, context: Optional[Dict] = None) -> List[Dict]:
        messages = [{"role": "user", "content": f"""Decompose this business task into a detailed execution plan:

Task: {task_description}

Return a JSON array of steps. Each step must have:
- step_type: the type of action
- description: what this step does
- agent_type: which agent handles it
- requires_human: boolean
- depends_on: list of step indices
- fallback_strategy: retry, skip, abort, or alternative

Be specific. Aim for 3-10 steps."""}]

        response = qwen_service.chat_completion(
            messages=messages,
            system_prompt=self.system_prompt,
            temperature=0.2,
            enable_thinking=True,
            response_format={"type": "json_object"},
        )

        try:
            content = response.get("content", "{}")
            if content.startswith("```"):
                content = content.strip("`").strip()
                if content.startswith("json"):
                    content = content[4:].strip()
            plan = json.loads(content)
            if isinstance(plan, dict) and "steps" in plan:
                return plan["steps"]
            if isinstance(plan, list):
                return plan
            return [{"step_type": "direct", "description": task_description, "agent_type": "orchestrator", "requires_human": False, "depends_on": [], "fallback_strategy": "abort"}]
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse plan: {e}")
            return [{"step_type": "direct", "description": task_description, "agent_type": "orchestrator", "requires_human": False, "depends_on": [], "fallback_strategy": "abort"}]


task_planner = TaskPlanner()
