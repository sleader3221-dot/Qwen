import pytest
from app.tools.email_tool import EmailTool, EmailClassifyTool
from app.core.tool_registry import ToolRegistry


@pytest.mark.asyncio
async def test_email_tool():
    tool = EmailTool()
    result = await tool.execute(
        to=["test@example.com"],
        subject="Test Email",
        body="This is a test"
    )
    assert result["status"] == "simulated"
    assert len(result["to"]) == 1


@pytest.mark.asyncio
async def test_tool_registry():
    registry = ToolRegistry()
    assert len(registry.get_all_tools()) > 0
    tools = registry.get_openai_tools()
    assert len(tools) > 0
    for t in tools:
        assert "type" in t
        assert "function" in t
