"""
Enumerations used throughout the SEBI Fraud Detection system.
"""

from __future__ import annotations

from enum import Enum


class InputType(str, Enum):
    """Supported input artifact types."""
    VIDEO = "video"
    IMAGE = "image"
    AUDIO = "audio"
    PDF = "pdf"
    URL = "url"
    EMAIL = "email"
    QR_CODE = "qr_code"
    WHATSAPP_MESSAGE = "whatsapp_message"
    TELEGRAM_LINK = "telegram_link"


class CaseStatus(str, Enum):
    """Lifecycle status of a fraud detection case."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Classification(str, Enum):
    """Final fraud classification."""
    GENUINE = "Genuine"
    SUSPICIOUS = "Suspicious"
    FRAUDULENT = "Fraudulent"


class ThreatSeverity(str, Enum):
    """Severity level of detected threat."""
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class RecommendedAction(str, Enum):
    """Recommended follow-up action based on analysis."""
    IGNORE_SAFE = "IGNORE_SAFE"
    WARN_USER = "WARN_USER"
    BLOCK_AND_REPORT = "BLOCK_AND_REPORT"
    ESCALATE_TO_SEBI = "ESCALATE_TO_SEBI"


class ComplaintStatus(str, Enum):
    """Status of a SEBI SCORES complaint draft."""
    DRAFT_READY = "DRAFT_READY"
    USER_REVIEWED = "USER_REVIEWED"
    READY_FOR_SUBMISSION = "READY_FOR_SUBMISSION"


class AgentType(str, Enum):
    """Identifiers for each specialized agent."""
    DEEPFAKE = "deepfake"
    VOICE = "voice"
    DOCUMENT = "document"
    PHISHING = "phishing"
    RISK_ASSESSMENT = "risk_assessment"
