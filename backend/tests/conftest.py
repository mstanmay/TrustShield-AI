"""
Test fixtures — mock services, test DB, sample data.
"""

from __future__ import annotations

import os
import uuid
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

# Override settings before importing app modules
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///test.db"
os.environ["DATABASE_SYNC_URL"] = "sqlite:///test.db"
os.environ["REDIS_URL"] = "redis://localhost:6379/15"
os.environ["ANTHROPIC_API_KEY"] = ""
os.environ["JWT_SECRET_KEY"] = "test_secret_key_32_chars_minimum"

from app.models.enums import AgentType, InputType
from app.models.schemas import (
    DeepfakeResult,
    DocumentResult,
    Evidence,
    PhishingResult,
    RiskAssessmentResult,
    VoiceResult,
)


@pytest.fixture
def sample_case_id() -> str:
    return str(uuid.uuid4())


@pytest.fixture
def sample_deepfake_result() -> DeepfakeResult:
    return DeepfakeResult(
        result="MODERATE indicators of potential manipulation found",
        confidence_score=0.45,
        evidence=[
            Evidence(
                finding="High facial landmark jitter detected (0.42)",
                severity="warning",
                detail={"score": 0.42, "check": "landmark_jitter"},
            ),
            Evidence(
                finding="Compression/blending artifacts detected (0.35)",
                severity="warning",
                detail={"score": 0.35, "check": "compression_artifacts"},
            ),
        ],
        raw_model_output={
            "landmark_jitter": 0.42,
            "lip_sync": 0.1,
            "compression": 0.35,
            "flicker": 0.15,
        },
        facial_landmark_jitter=0.42,
        lip_sync_score=0.1,
        compression_artifact_score=0.35,
        temporal_flicker_score=0.15,
        face_count=1,
        frames_analyzed=30,
    )


@pytest.fixture
def sample_voice_result() -> VoiceResult:
    return VoiceResult(
        result="MODERATE indicators of possible synthetic audio",
        confidence_score=0.35,
        evidence=[
            Evidence(
                finding="Unnaturally smooth pitch contour (F0 std: 8.5 Hz — normal is >15 Hz)",
                severity="warning",
                detail={"f0_std": 8.5, "f0_mean": 180.0},
            ),
        ],
        raw_model_output={"f0_std": 8.5, "f0_mean": 180.0, "spectral_flatness": 0.15},
        synthetic_speech_score=0.4,
        spectral_anomaly_score=0.2,
        audio_fingerprint="abc123def456",
        duration_seconds=30.5,
        sample_rate=16000,
    )


@pytest.fixture
def sample_document_result() -> DocumentResult:
    return DocumentResult(
        result="MODERATE indicators of potential document manipulation or scam content",
        confidence_score=0.5,
        evidence=[
            Evidence(
                finding="Urgency/pressure language detected: guaranteed return, act now",
                severity="warning",
                detail={"keywords": ["guaranteed return", "act now"]},
            ),
            Evidence(
                finding="Document created with non-standard tool: Canva",
                severity="warning",
                detail={"creation_tool": "Canva"},
            ),
        ],
        raw_model_output={"ocr_text_length": 1500, "pdf_metadata": {}},
        ocr_text="Guaranteed returns of 50% monthly! Act now. Contact: +919876543210",
        metadata_flags=["Document created with: Canva"],
        font_consistency_score=0.4,
        extracted_urls=["https://fake-sebi-portal.com/invest"],
        creation_tool="Canva",
    )


@pytest.fixture
def sample_phishing_result() -> PhishingResult:
    return PhishingResult(
        result="HIGH phishing risk — multiple indicators of fraudulent URL(s) detected",
        confidence_score=0.75,
        evidence=[
            Evidence(
                finding="Domain 'sebl.gov.in' is suspiciously similar to known domain 'sebi.gov.in' (edit distance: 1)",
                severity="critical",
                detail={"known_domain": "sebi.gov.in", "distance": 1},
            ),
            Evidence(
                finding="Domain registered very recently (5 days ago)",
                severity="critical",
                detail={"domain_age_days": 5},
            ),
        ],
        raw_model_output={"urls_analyzed": ["https://sebl.gov.in/login"]},
        analyzed_urls=["https://sebl.gov.in/login"],
        domain_age_days=5,
        ssl_valid=False,
        typosquat_matches=[
            {"known_domain": "sebi.gov.in", "suspicious_domain": "sebl.gov.in", "distance": 1}
        ],
        reputation_scores={"https://sebl.gov.in/login": 0.8},
    )


@pytest.fixture
def all_agent_results(
    sample_deepfake_result,
    sample_voice_result,
    sample_document_result,
    sample_phishing_result,
) -> dict[str, Any]:
    """All agent results as metadata dict for risk assessment."""
    return {
        "deepfake_result": sample_deepfake_result,
        "voice_result": sample_voice_result,
        "document_result": sample_document_result,
        "phishing_result": sample_phishing_result,
    }
