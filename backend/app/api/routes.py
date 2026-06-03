import json
import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from sse_starlette.sse import EventSourceResponse

from app.services.workflow_service import workflow_service
from app.services.audit_service import audit_service
from app.services.analytics_service import analytics_service
from app.utils.validators import ResponseFormatter
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "features": {
            "thinking_mode": settings.enable_thinking_mode,
            "web_search": settings.enable_web_search,
            "code_interpreter": settings.enable_code_interpreter,
            "mcp_integration": settings.enable_mcp_integration,
            "human_in_loop": settings.enable_human_in_loop,
        },
    }


@router.post("/workflows")
def create_workflow(
    name: str = Query(..., description="Workflow name"),
    task: str = Query(..., description="Task description"),
    created_by: str = Query("system"),
    agent_type: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
):
    try:
        parsed_tags = json.loads(tags) if tags else []
        workflow = workflow_service.create_workflow(
            name=name, task=task, created_by=created_by, agent_type=agent_type, tags=parsed_tags,
        )
        audit_service.log(
            action="workflow.created", entity_type="workflow", entity_id=workflow.id,
            actor=created_by, details={"name": name, "task_preview": task[:200]},
        )
        return ResponseFormatter.success({
            "id": workflow.id, "name": workflow.name,
            "status": workflow.status,
            "created_at": workflow.created_at.isoformat() if workflow.created_at else None,
        }, "Workflow created successfully")
    except Exception as e:
        logger.error(f"Create workflow error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows/{workflow_id}")
def get_workflow(workflow_id: str):
    result = workflow_service.get_workflow(workflow_id)
    if not result:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return ResponseFormatter.success(result)


@router.get("/workflows")
def list_workflows(
    status: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    result = workflow_service.list_workflows(status=status, limit=limit, offset=offset)
    return ResponseFormatter.paginated(result["workflows"], result["total"], limit, offset)


@router.post("/workflows/{workflow_id}/run-sync")
def run_workflow_sync(workflow_id: str):
    result = None
    for event in workflow_service.run_workflow(workflow_id):
        if event.get("type") == "workflow_completed":
            result = event
        elif event.get("type") == "workflow_failed":
            raise HTTPException(status_code=500, detail=event.get("error", "Workflow failed"))
    if result:
        audit_service.log(
            action="workflow.completed", entity_type="workflow", entity_id=workflow_id,
            details={"output_preview": str(result.get("output", ""))[:200]},
        )
        return ResponseFormatter.success(result)
    return ResponseFormatter.error("No result", "EXECUTION_EMPTY")


@router.post("/workflows/{workflow_id}/run")
def run_workflow_stream(workflow_id: str):
    def event_generator():
        for event in workflow_service.run_workflow(workflow_id):
            yield event
    return EventSourceResponse(event_generator())


@router.post("/workflows/{workflow_id}/cancel")
def cancel_workflow(workflow_id: str):
    success = workflow_service.cancel_workflow(workflow_id)
    if success:
        audit_service.log(action="workflow.cancelled", entity_type="workflow", entity_id=workflow_id)
        return ResponseFormatter.success({"cancelled": True})
    raise HTTPException(status_code=400, detail="Cannot cancel")


@router.post("/workflows/{workflow_id}/approve")
def approve_step(
    workflow_id: str,
    step_order: int = Query(...),
    approved: bool = Query(True),
    feedback: Optional[str] = Query(None),
):
    success = workflow_service.approve_human_step(workflow_id, step_order, approved, feedback)
    if success:
        audit_service.log(
            action=f"step.{'approved' if approved else 'rejected'}",
            entity_type="workflow_step", entity_id=f"{workflow_id}:{step_order}",
            workflow_id=workflow_id, details={"feedback": feedback},
        )
        return ResponseFormatter.success({"approved": approved})
    raise HTTPException(status_code=400, detail="Step not found")


@router.get("/token-usage")
def get_token_usage():
    return ResponseFormatter.success(workflow_service.get_token_usage())


@router.get("/analytics/dashboard")
def get_dashboard():
    return ResponseFormatter.success(analytics_service.get_dashboard_stats())


@router.get("/analytics/timeline")
def get_timeline(days: int = Query(7, ge=1, le=90)):
    return ResponseFormatter.success(analytics_service.get_workflow_timeline(days=days))


@router.get("/audit-logs")
def get_audit_logs(
    workflow_id: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    result = audit_service.get_logs(workflow_id=workflow_id, action=action, limit=limit, offset=offset)
    return ResponseFormatter.paginated(result["logs"], result["total"], limit, offset)


@router.get("/features")
def get_features():
    return ResponseFormatter.success({
        "thinking_mode": settings.enable_thinking_mode,
        "web_search": settings.enable_web_search,
        "code_interpreter": settings.enable_code_interpreter,
        "mcp_integration": settings.enable_mcp_integration,
        "human_in_loop": settings.enable_human_in_loop,
        "confidence_threshold": settings.confidence_threshold,
        "max_retry_attempts": settings.max_retry_attempts,
        "model": settings.qwen_model,
        "daily_token_budget": settings.token_budget_daily,
    })


@router.get("/alibaba-cloud-proof")
def alibaba_cloud_proof():
    return ResponseFormatter.success({
        "service": "Alibaba Cloud Model Studio (DashScope)",
        "region": settings.alibaba_cloud_region,
        "endpoints": {
            "chat_completions": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/chat/completions",
            "responses_api": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/responses",
            "embeddings": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1/embeddings",
        },
        "models_used": [settings.qwen_model],
        "deployment": "Alibaba Cloud Singapore Region",
        "services_used": [
            "Qwen Cloud Model Studio (DashScope)",
            "Qwen Chat Completions API",
            "Qwen Function Calling",
            "Qwen Built-in Tools",
            "Qwen Conversations API",
            "Qwen Session Cache",
        ],
    })


@router.post("/workflows/{workflow_id}/resume")
def resume_workflow(workflow_id: str):
    """Resume a workflow that was paused waiting for human input (legacy compat)."""
    return run_workflow_sync(workflow_id)
