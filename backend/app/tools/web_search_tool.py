import json
import logging
from typing import Dict

from app.core.tool_registry import BaseTool, register_tool
from app.services.qwen_service import qwen_service

logger = logging.getLogger(__name__)


@register_tool
class WebSearchTool(BaseTool):
    name = "web_search"
    description = "Search the web for current information on any topic. Returns relevant results with sources."
    parameters = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The search query"},
            "max_results": {"type": "integer", "description": "Maximum number of results"},
            "search_type": {"type": "string", "enum": ["general", "news", "research"]},
        },
        "required": ["query"],
    }

    async def execute(self, **kwargs) -> Dict:
        query = kwargs.get("query", "")
        logger.info(f"Web search: {query}")
        response = await qwen_service.chat_completion(
            messages=[{"role": "user", "content": f"Search the web for: {query}. Provide a concise summary with key findings and sources."}],
            enable_search=True,
            temperature=0.1,
        )
        return {
            "status": "completed",
            "query": query,
            "results": response.get("content", ""),
            "source": "qwen_web_search",
        }


@register_tool
class WebExtractorTool(BaseTool):
    name = "web_extractor"
    description = "Extract and read the full content of a web page given its URL"
    parameters = {
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "The URL to extract content from"},
            "max_length": {"type": "integer", "description": "Maximum characters to extract"},
        },
        "required": ["url"],
    }

    async def execute(self, **kwargs) -> Dict:
        url = kwargs.get("url", "")
        max_length = kwargs.get("max_length", 5000)
        return {
            "status": "simulated",
            "url": url,
            "content_preview": f"Content from {url} (web extraction simulated)",
            "total_chars": max_length,
        }
