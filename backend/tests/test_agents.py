import pytest
from unittest.mock import AsyncMock, patch
from app.agents.email_agent import EmailAgent


@pytest.fixture
def email_agent():
    return EmailAgent()


@pytest.mark.asyncio
async def test_email_agent_initialization(email_agent):
    assert email_agent.name == "email_agent"
    assert "email" in email_agent.description.lower()
