"""
Unit tests for the Decision Engine.
"""

from __future__ import annotations

import pytest

from app.decision_engine.engine import DecisionEngine
from app.models.enums import Classification, RecommendedAction, ThreatSeverity
from app.models.schemas import RiskAssessmentResult


class TestDecisionEngine:
    """Tests for DecisionEngine."""

    def test_genuine_classification(self):
        """Low risk score → Genuine classification."""
        engine = DecisionEngine()
        risk = RiskAssessmentResult(
            agent_type="risk_assessment",
            result="Low risk",
            confidence_score=0.1,
            evidence=[],
            raw_model_output={},
            fraud_probability=0.1,
            recommended_action=RecommendedAction.IGNORE_SAFE,
            explainable_reasoning="Low risk content",
        )
        verdict = engine.decide(risk, {})

        assert verdict.classification == Classification.GENUINE
        assert verdict.threat_severity == ThreatSeverity.LOW
        assert verdict.risk_score < 0.3

    def test_suspicious_classification(self):
        """Medium risk score → Suspicious classification."""
        engine = DecisionEngine()
        risk = RiskAssessmentResult(
            agent_type="risk_assessment",
            result="Medium risk",
            confidence_score=0.45,
            evidence=[],
            raw_model_output={},
            fraud_probability=0.45,
            recommended_action=RecommendedAction.WARN_USER,
            explainable_reasoning="Moderate risk indicators",
        )
        verdict = engine.decide(risk, {})

        assert verdict.classification == Classification.SUSPICIOUS
        assert verdict.threat_severity in (ThreatSeverity.MEDIUM, ThreatSeverity.HIGH)

    def test_fraudulent_classification(self):
        """High risk score → Fraudulent classification."""
        engine = DecisionEngine()
        risk = RiskAssessmentResult(
            agent_type="risk_assessment",
            result="High risk",
            confidence_score=0.85,
            evidence=[],
            raw_model_output={},
            fraud_probability=0.85,
            recommended_action=RecommendedAction.ESCALATE_TO_SEBI,
            explainable_reasoning="Multiple fraud indicators detected",
        )
        verdict = engine.decide(risk, {})

        assert verdict.classification == Classification.FRAUDULENT
        assert verdict.threat_severity == ThreatSeverity.CRITICAL
        assert verdict.risk_score >= 0.65

    def test_reasoning_chain_populated(self):
        """Decision includes a non-empty reasoning chain."""
        engine = DecisionEngine()
        risk = RiskAssessmentResult(
            agent_type="risk_assessment",
            result="Test",
            confidence_score=0.5,
            evidence=[],
            raw_model_output={},
            fraud_probability=0.5,
            recommended_action=RecommendedAction.WARN_USER,
        )
        verdict = engine.decide(risk, {"phishing": {"confidence_score": 0.6, "evidence": []}})

        assert len(verdict.reasoning_chain) >= 2
        assert any("risk score" in step.lower() for step in verdict.reasoning_chain)

    def test_evidence_breakdown_with_agents(self):
        """Evidence breakdown includes per-agent contributions when agent results are provided."""
        engine = DecisionEngine()
        risk = RiskAssessmentResult(
            agent_type="risk_assessment",
            result="Test",
            confidence_score=0.5,
            evidence=[],
            raw_model_output={},
            fraud_probability=0.5,
            recommended_action=RecommendedAction.WARN_USER,
        )
        agent_results = {
            "deepfake": {"confidence_score": 0.3, "evidence": []},
            "phishing": {"confidence_score": 0.7, "evidence": []},
        }
        verdict = engine.decide(risk, agent_results)

        assert "deepfake" in verdict.evidence_breakdown
        assert "phishing" in verdict.evidence_breakdown
        assert verdict.evidence_breakdown["phishing"].raw_confidence == 0.7

    def test_none_risk_assessment(self):
        """None risk assessment defaults to Genuine."""
        engine = DecisionEngine()
        verdict = engine.decide(None, {})

        assert verdict.classification == Classification.GENUINE
        assert verdict.risk_score == 0.0
