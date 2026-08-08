"""
Decision Engine (STEP 4)

Maps risk assessment output to final classification:
- Classification: Genuine | Suspicious | Fraudulent
- ThreatSeverity: Low | Medium | High | Critical
- Evidence breakdown showing per-agent contribution
- Reasoning chain showing which agents fired, their scores, and how they were weighted

The Decision Engine shows its reasoning chain — not just a final label.
"""

from __future__ import annotations

import logging
from typing import Any

from app.config import settings
from app.models.enums import AgentType, Classification, ThreatSeverity
from app.models.schemas import (
    AgentContribution,
    DecisionResult,
    RiskAssessmentResult,
)

logger = logging.getLogger(__name__)

# Score thresholds for classification
CLASSIFICATION_THRESHOLDS = {
    "fraudulent": 0.65,
    "suspicious": 0.30,
}

SEVERITY_THRESHOLDS = {
    "critical": 0.80,
    "high": 0.60,
    "medium": 0.35,
}


class DecisionEngine:
    """Translates Risk Assessment output into the final verdict with full reasoning chain."""

    def decide(
        self,
        risk_assessment: RiskAssessmentResult | None,
        agent_results: dict[str, Any] | None = None,
    ) -> DecisionResult:
        """Produce the final decision from the risk assessment.

        Args:
            risk_assessment: Output from the Risk Assessment Agent.
            agent_results: Raw dict of per-agent results for evidence breakdown.

        Returns:
            DecisionResult with classification, risk_score, severity, explanation,
            evidence_breakdown, and reasoning_chain.
        """
        if risk_assessment is None:
            return DecisionResult(
                classification=Classification.GENUINE,
                risk_score=0.0,
                threat_severity=ThreatSeverity.LOW,
                explanation="No risk assessment available — defaulting to Genuine.",
                evidence_breakdown={},
                reasoning_chain=["No risk assessment output available"],
            )

        risk_score = risk_assessment.fraud_probability
        reasoning_chain: list[str] = []

        # ── 1. Classification ────────────────────────────────────────────
        if risk_score >= CLASSIFICATION_THRESHOLDS["fraudulent"]:
            classification = Classification.FRAUDULENT
            reasoning_chain.append(
                f"Risk score {risk_score:.3f} >= {CLASSIFICATION_THRESHOLDS['fraudulent']} → FRAUDULENT"
            )
        elif risk_score >= CLASSIFICATION_THRESHOLDS["suspicious"]:
            classification = Classification.SUSPICIOUS
            reasoning_chain.append(
                f"Risk score {risk_score:.3f} >= {CLASSIFICATION_THRESHOLDS['suspicious']} → SUSPICIOUS"
            )
        else:
            classification = Classification.GENUINE
            reasoning_chain.append(
                f"Risk score {risk_score:.3f} < {CLASSIFICATION_THRESHOLDS['suspicious']} → GENUINE"
            )

        # ── 2. Threat Severity ───────────────────────────────────────────
        if risk_score >= SEVERITY_THRESHOLDS["critical"]:
            threat_severity = ThreatSeverity.CRITICAL
        elif risk_score >= SEVERITY_THRESHOLDS["high"]:
            threat_severity = ThreatSeverity.HIGH
        elif risk_score >= SEVERITY_THRESHOLDS["medium"]:
            threat_severity = ThreatSeverity.MEDIUM
        else:
            threat_severity = ThreatSeverity.LOW

        reasoning_chain.append(f"Threat severity determined: {threat_severity.value}")

        # ── 3. Evidence Breakdown ────────────────────────────────────────
        evidence_breakdown: dict[str, AgentContribution] = {}
        agent_results = agent_results or {}

        # Weight map
        weight_map = {
            "deepfake": settings.WEIGHT_DEEPFAKE,
            "voice": settings.WEIGHT_VOICE,
            "document": settings.WEIGHT_DOCUMENT,
            "phishing": settings.WEIGHT_PHISHING,
        }

        # Normalize weights to only agents that ran
        active_agents = [k for k in weight_map if k in agent_results]
        total_weight = sum(weight_map[k] for k in active_agents) or 1.0

        for agent_name in active_agents:
            agent_data = agent_results[agent_name]
            raw_weight = weight_map[agent_name]
            normalized_weight = raw_weight / total_weight
            raw_confidence = agent_data.get("confidence_score", 0.0)
            weighted_score = raw_confidence * normalized_weight

            # Extract key findings
            key_findings = []
            for ev in agent_data.get("evidence", [])[:3]:
                if isinstance(ev, dict):
                    key_findings.append(ev.get("finding", ""))
                elif hasattr(ev, "finding"):
                    key_findings.append(ev.finding)

            agent_type = AgentType(agent_name)
            evidence_breakdown[agent_name] = AgentContribution(
                agent_type=agent_type,
                weight=normalized_weight,
                raw_confidence=raw_confidence,
                weighted_score=weighted_score,
                key_findings=key_findings,
            )

            reasoning_chain.append(
                f"Agent '{agent_name}': confidence={raw_confidence:.3f} × weight={normalized_weight:.3f} "
                f"= contribution={weighted_score:.4f}"
            )

        # ── 4. Explanation ───────────────────────────────────────────────
        reasoning_chain.append(
            f"Final risk score: {risk_score:.3f} → "
            f"Classification: {classification.value}, "
            f"Severity: {threat_severity.value}, "
            f"Recommended: {risk_assessment.recommended_action.value}"
        )

        explanation = risk_assessment.explainable_reasoning
        if not explanation:
            # Fallback: build from reasoning chain
            explanation = " | ".join(reasoning_chain)

        logger.info(
            "Decision: case=%s classification=%s risk=%.3f severity=%s",
            "unknown",
            classification.value,
            risk_score,
            threat_severity.value,
        )

        return DecisionResult(
            classification=classification,
            risk_score=risk_score,
            threat_severity=threat_severity,
            explanation=explanation,
            evidence_breakdown=evidence_breakdown,
            reasoning_chain=reasoning_chain,
        )
