import logging
from typing import Dict, Any, Optional, Callable, Awaitable

logger = logging.getLogger(__name__)


class BaseTool:
    name: str = ""
    description: str = ""
    parameters: dict = {"type": "object", "properties": {}, "required": []}

    async def execute(self, **kwargs) -> Any:
        raise NotImplementedError

    def to_openai_tool(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class ToolRegistry:
    _tools: Dict[str, BaseTool] = {}

    @classmethod
    def register(cls, tool: BaseTool):
        cls._tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")

    @classmethod
    def get_tool(cls, name: str) -> Optional[BaseTool]:
        return cls._tools.get(name)

    @classmethod
    def get_all_tools(cls) -> list:
        return list(cls._tools.values())

    @classmethod
    def get_openai_tools(cls) -> list:
        return [t.to_openai_tool() for t in cls._tools.values()]

    @classmethod
    def get_tool_schemas(cls) -> list:
        return [{"name": t.name, "description": t.description, "parameters": t.parameters} for t in cls._tools.values()]


def register_tool(cls):
    ToolRegistry.register(cls())
    return cls
