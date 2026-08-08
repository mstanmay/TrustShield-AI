"""
Pydantic schemas — CaseState (LangGraph shared state), all agent result types,
Decision Engine output, and API request/response models.

Every agent result includes: result, confidence_score, evidence, raw_model_output.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.enums import (
    AgentType,
    CaseStatus,
    Classification,
    ComplaintStatus,
    InputType,
    RecommendedAction,
    ThreatSeverity,
)


# ── Evidence Building Block ──────────────────────────────────────────────────

class Evidence(BaseModel):
    """A single piece of evidence found by an agent."""
    finding: str = Field(..., description="What was found")
    severity: str = Field(default="info", description="info | warning | critical")
    detail: dict[str, Any] = Field(default_factory=dict, description="Structured detail")


# ── Base Agent Result ────────────────────────────────────────────────────────

class AgentResult(BaseModel):
    """Standard output shape for every agent."""
    agent_type: AgentType
    result: str = Field(..., description="Human-readable summary of analysis")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="0=no concern, 1=certain fraud")
    evidence: list[Evidence] = Field(default_factory=list)
    raw_model_output: dict[str, Any] = Field(default_factory=dict, description="Raw output for auditability")
    execution_time_ms: float = Field(default=0.0, description="Agent execution time in milliseconds")
    error: str | None = Field(default=None, description="Error message if agent failed")


# ── Specialized Agent Results ────────────────────────────────────────────────

class DeepfakeResult(AgentResult):
    """Output from the Deepfake Detection Agent."""
    agent_type: AgentType = AgentType.DEEPFAKE
    facial_landmark_jitter: float = Field(default=0.0, description="Landmark consistency score 0-1")
    lip_sync_score: float = Field(default=0.0, description="Audio-visual lip sync correlation 0-1")
    compression_artifact_score: float = Field(default=0.0, description="Compression/blending artifact level 0-1")
    temporal_flicker_score: float = Field(default=0.0, description="Frame-to-frame flicker detection 0-1")
    face_count: int = Field(default=0, description="Number of faces detected")
    frames_analyzed: int = Field(default=0, description="Number of frames processed")


class VoiceResult(AgentResult):
    """Output from the Voice Analysis Agent."""
    agent_type: AgentType = AgentType.VOICE
    synthetic_speech_score: float = Field(default=0.0, description="Probability of synthetic speech 0-1")
    spectral_anomaly_score: float = Field(default=0.0, description="Spectral inconsistency level 0-1")
    speaker_match_score: float | None = Field(default=None, description="Match against known speaker DB, 0-1")
    audio_fingerprint: str | None = Field(default=None, description="Chromaprint-style hash for reuse detection")
    duration_seconds: float = Field(default=0.0)
    sample_rate: int = Field(default=0)


class DocumentResult(AgentResult):
    """Output from the OCR & Document Verification Agent."""
    agent_type: AgentType = AgentType.DOCUMENT
    ocr_text: str = Field(default="", description="Extracted text from document")
    metadata_flags: list[str] = Field(default_factory=list, description="Suspicious metadata findings")
    font_consistency_score: float = Field(default=0.0, description="Font uniformity score 0-1")
    corpus_match_score: float | None = Field(default=None, description="Similarity to trusted SEBI circular corpus")
    matched_circular_id: str | None = Field(default=None, description="Closest matching SEBI circular ID")
    extracted_urls: list[str] = Field(default_factory=list, description="URLs found in document")
    creation_tool: str | None = Field(default=None)


class PhishingResult(AgentResult):
    """Output from the Phishing Intelligence Agent."""
    agent_type: AgentType = AgentType.PHISHING
    analyzed_urls: list[str] = Field(default_factory=list)
    domain_age_days: int | None = Field(default=None, description="Age of domain in days")
    ssl_valid: bool | None = Field(default=None)
    ssl_issuer: str | None = Field(default=None)
    registrant_info: dict[str, Any] = Field(default_factory=dict)
    typosquat_matches: list[dict[str, Any]] = Field(default_factory=list, description="Similar known domains")
    reputation_scores: dict[str, float] = Field(default_factory=dict, description="Per-provider reputation")
    qr_decoded_url: str | None = Field(default=None, description="URL decoded from QR code")


class RiskAssessmentResult(AgentResult):
    """Output from the Risk Assessment Agent."""
    agent_type: AgentType = AgentType.RISK_ASSESSMENT
    fraud_probability: float = Field(default=0.0, ge=0.0, le=1.0)
    recommended_action: RecommendedAction = Field(default=RecommendedAction.IGNORE_SAFE)
    explainable_reasoning: str = Field(default="", description="LLM-generated explanation grounded in agent outputs")
    weighted_scores: dict[str, float] = Field(default_factory=dict, description="Per-agent weighted contribution")
    agents_used: list[AgentType] = Field(default_factory=list)


# ── Decision Engine Output ───────────────────────────────────────────────────

class AgentContribution(BaseModel):
    """Per-agent contribution to the final decision."""
    agent_type: AgentType
    weight: float
    raw_confidence: float
    weighted_score: float
    key_findings: list[str] = Field(default_factory=list)


class DecisionResult(BaseModel):
    """Final output from the Decision Engine (STEP 4)."""
    classification: Classification
    risk_score: float = Field(..., ge=0.0, le=1.0)
    threat_severity: ThreatSeverity
    explanation: str
    evidence_breakdown: dict[str, AgentContribution] = Field(default_factory=dict)
    reasoning_chain: list[str] = Field(default_factory=list, description="Step-by-step reasoning trace")


# ── LangGraph Shared State ───────────────────────────────────────────────────

class CaseState(BaseModel):
    """Shared state object passed through the LangGraph orchestrator.
    Carries input metadata, per-agent results, and final verdict."""
    case_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    input_type: InputType
    artifact_path: str = Field(default="", description="Object storage path to raw artifact")
    original_filename: str = Field(default="")
    metadata: dict[str, Any] = Field(default_factory=dict)
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

    # Per-agent results — populated as agents complete
    deepfake_result: DeepfakeResult | None = None
    voice_result: VoiceResult | None = None
    document_result: DocumentResult | None = None
    phishing_result: PhishingResult | None = None
    risk_assessment: RiskAssessmentResult | None = None
    final_verdict: DecisionResult | None = None

    # Routing metadata
    applicable_agents: list[AgentType] = Field(default_factory=list)
    execution_trace: list[dict[str, Any]] = Field(default_factory=list, description="Full LangGraph execution log")
    status: CaseStatus = CaseStatus.PENDING
    error_message: str | None = None


# ── API Request/Response Schemas ─────────────────────────────────────────────

class IngestRequest(BaseModel):
    """Request body for URL-based ingestion (non-file)."""
    url: str | None = None
    text_content: str | None = None
    input_type_hint: InputType | None = None
    source_ip: str | None = None


class IngestResponse(BaseModel):
    """Response after successful ingestion."""
    case_id: str
    status: CaseStatus
    message: str = "Case created and queued for analysis"


class CaseResponse(BaseModel):
    """Full case details including all agent results."""
    case_id: str
    input_type: InputType
    status: CaseStatus
    uploaded_at: datetime
    deepfake_result: DeepfakeResult | None = None
    voice_result: VoiceResult | None = None
    document_result: DocumentResult | None = None
    phishing_result: PhishingResult | None = None
    risk_assessment: RiskAssessmentResult | None = None
    final_verdict: DecisionResult | None = None
    execution_trace: list[dict[str, Any]] = Field(default_factory=list)


class ThreatIntelResponse(BaseModel):
    """Aggregated threat intelligence stats."""
    total_cases: int = 0
    fraudulent_count: int = 0
    suspicious_count: int = 0
    genuine_count: int = 0
    avg_risk_score: float = 0.0
    top_threat_types: list[dict[str, Any]] = Field(default_factory=list)
    recent_cases: list[dict[str, Any]] = Field(default_factory=list)


class HeatmapDataPoint(BaseModel):
    """Single point in the fraud heatmap."""
    region: str
    count: int
    avg_severity: float
    time_bucket: str


class HeatmapResponse(BaseModel):
    """Geo/time aggregation of fraud cases."""
    data_points: list[HeatmapDataPoint] = Field(default_factory=list)
    total_regions: int = 0


class TrendCluster(BaseModel):
    """A cluster of similar scam patterns."""
    cluster_id: str
    label: str
    case_count: int
    avg_risk_score: float
    representative_case_ids: list[str] = Field(default_factory=list)
    common_indicators: list[str] = Field(default_factory=list)


class TrendsResponse(BaseModel):
    """Emerging scam trend clusters."""
    clusters: list[TrendCluster] = Field(default_factory=list)
    analysis_period_days: int = 30


class AlertItem(BaseModel):
    """A browser protection alert."""
    alert_id: str
    case_id: str
    alert_type: str
    severity: ThreatSeverity
    message: str
    created_at: datetime
    urls: list[str] = Field(default_factory=list)


class AlertsResponse(BaseModel):
    """List of active alerts."""
    alerts: list[AlertItem] = Field(default_factory=list)
    total: int = 0


class ComplaintDraft(BaseModel):
    """Structured complaint draft for SEBI SCORES."""
    case_id: str
    status: ComplaintStatus = ComplaintStatus.DRAFT_READY
    complainant_name: str | None = None
    subject: str = ""
    complaint_body: str = ""
    evidence_summary: list[dict[str, Any]] = Field(default_factory=list)
    involved_urls: list[str] = Field(default_factory=list)
    involved_domains: list[str] = Field(default_factory=list)
    involved_phone_numbers: list[str] = Field(default_factory=list)
    timestamps: list[str] = Field(default_factory=list)
    verdict_summary: str = ""
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class ComplaintResponse(BaseModel):
    """Response after complaint generation."""
    case_id: str
    status: ComplaintStatus
    draft: ComplaintDraft | None = None
    pdf_download_url: str | None = None
    message: str = ""


# ── Auth Schemas ─────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    """User registration payload."""
    username: str = Field(..., min_length=3, max_length=50)
    email: str
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """Login payload."""
    username: str
    password: str


class TokenResponse(BaseModel):
    """JWT token pair."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Public user info."""
    id: str
    username: str
    email: str
    created_at: datetime
