"""
Unit tests for the Voice Analysis Agent.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.agents.voice_agent import VoiceAnalysisAgent
from app.models.enums import AgentType
from app.models.schemas import VoiceResult


@pytest.mark.asyncio
class TestVoiceAgent:
    """Tests for VoiceAnalysisAgent."""

    async def test_agent_type(self):
        agent = VoiceAnalysisAgent()
        assert agent.agent_type == AgentType.VOICE

    @patch("app.agents.voice_agent.VoiceAnalysisAgent._extract_audio_from_video")
    async def test_analyze_returns_voice_result_shape(self, mock_extract):
        """Agent returns properly shaped result even when librosa is mocked."""
        mock_extract.return_value = (None, None)

        agent = VoiceAnalysisAgent()
        result = await agent.analyze("test.mp4", metadata={"input_type": "video"})

        assert result.agent_type == AgentType.VOICE
        assert 0.0 <= result.confidence_score <= 1.0
        assert result.result
        assert isinstance(result.evidence, list)
        assert isinstance(result.raw_model_output, dict)

    async def test_error_handling_returns_safe_result(self):
        """Agent handles errors gracefully without crashing."""
        agent = VoiceAnalysisAgent()
        # Analyzing a non-existent file
        result = await agent.analyze("nonexistent_file.wav", metadata={"input_type": "audio"})

        assert result.confidence_score == 0.0
        assert isinstance(result.evidence, list)

    async def test_execution_time_recorded(self):
        """Execution time is recorded in the result."""
        agent = VoiceAnalysisAgent()
        result = await agent.analyze("test.wav", metadata={"input_type": "audio"})
        assert result.execution_time_ms >= 0
