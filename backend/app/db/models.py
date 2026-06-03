import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Float, Integer, Boolean, DateTime, ForeignKey, JSON, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.db.session import Base


def generate_uuid():
    return str(uuid.uuid4())


class WorkflowStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"
    AWAITING_HUMAN = "awaiting_human"


class AgentType(str, enum.Enum):
    ORCHESTRATOR = "orchestrator"
    EMAIL = "email"
    DOCUMENT = "document"
    SCHEDULER = "scheduler"
    CRM = "crm"
    DATA = "data"
    NOTIFICATION = "notification"
    CODE_REVIEW = "code_review"
    REPORT = "report"


class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), default=WorkflowStatus.PENDING.value)
    input_data = Column(JSON)
    output_data = Column(JSON, nullable=True)
    confidence_score = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    created_by = Column(String(255), default="system")
    total_tokens_used = Column(Integer, default=0)
    total_steps = Column(Integer, default=0)
    completed_steps = Column(Integer, default=0)
    human_intervention_count = Column(Integer, default=0)
    agent_type = Column(String(50), nullable=True)
    tags = Column(JSON, default=list)

    steps = relationship("WorkflowStep", back_populates="workflow", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="workflow", cascade="all, delete-orphan")


class WorkflowStep(Base):
    __tablename__ = "workflow_steps"

    id = Column(String, primary_key=True, default=generate_uuid)
    workflow_id = Column(String, ForeignKey("workflows.id"), nullable=False)
    step_order = Column(Integer, nullable=False)
    step_type = Column(String(100), nullable=False)
    agent_type = Column(String(50), nullable=True)
    status = Column(String(50), default="pending")
    input_data = Column(JSON)
    output_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    confidence_score = Column(Float, nullable=True)
    requires_human = Column(Boolean, default=False)
    human_approved = Column(Boolean, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    tokens_used = Column(Integer, default=0)
    retry_count = Column(Integer, default=0)
    step_metadata = Column("metadata", JSON, default=dict)

    workflow = relationship("Workflow", back_populates="steps")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=generate_uuid)
    workflow_id = Column(String, ForeignKey("workflows.id"), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(100), nullable=True)
    entity_id = Column(String(100), nullable=True)
    actor = Column(String(255), nullable=True)
    details = Column(JSON)
    severity = Column(String(20), default="info")
    created_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)

    workflow = relationship("Workflow", back_populates="audit_logs")


class AgentMemory(Base):
    __tablename__ = "agent_memories"

    id = Column(String, primary_key=True, default=generate_uuid)
    agent_type = Column(String(50), nullable=False)
    memory_key = Column(String(255), nullable=False)
    memory_value = Column(JSON, nullable=False)
    context = Column(JSON, default=dict)
    importance_score = Column(Float, default=0.5)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_accessed_at = Column(DateTime, default=datetime.utcnow)
    access_count = Column(Integer, default=1)
    expires_at = Column(DateTime, nullable=True)
    ttl_seconds = Column(Integer, nullable=True)

    __table_args__ = (
        {"sqlite_autoincrement": True},
    )


class ConversationCache(Base):
    __tablename__ = "conversation_caches"

    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String(255), nullable=False, index=True)
    messages = Column(JSON, default=list)
    context_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    token_count = Column(Integer, default=0)
