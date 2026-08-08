"""
Deepfake Detection Agent (3a)

Analyzes video/image files for deepfake indicators:
- Facial landmark inconsistency / jitter across frames
- Lip-sync mismatch (audio-visual correlation)
- Frame-level compression/blending artifacts
- Temporal flicker detection

Uses the pluggable DeepfakeModel adapter (heuristic default, ONNX upgrade slot).
"""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path
from typing import Any

from app.agents.base import BaseAgent
from app.adapters.deepfake_model import get_deepfake_model
from app.core.observability import traced_agent
from app.models.enums import AgentType
from app.models.schemas import DeepfakeResult, Evidence

logger = logging.getLogger(__name__)


class DeepfakeDetectionAgent(BaseAgent):
    """Agent 3a: Deepfake detection for video and image inputs."""

    @property
    def agent_type(self) -> AgentType:
        return AgentType.DEEPFAKE

    def __init__(self):
        self._model = get_deepfake_model()

    @traced_agent("deepfake")
    async def _analyze_impl(self, input_path: str, metadata: dict[str, Any]) -> DeepfakeResult:
        """Run deepfake analysis on a video or image file."""
        is_video = metadata.get("input_type") in ("video", "VIDEO")
        evidence: list[Evidence] = []

        # Run the deepfake model (heuristic or ONNX)
        model_result = await self._model.predict(input_path, is_video=is_video)

        # Build evidence from individual checks
        if model_result.facial_landmark_jitter > 0.3:
            evidence.append(Evidence(
                finding=f"High facial landmark jitter detected ({model_result.facial_landmark_jitter:.2f})",
                severity="warning" if model_result.facial_landmark_jitter < 0.6 else "critical",
                detail={"score": model_result.facial_landmark_jitter, "check": "landmark_jitter"},
            ))

        if model_result.lip_sync_score > 0.3:
            evidence.append(Evidence(
                finding=f"Lip-sync mismatch detected ({model_result.lip_sync_score:.2f})",
                severity="warning" if model_result.lip_sync_score < 0.6 else "critical",
                detail={"score": model_result.lip_sync_score, "check": "lip_sync"},
            ))

        if model_result.compression_artifact_score > 0.3:
            evidence.append(Evidence(
                finding=f"Compression/blending artifacts detected ({model_result.compression_artifact_score:.2f})",
                severity="warning" if model_result.compression_artifact_score < 0.5 else "critical",
                detail={"score": model_result.compression_artifact_score, "check": "compression_artifacts"},
            ))

        if model_result.temporal_flicker_score > 0.3:
            evidence.append(Evidence(
                finding=f"Temporal flicker detected between frames ({model_result.temporal_flicker_score:.2f})",
                severity="warning" if model_result.temporal_flicker_score < 0.5 else "critical",
                detail={"score": model_result.temporal_flicker_score, "check": "temporal_flicker"},
            ))

        if model_result.face_count == 0:
            evidence.append(Evidence(
                finding="No faces detected in the media",
                severity="info",
                detail={"check": "face_detection"},
            ))

        # Determine overall result
        confidence = model_result.is_deepfake_probability
        if confidence > 0.7:
            result_text = "HIGH probability of deepfake manipulation detected"
        elif confidence > 0.4:
            result_text = "MODERATE indicators of potential manipulation found"
        elif confidence > 0.15:
            result_text = "LOW-level anomalies detected — likely authentic with minor artifacts"
        else:
            result_text = "No significant deepfake indicators found — appears authentic"

        return DeepfakeResult(
            result=result_text,
            confidence_score=confidence,
            evidence=evidence,
            raw_model_output=model_result.raw_scores,
            facial_landmark_jitter=model_result.facial_landmark_jitter,
            lip_sync_score=model_result.lip_sync_score,
            compression_artifact_score=model_result.compression_artifact_score,
            temporal_flicker_score=model_result.temporal_flicker_score,
            face_count=model_result.face_count,
            frames_analyzed=model_result.frames_analyzed,
        )
