"""
Event Schemas — Pydantic event contracts for RabbitMQ event bus messages.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from pydantic import BaseModel, Field


class BaseEvent(BaseModel):
    """Base event payload header."""
    event_id: str
    event_type: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    correlation_id: str


class CaseUploadedEvent(BaseEvent):
    """Fired when an artifact/URL/text is uploaded to the system."""
    case_id: str
    input_type: str
    artifact_path: str
    original_filename: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)


class AnalysisRequestedEvent(BaseEvent):
    """Fired when an async analysis task is enqueued."""
    case_id: str
    input_type: str
    artifact_path: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class AnalysisCompletedEvent(BaseEvent):
    """Fired when LangGraph orchestrator completes a case verdict."""
    case_id: str
    classification: str
    risk_score: float
    threat_severity: str
    execution_time_ms: float


class AnalysisFailedEvent(BaseEvent):
    """Fired when case processing fails or lands in Dead Letter Queue (DLQ)."""
    case_id: str
    error_message: str
    retry_count: int = 0


class AlertTriggeredEvent(BaseEvent):
    """Fired when high-severity fraud threat is detected for real-time notification."""
    case_id: str
    threat_type: str
    risk_score: float
    affected_url_or_domain: str
