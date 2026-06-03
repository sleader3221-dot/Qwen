import pytest
from unittest.mock import AsyncMock, patch
from app.core.orchestrator import WorkflowOrchestrator
from app.db.models import Workflow


@pytest.fixture
def orchestrator():
    return WorkflowOrchestrator()


@pytest.fixture
def sample_workflow():
    return Workflow(
        id="test-wf-1",
        name="Test Workflow",
        status="pending",
        input_data={"task": "Send an email notification about the Q4 report to the team"},
    )


@pytest.mark.asyncio
async def test_workflow_creation(orchestrator, sample_workflow):
    assert sample_workflow.id == "test-wf-1"
    assert sample_workflow.status == "pending"


@pytest.mark.asyncio
async def test_confidence_scorer():
    from app.core.confidence_scorer import ConfidenceScorer
    scorer = ConfidenceScorer()

    response = {
        "content": "This is a detailed response with multiple steps to complete the task successfully.",
        "finish_reason": "stop",
        "usage": {"total_tokens": 150},
    }
    score = scorer.score(response, "email_processing")
    assert 0 <= score <= 1
    assert score > 0.5


@pytest.mark.asyncio
async def test_error_handler_classification():
    from app.core.error_handler import ErrorHandler
    handler = ErrorHandler()

    assert handler.classify_error(Exception("Rate limit exceeded")) == "rate_limit"
    assert handler.classify_error(Exception("timeout occurred")) == "timeout"
    assert handler.classify_error(Exception("unauthorized access")) == "authentication"
    assert handler.classify_error(Exception("unknown error")) == "unknown"


@pytest.mark.asyncio
async def test_token_manager():
    from app.utils.token_manager import TokenManager
    mgr = TokenManager()

    result = mgr.check_budget(100)
    assert result["status"] == "ok"
    assert result["remaining"] > 0
    assert result["usage_ratio"] < 0.01
