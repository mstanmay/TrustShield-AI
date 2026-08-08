"""
Unit tests for the Phishing Intelligence Agent.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.agents.phishing_agent import PhishingIntelligenceAgent
from app.models.enums import AgentType
from app.models.schemas import PhishingResult


@pytest.mark.asyncio
class TestPhishingAgent:
    """Tests for PhishingIntelligenceAgent."""

    async def test_agent_type(self):
        agent = PhishingIntelligenceAgent()
        assert agent.agent_type == AgentType.PHISHING

    async def test_typosquatting_detection(self):
        """Agent detects typosquatting domains similar to SEBI."""
        agent = PhishingIntelligenceAgent()
        result = await agent.analyze(
            "",
            metadata={
                "url": "https://sebl.gov.in/login",
                "input_type": "url",
            },
        )

        assert isinstance(result, PhishingResult)
        assert result.confidence_score > 0.3  # Typosquatting should trigger
        assert len(result.typosquat_matches) > 0
        assert result.typosquat_matches[0]["known_domain"] == "sebi.gov.in"

    async def test_no_urls_returns_safe(self):
        """Agent handles no URLs gracefully."""
        agent = PhishingIntelligenceAgent()
        result = await agent.analyze("", metadata={"input_type": "url"})

        assert result.confidence_score == 0.0
        assert len(result.analyzed_urls) == 0

    async def test_url_extraction_from_text(self):
        """Agent extracts and analyzes URLs from text content."""
        agent = PhishingIntelligenceAgent()
        result = await agent.analyze(
            "",
            metadata={
                "input_type": "whatsapp_message",
                "text_content": "Click here: https://example-scam.com/login now!",
            },
        )

        assert len(result.analyzed_urls) >= 1
        assert "https://example-scam.com/login" in result.analyzed_urls

    async def test_levenshtein_distance(self):
        """Levenshtein distance computation is correct."""
        agent = PhishingIntelligenceAgent()
        assert agent._levenshtein_distance("sebi", "sebl") == 1
        assert agent._levenshtein_distance("sebi", "sebi") == 0
        assert agent._levenshtein_distance("sebi", "sbi") == 1
        assert agent._levenshtein_distance("sebi.gov.in", "sebl.gov.in") == 1

    async def test_suspicious_url_patterns(self):
        """Agent detects suspicious URL patterns (IP addresses, shorteners)."""
        agent = PhishingIntelligenceAgent()
        result = await agent.analyze(
            "",
            metadata={
                "url": "http://192.168.1.1/sebi/login?verify=true",
                "input_type": "url",
            },
        )

        assert result.confidence_score > 0.15
        # Should flag: raw IP, HTTP instead of HTTPS, contains "login" and "verify"
        findings = [e.finding.lower() for e in result.evidence]
        assert any("ip address" in f for f in findings)

    async def test_confidence_bounds(self):
        """Confidence score stays within 0-1."""
        agent = PhishingIntelligenceAgent()
        result = await agent.analyze(
            "",
            metadata={"url": "https://sebi.gov.in", "input_type": "url"},
        )
        assert 0.0 <= result.confidence_score <= 1.0
