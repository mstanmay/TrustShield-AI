"""
Unit tests for the OCR & Document Verification Agent.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.agents.document_agent import DocumentVerificationAgent
from app.models.enums import AgentType
from app.models.schemas import DocumentResult


@pytest.mark.asyncio
class TestDocumentAgent:
    """Tests for DocumentVerificationAgent."""

    async def test_agent_type(self):
        agent = DocumentVerificationAgent()
        assert agent.agent_type == AgentType.DOCUMENT

    async def test_text_content_analysis(self):
        """Agent can analyze directly-provided text (WhatsApp/Telegram messages)."""
        agent = DocumentVerificationAgent()
        result = await agent.analyze(
            "",
            metadata={
                "input_type": "whatsapp_message",
                "text_content": (
                    "URGENT! Guaranteed returns of 100% in 30 days! "
                    "SEBI registered advisor. Contact +919876543210. "
                    "Visit https://fake-sebi.com/invest now. Limited time offer! "
                    "Act now or miss this once in a lifetime opportunity."
                ),
            },
        )

        assert isinstance(result, DocumentResult)
        assert result.confidence_score > 0.2  # Should flag urgency language
        assert result.ocr_text  # Text was captured
        assert len(result.evidence) > 0
        # Should detect urgency keywords
        assert any("urgency" in e.finding.lower() or "language" in e.finding.lower() for e in result.evidence)

    async def test_extracts_urls_from_text(self):
        """Agent extracts URLs from OCR/text content."""
        agent = DocumentVerificationAgent()
        result = await agent.analyze(
            "",
            metadata={
                "input_type": "whatsapp_message",
                "text_content": "Check out https://example.com and https://test.com/path",
            },
        )

        assert len(result.extracted_urls) >= 2

    async def test_extracts_phone_numbers(self):
        """Agent raw_model_output includes phone numbers found in text."""
        agent = DocumentVerificationAgent()
        result = await agent.analyze(
            "",
            metadata={
                "input_type": "whatsapp_message",
                "text_content": "Call me at 9876543210 or +919123456789",
            },
        )

        phone_numbers = result.raw_model_output.get("phone_numbers", [])
        assert len(phone_numbers) >= 1

    async def test_confidence_bounds(self):
        """Confidence score is always 0-1."""
        agent = DocumentVerificationAgent()
        result = await agent.analyze("", metadata={"text_content": "Hello world"})
        assert 0.0 <= result.confidence_score <= 1.0

    async def test_error_handling(self):
        """Agent handles missing file gracefully."""
        agent = DocumentVerificationAgent()
        result = await agent.analyze(
            "nonexistent.pdf",
            metadata={"input_type": "pdf"},
        )
        assert result.confidence_score == 0.0 or result.error is not None
