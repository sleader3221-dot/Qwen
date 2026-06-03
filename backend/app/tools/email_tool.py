import json
import logging
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

from app.core.tool_registry import BaseTool, register_tool

logger = logging.getLogger(__name__)


@dataclass
class EmailToolConfig:
    sendgrid_api_key: Optional[str] = None
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_pass: Optional[str] = None
    default_from: str = "autopilot@enterprise.com"


@register_tool
class EmailTool(BaseTool):
    name = "send_email"
    description = "Send an email with specified recipients, subject, and body content"
    parameters = {
        "type": "object",
        "properties": {
            "to": {"type": "array", "items": {"type": "string"}, "description": "List of email recipients"},
            "cc": {"type": "array", "items": {"type": "string"}, "description": "List of CC recipients"},
            "bcc": {"type": "array", "items": {"type": "string"}, "description": "List of BCC recipients"},
            "subject": {"type": "string", "description": "Email subject line"},
            "body": {"type": "string", "description": "Email body content (HTML or plain text)"},
            "is_html": {"type": "boolean", "description": "Whether body is HTML"},
            "priority": {"type": "string", "enum": ["low", "normal", "high", "urgent"]},
            "attachments": {
                "type": "array",
                "items": {"type": "object", "properties": {
                    "filename": {"type": "string"},
                    "content": {"type": "string"},
                    "content_type": {"type": "string"},
                }},
            },
        },
        "required": ["to", "subject", "body"],
    }

    async def execute(self, **kwargs) -> Dict:
        logger.info(f"Sending email: {kwargs.get('subject', 'No subject')} to {kwargs.get('to', [])}")
        to = kwargs.get("to", [])
        subject = kwargs.get("subject", "")
        body = kwargs.get("body", "")

        result = {
            "status": "simulated",
            "message": f"Email would be sent to {len(to)} recipient(s)",
            "to": to,
            "subject": subject,
            "estimated_tokens": len(subject) + len(body),
        }

        if kwargs.get("priority") == "urgent":
            result["priority"] = "urgent"
            result["note"] = "Flagged for immediate delivery"

        return result


@register_tool
class EmailSearchTool(BaseTool):
    name = "search_emails"
    description = "Search through email history by query, sender, date range, or folder"
    parameters = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Search query"},
            "from_address": {"type": "string", "description": "Filter by sender email"},
            "max_results": {"type": "integer", "description": "Maximum results to return"},
            "folder": {"type": "string", "description": "Email folder to search"},
            "date_from": {"type": "string", "description": "Start date (ISO format)"},
            "date_to": {"type": "string", "description": "End date (ISO format)"},
        },
        "required": ["query"],
    }

    async def execute(self, **kwargs) -> Dict:
        query = kwargs.get("query", "")
        return {
            "status": "simulated",
            "results": [],
            "query": query,
            "total_found": 0,
            "message": f"Search for '{query}' completed (simulated)",
        }


@register_tool
class EmailClassifyTool(BaseTool):
    name = "classify_email"
    description = "Classify an email by priority, category, and sentiment"
    parameters = {
        "type": "object",
        "properties": {
            "subject": {"type": "string", "description": "Email subject"},
            "body": {"type": "string", "description": "Email body content"},
            "from_address": {"type": "string", "description": "Sender email address"},
        },
        "required": ["subject", "body"],
    }

    async def execute(self, **kwargs) -> Dict:
        return {
            "status": "simulated",
            "classification": {
                "priority": "normal",
                "category": "general",
                "sentiment": "neutral",
                "is_urgent": False,
                "requires_immediate_action": False,
            }
        }
