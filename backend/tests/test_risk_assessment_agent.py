"""
Unit tests for the Risk Assessment Agent.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.agents.risk_assessment_agent import RiskAssessmentAgent
from app.models.enums import AgentType, RecommendedAction
from app.models.schemas import RiskAssessmentResult


@pytest.mark.asyncio
class TestRiskAssessmentAgent:
    """Tests for RiskAssessmentAgent."""

    async def test_agent_type(self):
        agent = RiskAssessmentAgent()
        assert agent.agent_type == AgentType.RISK_ASSESSMENT

    async def test_weighted_scoring(self, all_agent_results):
        """Agent computes weighted score from upstream results."""
        agent = RiskAssessmentAgent()
        result = await agent.analyze("", metadata=all_agent_results)

        assert isinstance(result, RiskAssessmentResult)
        assert 0.0 <= result.fraud_probability <= 1.0
        assert 0.0 <= result.confidence_score <= 1.0
        assert result.recommended_action in RecommendedAction
        assert len(result.weighted_scores) > 0
        assert len(result.agents_used) > 0

    async def test_no_results_returns_safe(self):
        """Agent returns safe result when no upstream results are available."""
        agent = RiskAssessmentAgent()
        result = await agent.analyze("", metadata={})

        assert result.fraud_probability == 0.0
        assert result.recommended_action == RecommendedAction.IGNORE_SAFE

    async def test_high_risk_triggers_escalation(self, sample_phishing_result):
        """High-confidence phishing result should trigger escalation."""
        # Create a high-confidence phishing result
        sample_phishing_result.confidence_score = 0.95
        agent = RiskAssessmentAgent()
        result = await agent.analyze(
            "",
            metadata={"phishing_result": sample_phishing_result},
        )

        assert result.fraud_probability > 0.5
        assert result.recommended_action in (
            RecommendedAction.BLOCK_AND_REPORT,
            RecommendedAction.ESCALATE_TO_SEBI,
        )

    async def test_explanation_generated(self, all_agent_results):
        """Agent generates a non-empty explanation."""
        agent = RiskAssessmentAgent()
        result = await agent.analyze("", metadata=all_agent_results)

        assert result.explainable_reasoning  # Non-empty
        assert len(result.explainable_reasoning) > 20

    async def test_evidence_shows_per_agent_contribution(self, all_agent_results):
        """Evidence includes per-agent weighted contribution breakdown."""
        agent = RiskAssessmentAgent()
        result = await agent.analyze("", metadata=all_agent_results)

        # Should have evidence entries for each agent
        assert len(result.evidence) >= 3
        agent_findings = [e.detail.get("agent") for e in result.evidence if e.detail.get("agent")]
        assert len(agent_findings) > 0
