import pytest
from app.services.workflow_service import WorkflowService


@pytest.mark.asyncio
async def test_workflow_service_analytics():
    from app.services.analytics_service import AnalyticsService
    analytics = AnalyticsService()
    result = await analytics.get_dashboard_stats()
    assert "total_workflows" in result
    assert "success_rate" in result
