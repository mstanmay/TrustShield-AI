"""
Browser Extension Schemas — fast lightweight request & response models (< 300ms SLA).
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class ExtensionScanURLRequest(BaseModel):
    """Payload for real-time URL scanning from browser address bar / links."""
    url: str = Field(..., min_length=4)
    page_title: str | None = None
    referrer: str | None = None


class ExtensionScanURLResponse(BaseModel):
    """Fast URL scan result payload."""
    url: str
    is_phishing: bool
    risk_score: float = Field(..., ge=0.0, le=1.0)
    threat_severity: str  # CRITICAL | HIGH | MEDIUM | LOW | SAFE
    domain_age_days: int | None = None
    category: str
    action_recommended: str  # BLOCK | WARN | ALLOW
    cached: bool = False
    processing_time_ms: float


class ExtensionScanTextRequest(BaseModel):
    """Payload for page body text snippet or selection scan."""
    text: str = Field(..., min_length=5)
    page_url: str | None = None


class ExtensionScanTextResponse(BaseModel):
    """Fast text analysis response."""
    contains_scam_keywords: bool
    risk_score: float = Field(..., ge=0.0, le=1.0)
    detected_keywords: list[str]
    unregistered_advisor_flags: list[str]
    action_recommended: str
    processing_time_ms: float


class ExtensionScanDOMRequest(BaseModel):
    """Payload for webpage DOM structural inspection."""
    page_url: str
    dom_text_snippet: str
    form_actions: list[str] = Field(default_factory=list)
    image_srcs: list[str] = Field(default_factory=list)
    has_sebi_logo_mention: bool = False


class ExtensionScanDOMResponse(BaseModel):
    """Fast DOM inspection response."""
    page_url: str
    is_impersonating_sebi: bool
    suspicious_forms_count: int
    risk_score: float = Field(..., ge=0.0, le=1.0)
    reasons: list[str]
    action_recommended: str
    processing_time_ms: float


class ActiveThreatItem(BaseModel):
    """Item in active threat intelligence feed."""
    threat_id: str
    type: str  # Phishing Domain | Fake SEBI Portal | Telegram Pump Group | WhatsApp Advisory Scam
    indicator: str
    risk_score: float
    reported_count: int
    added_at: str


class ActiveThreatsResponse(BaseModel):
    """Live active threat feed response for extension badge warnings."""
    total_active_threats: int
    threats: list[ActiveThreatItem]
