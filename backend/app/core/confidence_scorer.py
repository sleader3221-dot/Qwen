import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class ConfidenceScorer:
    def __init__(self):
        self.default_threshold = 0.85

    def score(
        self,
        agent_response: Dict,
        task_type: str,
        context: Optional[Dict] = None,
    ) -> float:
        factors = []

        response_quality = self._assess_response_quality(agent_response)
        factors.append(("response_quality", response_quality, 0.30))

        task_complexity = self._assess_task_complexity(agent_response, task_type)
        factors.append(("task_complexity", task_complexity, 0.25))

        if context:
            context_confidence = self._assess_context_confidence(context)
            factors.append(("context", context_confidence, 0.20))

        tool_success = self._assess_tool_success(agent_response)
        if tool_success is not None:
            factors.append(("tool_success", tool_success, 0.25))

        weighted_score = sum(score * weight for _, score, weight in factors)
        total_weight = sum(weight for _, _, weight in factors)

        final_score = weighted_score / total_weight if total_weight > 0 else 0.5
        return round(max(0.0, min(1.0, final_score)), 4)

    def _assess_response_quality(self, response: Dict) -> float:
        score = 0.7
        content = response.get("content", "")
        finish_reason = response.get("finish_reason", "")

        if finish_reason == "stop":
            score += 0.15
        elif finish_reason == "length":
            score -= 0.15

        if content and len(content) > 20:
            score += 0.1
        if not content:
            score -= 0.3
        if "error" in content.lower()[:100]:
            score -= 0.2

        usage = response.get("usage", {})
        total_tokens = usage.get("total_tokens", 0)
        if total_tokens == 0:
            score -= 0.1

        return max(0.0, min(1.0, score))

    def _assess_task_complexity(self, response: Dict, task_type: str) -> float:
        score = 0.8
        content = response.get("content", "")

        complex_indicators = [
            "multiple steps", "first", "then", "finally",
            "scenario", "option", "alternative",
            "if", "when", "depending",
        ]
        simple_indicators = [
            "i cannot", "i don't know", "i'm not sure",
            "error", "failed", "unable",
        ]

        content_lower = content.lower()
        for indicator in simple_indicators:
            if indicator in content_lower:
                score -= 0.15
                break

        complex_count = sum(1 for ind in complex_indicators if ind in content_lower)
        if complex_count >= 3:
            score += 0.1

        return max(0.0, min(1.0, score))

    def _assess_context_confidence(self, context: Dict) -> float:
        score = 0.75
        prev_success = context.get("previous_step_success", None)
        similar_tasks = context.get("similar_tasks_completed", 0)

        if prev_success is False:
            score -= 0.2
        if prev_success is True:
            score += 0.1
        if similar_tasks > 5:
            score += 0.1
        elif similar_tasks > 0:
            score += 0.05

        return max(0.0, min(1.0, score))

    def _assess_tool_success(self, response: Dict) -> Optional[float]:
        tool_calls = response.get("tool_calls")
        if not tool_calls:
            return None

        score = 0.8
        error_in_args = sum(
            1 for tc in tool_calls
            if "error" in tc.get("function", {}).get("arguments", "").lower()
        )
        score -= error_in_args * 0.2

        return max(0.0, min(1.0, score))

    def needs_human_review(self, score: float, threshold: Optional[float] = None) -> bool:
        t = threshold or self.default_threshold
        from app.config import settings
        if not settings.enable_human_in_loop:
            return False
        return score < t
