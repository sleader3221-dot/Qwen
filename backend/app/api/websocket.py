import json
import logging
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Set

from app.services.workflow_service import workflow_service
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)
router = APIRouter()

active_connections: Set[WebSocket] = set()


@router.websocket("/ws/workflows/{workflow_id}")
async def workflow_websocket(websocket: WebSocket, workflow_id: str):
    await websocket.accept()
    active_connections.add(websocket)
    logger.info(f"WebSocket connected for workflow {workflow_id}")

    try:
        loop = asyncio.get_event_loop()
        for event in workflow_service.run_workflow(workflow_id):
            try:
                await websocket.send_json(event)
            except Exception:
                break
            await asyncio.sleep(0)
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for workflow {workflow_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        active_connections.discard(websocket)
