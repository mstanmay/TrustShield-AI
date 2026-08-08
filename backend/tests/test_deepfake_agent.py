"""
Unit tests for the Deepfake Detection Agent.
Tests interface compliance, confidence bounds, evidence population.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.agents.deepfake_agent import DeepfakeDetectionAgent
from app.adapters.deepfake_model import DeepfakeModelResult
from app.models.enums import AgentType
from app.models.schemas import DeepfakeResult


@pytest.mark.asyncio
class TestDeepfakeAgent:
    """Tests for DeepfakeDetectionAgent."""

    async def test_agent_type(self):
        agent = DeepfakeDetectionAgent()
        assert agent.agent_type == AgentType.DEEPFAKE

    @patch("app.agents.deepfake_agent.get_deepfake_model")
    async def test_analyze_returns_deepfake_result(self, mock_get_model):
        """Agent returns a properly shaped DeepfakeResult."""
        mock_model = AsyncMock()
        mock_model.predict.return_value = DeepfakeModelResult(
            is_deepfake_probability=0.6,
            facial_landmark_jitter=0.5,
            lip_sync_score=0.3,
            compression_artifact_score=0.4,
            temporal_flicker_score=0.2,
            face_count=1,
            frames_analyzed=20,
            raw_scores={"test": 0.6},
        )
        mock_get_model.return_value = mock_model

        agent = DeepfakeDetectionAgent()
        agent._model = mock_model

        result = await agent.analyze("test_video.mp4", metadata={"input_type": "video"})

        assert isinstance(result, (DeepfakeResult, type(result)))
        assert result.agent_type == AgentType.DEEPFAKE
        assert 0.0 <= result.confidence_score <= 1.0
        assert result.result  # Non-empty result string
        assert isinstance(result.evidence, list)
        assert isinstance(result.raw_model_output, dict)

    @patch("app.agents.deepfake_agent.get_deepfake_model")
    async def test_confidence_score_bounds(self, mock_get_model):
        """Confidence score is always normalized to 0-1 range."""
        mock_model = AsyncMock()
        mock_model.predict.return_value = DeepfakeModelResult(
            is_deepfake_probability=1.5,  # Out of bounds
            raw_scores={},
        )
        mock_get_model.return_value = mock_model

        agent = DeepfakeDetectionAgent()
        agent._model = mock_model

        result = await agent.analyze("test.mp4", metadata={"input_type": "video"})
        assert result.confidence_score <= 1.0
        assert result.confidence_score >= 0.0

    @patch("app.agents.deepfake_agent.get_deepfake_model")
    async def test_high_confidence_generates_evidence(self, mock_get_model):
        """High jitter/artifact scores should produce evidence entries."""
        mock_model = AsyncMock()
        mock_model.predict.return_value = DeepfakeModelResult(
            is_deepfake_probability=0.8,
            facial_landmark_jitter=0.7,
            lip_sync_score=0.6,
            compression_artifact_score=0.5,
            temporal_flicker_score=0.4,
            face_count=1,
            frames_analyzed=50,
            raw_scores={},
        )
        mock_get_model.return_value = mock_model

        agent = DeepfakeDetectionAgent()
        agent._model = mock_model

        result = await agent.analyze("test.mp4", metadata={"input_type": "video"})
        assert len(result.evidence) >= 3  # At least landmark, lip-sync, compression
        assert any("landmark" in e.finding.lower() for e in result.evidence)

    @patch("app.agents.deepfake_agent.get_deepfake_model")
    async def test_error_handling(self, mock_get_model):
        """Agent returns safe error result on failure, doesn't crash."""
        mock_model = AsyncMock()
        mock_model.predict.side_effect = RuntimeError("Model crashed")
        mock_get_model.return_value = mock_model

        agent = DeepfakeDetectionAgent()
        agent._model = mock_model

        result = await agent.analyze("bad_file.mp4", metadata={"input_type": "video"})
        assert result.confidence_score == 0.0
        assert result.error is not None
        assert "failed" in result.result.lower() or "error" in result.result.lower()
