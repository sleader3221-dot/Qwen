import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.api.routes import router as api_router
from app.api.websocket import router as ws_router
from app.api.middleware import LoggingMiddleware, MetricsMiddleware
from app.db.session import engine, Base
from app.services.audit_service import AuditService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized")
except Exception as e:
    logger.warning(f"Database init skipped: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)
app.add_middleware(MetricsMiddleware)

app.include_router(api_router, prefix="/v1")
app.include_router(ws_router)
