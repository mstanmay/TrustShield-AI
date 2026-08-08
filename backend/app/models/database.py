"""
SQLAlchemy ORM models — Case, Verdict, Complaint, AlertSubscription, User tables.
Uses pgvector for embedding-based similarity search.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Enum as SAEnum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Boolean,
    JSON,
    UUID,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cases = relationship("Case", back_populates="user")


class Case(Base):
    """A fraud detection case — the central entity."""
    __tablename__ = "cases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(String(36), unique=True, nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    input_type = Column(String(50), nullable=False)
    original_filename = Column(String(500), nullable=True)
    artifact_path = Column(String(1000), nullable=True)
    status = Column(String(20), nullable=False, default="pending")
    source_ip = Column(String(45), nullable=True)
    geo_region = Column(String(100), nullable=True)

    # Per-agent results stored as JSON
    deepfake_result = Column(JSON, nullable=True)
    voice_result = Column(JSON, nullable=True)
    document_result = Column(JSON, nullable=True)
    phishing_result = Column(JSON, nullable=True)
    risk_assessment_result = Column(JSON, nullable=True)

    # Execution trace for audit
    execution_trace = Column(JSON, nullable=True)
    applicable_agents = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)

    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processing_started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="cases")
    verdict = relationship("Verdict", back_populates="case", uselist=False)
    complaint = relationship("Complaint", back_populates="case", uselist=False)

    __table_args__ = (
        Index("idx_cases_status", "status"),
        Index("idx_cases_input_type", "input_type"),
        Index("idx_cases_uploaded_at", "uploaded_at"),
    )


class Verdict(Base):
    """Final decision engine output for a case."""
    __tablename__ = "verdicts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(String(36), ForeignKey("cases.case_id"), unique=True, nullable=False)
    classification = Column(String(20), nullable=False)
    risk_score = Column(Float, nullable=False)
    threat_severity = Column(String(20), nullable=False)
    explanation = Column(Text, nullable=True)
    evidence_breakdown = Column(JSON, nullable=True)
    reasoning_chain = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    case = relationship("Case", back_populates="verdict")

    __table_args__ = (
        Index("idx_verdicts_classification", "classification"),
        Index("idx_verdicts_risk_score", "risk_score"),
    )


class Complaint(Base):
    """SEBI SCORES complaint draft and submission tracking."""
    __tablename__ = "complaints"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(String(36), ForeignKey("cases.case_id"), unique=True, nullable=False)
    status = Column(String(30), nullable=False, default="DRAFT_READY")
    complainant_name = Column(String(255), nullable=True)
    subject = Column(String(500), nullable=True)
    complaint_body = Column(Text, nullable=True)
    evidence_summary = Column(JSON, nullable=True)
    involved_urls = Column(JSON, nullable=True)
    involved_domains = Column(JSON, nullable=True)
    involved_phone_numbers = Column(JSON, nullable=True)
    verdict_summary = Column(Text, nullable=True)
    pdf_path = Column(String(1000), nullable=True)
    draft_json = Column(JSON, nullable=True)

    generated_at = Column(DateTime, default=datetime.utcnow)
    confirmed_at = Column(DateTime, nullable=True)

    case = relationship("Case", back_populates="complaint")


class AlertSubscription(Base):
    """Browser extension / webhook alert subscriptions."""
    __tablename__ = "alert_subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    subscription_type = Column(String(20), nullable=False)  # "websocket" | "webhook"
    webhook_url = Column(String(1000), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class SEBICircular(Base):
    """Known trusted SEBI circulars for corpus matching.
    Uses pgvector for embedding-based similarity search."""
    __tablename__ = "sebi_circulars"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    circular_number = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=True)
    issued_date = Column(DateTime, nullable=True)
    content_text = Column(Text, nullable=True)
    signatory = Column(String(255), nullable=True)
    department = Column(String(255), nullable=True)
    content_hash = Column(String(64), nullable=True)  # SHA-256 of content
    # NOTE: embedding column added via Alembic migration with pgvector
    # embedding = Column(Vector(1536), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class KnownScamPattern(Base):
    """Known scam patterns for similarity matching."""
    __tablename__ = "known_scam_patterns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    pattern_type = Column(String(50), nullable=False)  # "domain", "message_template", "audio_fingerprint"
    pattern_value = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    severity = Column(String(20), default="medium")
    # NOTE: embedding column added via Alembic migration with pgvector
    # embedding = Column(Vector(1536), nullable=True)
    reported_count = Column(Integer, default=1)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
