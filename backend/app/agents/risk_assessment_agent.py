"""
Risk Assessment Agent (3e)

Combines all upstream agent results into:
- fraud_probability (0-1)
- confidence_score
- explainable_reasoning (LLM-generated, grounded in agent outputs — cannot override computed score)
- recommended_action (IGNORE_SAFE / WARN_USER / BLOCK_AND_REPORT / ESCALATE_TO_SEBI)

Uses a transparent weighted-scoring model, then an LLM to synthesize the explanation.
"""

from __future__ import annotations

import logging
from typing import Any

from app.agents.base import BaseAgent
from app.adapters.llm_provider import get_llm_provider
from app.config import settings
from app.core.observability import traced_agent
from app.models.enums import AgentType, RecommendedAction
from app.models.schemas import (
    AgentResult,
    DeepfakeResult,
    DocumentResult,
    Evidence,
    PhishingResult,
    RiskAssessmentResult,
    VoiceResult,
)

logger = logging.getLogger(__name__)


class RiskAssessmentAgent(BaseAgent):
    """Agent 3e: Risk assessment — combines all upstream agent results."""

    @property
    def agent_type(self) -> AgentType:
        return AgentType.RISK_ASSESSMENT

    def __init__(self):
        self._llm = get_llm_provider()

    @traced_agent("risk_assessment")
    async def _analyze_impl(self, input_path: str, metadata: dict[str, Any]) -> RiskAssessmentResult:
        """Compute weighted risk score and generate LLM explanation."""
        evidence: list[Evidence] = []
        raw_output: dict[str, Any] = {}

        # Collect agent results from metadata
        agent_results: dict[AgentType, AgentResult] = {}
        if metadata.get("deepfake_result"):
            agent_results[AgentType.DEEPFAKE] = metadata["deepfake_result"]
        if metadata.get("voice_result"):
            agent_results[AgentType.VOICE] = metadata["voice_result"]
        if metadata.get("document_result"):
            agent_results[AgentType.DOCUMENT] = metadata["document_result"]
        if metadata.get("phishing_result"):
            agent_results[AgentType.PHISHING] = metadata["phishing_result"]

        agents_used = list(agent_results.keys())
        raw_output["agents_used"] = [a.value for a in agents_used]

        if not agent_results:
            return RiskAssessmentResult(
                result="No agent results available for risk assessment",
                confidence_score=0.0,
                evidence=[Evidence(finding="No upstream agents produced results", severity="info")],
                raw_model_output=raw_output,
                fraud_probability=0.0,
                recommended_action=RecommendedAction.IGNORE_SAFE,
                agents_used=[],
            )

        # ── 1. Weighted Scoring Model ────────────────────────────────────
        # Weights are configurable via settings
        weight_map = {
            AgentType.DEEPFAKE: settings.WEIGHT_DEEPFAKE,
            AgentType.VOICE: settings.WEIGHT_VOICE,
            AgentType.DOCUMENT: settings.WEIGHT_DOCUMENT,
            AgentType.PHISHING: settings.WEIGHT_PHISHING,
        }

        # Normalize weights to applicable agents only
        applicable_weights = {k: v for k, v in weight_map.items() if k in agent_results}
        total_weight = sum(applicable_weights.values())
        if total_weight > 0:
            normalized_weights = {k: v / total_weight for k, v in applicable_weights.items()}
        else:
            normalized_weights = {k: 1.0 / len(agent_results) for k in agent_results}

        # Compute weighted score
        weighted_scores: dict[str, float] = {}
        fraud_probability = 0.0

        for agent_type, result in agent_results.items():
            weight = normalized_weights.get(agent_type, 0)
            weighted_score = result.confidence_score * weight
            weighted_scores[agent_type.value] = weighted_score
            fraud_probability += weighted_score

            evidence.append(Evidence(
                finding=f"{agent_type.value}: confidence={result.confidence_score:.2f}, weight={weight:.2f}, contribution={weighted_score:.3f}",
                severity="info",
                detail={
                    "agent": agent_type.value,
                    "confidence": result.confidence_score,
                    "weight": weight,
                    "weighted_score": weighted_score,
                    "key_findings": [e.finding for e in result.evidence[:3]],
                },
            ))

        fraud_probability = min(fraud_probability, 1.0)
        raw_output["weighted_scores"] = weighted_scores
        raw_output["fraud_probability"] = fraud_probability

        # ── 2. Determine Recommended Action ──────────────────────────────
        if fraud_probability > 0.8:
            recommended_action = RecommendedAction.ESCALATE_TO_SEBI
        elif fraud_probability > 0.6:
            recommended_action = RecommendedAction.BLOCK_AND_REPORT
        elif fraud_probability > 0.3:
            recommended_action = RecommendedAction.WARN_USER
        else:
            recommended_action = RecommendedAction.IGNORE_SAFE

        # ── 3. LLM Explanation (grounded in agent outputs) ───────────────
        # The LLM synthesizes the explanation but CANNOT override the computed score
        explanation = await self._generate_explanation(
            agent_results=agent_results,
            weighted_scores=weighted_scores,
            fraud_probability=fraud_probability,
            recommended_action=recommended_action,
        )
        raw_output["llm_explanation_raw"] = explanation

        # Overall confidence = how much data we had to work with
        data_coverage = len(agent_results) / 4.0  # 4 possible agents
        confidence_score = min(fraud_probability * data_coverage * 1.5, 1.0)

        if fraud_probability > 0.6:
            result_text = f"HIGH RISK — fraud probability {fraud_probability:.1%}. Recommended action: {recommended_action.value}"
        elif fraud_probability > 0.3:
            result_text = f"MODERATE RISK — fraud probability {fraud_probability:.1%}. Recommended action: {recommended_action.value}"
        else:
            result_text = f"LOW RISK — fraud probability {fraud_probability:.1%}. Content appears largely safe."

        return RiskAssessmentResult(
            result=result_text,
            confidence_score=confidence_score,
            evidence=evidence,
            raw_model_output=raw_output,
            fraud_probability=fraud_probability,
            recommended_action=recommended_action,
            explainable_reasoning=explanation,
            weighted_scores=weighted_scores,
            agents_used=agents_used,
        )

    async def _generate_explanation(
        self,
        agent_results: dict[AgentType, AgentResult],
        weighted_scores: dict[str, float],
        fraud_probability: float,
        recommended_action: RecommendedAction,
    ) -> str:
        """Use LLM to generate a human-readable explanation grounded in agent outputs.

        The LLM must not invent evidence — it can only cite what agents actually found.
        """
        # Build context for the LLM
        agent_summaries = []
        for agent_type, result in agent_results.items():
            findings = [e.finding for e in result.evidence]
            agent_summaries.append(
                f"**{agent_type.value.upper()} Agent** (confidence: {result.confidence_score:.2f}):\n"
                f"  Summary: {result.result}\n"
                f"  Key findings: {'; '.join(findings[:5]) if findings else 'No specific findings'}"
            )

        # Retrieve regulatory context via RAG
        rag_context_str = ""
        try:
            from app.rag.pipeline.rag_pipeline import RAGPipeline
            rag_pipeline = RAGPipeline()
            query_str = " ".join([r.result for r in agent_results.values()])
            rag_results = rag_pipeline.retrieve_context(query_str, top_k=2)
            rag_context_str = RAGPipeline._format_context(rag_results)
        except Exception as e:
            logger.debug("RAG lookup in risk assessment skipped: %s", e)

        prompt = f"""You are a senior SEBI fraud analysis expert. Based on the agent analysis results and official regulatory guidelines, 
write a clear, concise explanation of why this content was assigned a fraud probability of {fraud_probability:.1%} 
and recommended action of "{recommended_action.value}".

OFFICIAL REGULATORY CONTEXT (RAG):
{rag_context_str if rag_context_str else "No specific regulatory circular matched."}

AGENT ANALYSIS RESULTS:
{chr(10).join(agent_summaries)}

Weighted Scores: {weighted_scores}
Final Fraud Probability: {fraud_probability:.3f}
Recommended Action: {recommended_action.value}

CRITICAL RULES:
1. Ground your reasoning strictly in the provided agent findings and official regulatory context.
2. Do NOT invent evidence.
3. Be specific — reference exact scores and findings.
4. Keep explanation under 300 words.

Write the explanation:"""

        system_prompt = (
            "You are a SEBI fraud analysis assistant. You explain fraud detection results "
            "to investigators and users in clear, professional language. You never invent "
            "evidence — you only cite what the detection agents actually found."
        )

        try:
            response = await self._llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                max_tokens=1024,
                temperature=0.1,
            )
            return response.content
        except Exception as e:
            logger.error("LLM explanation generation failed: %s", e)
            # Fallback: structured template explanation
            findings_text = "; ".join(
                f"{at.value}: {r.result}"
                for at, r in agent_results.items()
            )
            return (
                f"Risk Assessment: Fraud probability {fraud_probability:.1%}. "
                f"Based on {len(agent_results)} agent(s): {findings_text}. "
                f"Recommended action: {recommended_action.value}."
            )
