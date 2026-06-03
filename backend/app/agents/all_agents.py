import json
import logging
from typing import Dict

from app.core.agent_base import BaseAgent

logger = logging.getLogger(__name__)


class EmailAgent(BaseAgent):
    name = "email_agent"
    description = "Handles email processing, classification, drafting, and response generation"
    system_prompt = "You are an Email Processing Agent. Classify, draft, and respond to emails."

    def process(self, workflow, input_data: Dict) -> Dict:
        messages = [{"role": "user", "content": json.dumps(input_data)}]
        response = self._call_qwen(messages=messages, temperature=0.1, enable_thinking=True)
        response["confidence"] = self.confidence_scorer.score(response, "email_processing", input_data)
        response["tokens_used"] = response.get("usage", {}).get("total_tokens", 0)
        return response


class DocumentAgent(BaseAgent):
    name = "document_agent"
    description = "Handles document parsing, generation, analysis, and format conversion"
    system_prompt = "You are a Document Processing Agent for an enterprise automation system. Parse and generate business documents."

    def process(self, workflow, input_data: Dict) -> Dict:
        messages = [{"role": "user", "content": json.dumps(input_data)}]
        response = self._call_qwen(messages=messages, temperature=0.1, enable_thinking=True)
        response["confidence"] = self.confidence_scorer.score(response, "document_processing", input_data)
        response["tokens_used"] = response.get("usage", {}).get("total_tokens", 0)
        return response


class SchedulerAgent(BaseAgent):
    name = "scheduler_agent"
    description = "Manages calendar operations, meeting scheduling, and time optimization"
    system_prompt = "You are a Scheduling Agent. Schedule meetings, find optimal times, manage conflicts."

    def process(self, workflow, input_data: Dict) -> Dict:
        messages = [{"role": "user", "content": json.dumps(input_data)}]
        response = self._call_qwen(messages=messages, temperature=0.1, enable_thinking=True)
        response["confidence"] = self.confidence_scorer.score(response, "scheduling", input_data)
        response["tokens_used"] = response.get("usage", {}).get("total_tokens", 0)
        return response


class CRMAgent(BaseAgent):
    name = "crm_agent"
    description = "Manages CRM operations, contact management, lead tracking, and pipeline optimization"
    system_prompt = "You are a CRM Agent. Manage contacts, leads, and sales pipeline."

    def process(self, workflow, input_data: Dict) -> Dict:
        messages = [{"role": "user", "content": json.dumps(input_data)}]
        response = self._call_qwen(messages=messages, temperature=0.1, enable_thinking=True)
        response["confidence"] = self.confidence_scorer.score(response, "crm_operation", input_data)
        response["tokens_used"] = response.get("usage", {}).get("total_tokens", 0)
        return response


class DataAgent(BaseAgent):
    name = "data_agent"
    description = "Handles data querying, analysis, visualization, and business intelligence"
    system_prompt = "You are a Data Analysis Agent. Query databases, analyze data, generate insights."

    def process(self, workflow, input_data: Dict) -> Dict:
        messages = [{"role": "user", "content": json.dumps(input_data)}]
        response = self._call_qwen(messages=messages, temperature=0.1, enable_thinking=True)
        response["confidence"] = self.confidence_scorer.score(response, "data_analysis", input_data)
        response["tokens_used"] = response.get("usage", {}).get("total_tokens", 0)
        return response


class NotificationAgent(BaseAgent):
    name = "notification_agent"
    description = "Manages multi-channel notifications via email, Slack, and webhooks"
    system_prompt = "You are a Notification Agent. Send notifications through multiple channels."

    def process(self, workflow, input_data: Dict) -> Dict:
        messages = [{"role": "user", "content": json.dumps(input_data)}]
        response = self._call_qwen(messages=messages, temperature=0.1, enable_thinking=True)
        response["confidence"] = self.confidence_scorer.score(response, "notification", input_data)
        response["tokens_used"] = response.get("usage", {}).get("total_tokens", 0)
        return response


class CodeReviewAgent(BaseAgent):
    name = "code_review_agent"
    description = "Automates code review, PR analysis, bug detection, and fix suggestions"
    system_prompt = "You are a Code Review Agent. Analyze code, detect bugs, suggest fixes."

    def process(self, workflow, input_data: Dict) -> Dict:
        messages = [{"role": "user", "content": json.dumps(input_data)}]
        response = self._call_qwen(messages=messages, temperature=0.1, enable_thinking=True)
        response["confidence"] = self.confidence_scorer.score(response, "code_review", input_data)
        response["tokens_used"] = response.get("usage", {}).get("total_tokens", 0)
        return response


class ReportAgent(BaseAgent):
    name = "report_agent"
    description = "Generates comprehensive business reports with visualizations and insights"
    system_prompt = "You are a Report Generation Agent. Generate business reports and dashboards."

    def process(self, workflow, input_data: Dict) -> Dict:
        messages = [{"role": "user", "content": json.dumps(input_data)}]
        response = self._call_qwen(messages=messages, temperature=0.1, enable_thinking=True)
        response["confidence"] = self.confidence_scorer.score(response, "report_generation", input_data)
        response["tokens_used"] = response.get("usage", {}).get("total_tokens", 0)
        return response
