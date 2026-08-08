"""
LangGraph Orchestrator — StateGraph definition with nodes, edges, and conditional routing.

Graph structure:
  START → route_by_input_type
  route_by_input_type → [deepfake_node, voice_node, document_node, phishing_node] (conditional fan-out)
  [parallel agents] → join_results
  join_results → risk_assessment_node
  risk_assessment_node → decision_engine_node
  decision_engine_node → persist_results → END

Full execution trace is persisted per case for audit/explainability.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Any

from langgraph.graph import END, StateGraph

from app.agents.deepfake_agent import DeepfakeDetectionAgent
from app.agents.document_agent import DocumentVerificationAgent
from app.agents.phishing_agent import PhishingIntelligenceAgent
from app.agents.risk_assessment_agent import RiskAssessmentAgent
from app.agents.voice_agent import VoiceAnalysisAgent
from app.decision_engine.engine import DecisionEngine
from app.models.enums import AgentType, CaseStatus
from app.orchestrator.routing import determine_applicable_agents, should_run_agent
from app.orchestrator.state import GraphState

logger = logging.getLogger(__name__)


# ── Node Functions ───────────────────────────────────────────────────────────

async def route_node(state: GraphState) -> GraphState:
    """Determine which agents to invoke based on input type and metadata."""
    from app.models.enums import InputType

    input_type = state.get("input_type", "")
    metadata = state.get("metadata", {})

    agents = determine_applicable_agents(input_type, metadata)
    applicable = [a.value for a in agents]

    trace_entry = {
        "node": "route_by_input_type",
        "timestamp": datetime.utcnow().isoformat(),
        "input_type": input_type,
        "applicable_agents": applicable,
    }

    return {
        "applicable_agents": applicable,
        "status": CaseStatus.PROCESSING.value,
        "execution_trace": [trace_entry],
    }


async def deepfake_node(state: GraphState) -> dict:
    """Run the Deepfake Detection Agent."""
    if not should_run_agent(AgentType.DEEPFAKE, state.get("applicable_agents", [])):
        return {}

    start = time.time()
    agent = DeepfakeDetectionAgent()
    result = await agent.analyze(
        state.get("artifact_path", ""),
        metadata={"input_type": state.get("input_type", "")},
    )
    elapsed = time.time() - start

    trace_entry = {
        "node": "deepfake_agent",
        "timestamp": datetime.utcnow().isoformat(),
        "confidence_score": result.confidence_score,
        "execution_time_ms": elapsed * 1000,
        "evidence_count": len(result.evidence),
    }

    return {
        "deepfake_result": result.model_dump(),
        "execution_trace": [trace_entry],
    }


async def voice_node(state: GraphState) -> dict:
    """Run the Voice Analysis Agent."""
    if not should_run_agent(AgentType.VOICE, state.get("applicable_agents", [])):
        return {}

    start = time.time()
    agent = VoiceAnalysisAgent()
    result = await agent.analyze(
        state.get("artifact_path", ""),
        metadata={"input_type": state.get("input_type", "")},
    )
    elapsed = time.time() - start

    trace_entry = {
        "node": "voice_agent",
        "timestamp": datetime.utcnow().isoformat(),
        "confidence_score": result.confidence_score,
        "execution_time_ms": elapsed * 1000,
        "evidence_count": len(result.evidence),
    }

    return {
        "voice_result": result.model_dump(),
        "execution_trace": [trace_entry],
    }


async def document_node(state: GraphState) -> dict:
    """Run the OCR & Document Verification Agent."""
    if not should_run_agent(AgentType.DOCUMENT, state.get("applicable_agents", [])):
        return {}

    start = time.time()
    agent = DocumentVerificationAgent()
    metadata = {
        "input_type": state.get("input_type", ""),
        "text_content": state.get("metadata", {}).get("text_content"),
    }
    result = await agent.analyze(state.get("artifact_path", ""), metadata=metadata)
    elapsed = time.time() - start

    doc_result_dict = result.model_dump()
    trace_entry = {
        "node": "document_agent",
        "timestamp": datetime.utcnow().isoformat(),
        "confidence_score": result.confidence_score,
        "execution_time_ms": elapsed * 1000,
        "evidence_count": len(result.evidence),
        "urls_found": len(result.extracted_urls),
    }

    return {
        "document_result": doc_result_dict,
        "execution_trace": [trace_entry],
    }


async def phishing_node(state: GraphState) -> dict:
    """Run the Phishing Intelligence Agent."""
    if not should_run_agent(AgentType.PHISHING, state.get("applicable_agents", [])):
        return {}

    start = time.time()
    agent = PhishingIntelligenceAgent()
    metadata = {
        "input_type": state.get("input_type", ""),
        "url": state.get("metadata", {}).get("url"),
        "text_content": state.get("metadata", {}).get("text_content"),
        "extracted_urls": state.get("metadata", {}).get("extracted_urls", []),
    }
    result = await agent.analyze(state.get("artifact_path", ""), metadata=metadata)
    elapsed = time.time() - start

    trace_entry = {
        "node": "phishing_agent",
        "timestamp": datetime.utcnow().isoformat(),
        "confidence_score": result.confidence_score,
        "execution_time_ms": elapsed * 1000,
        "evidence_count": len(result.evidence),
        "urls_analyzed": len(result.analyzed_urls),
    }

    return {
        "phishing_result": result.model_dump(),
        "execution_trace": [trace_entry],
    }


async def join_results_node(state: GraphState) -> dict:
    """Join point after parallel agent execution."""
    trace_entry = {
        "node": "join_results",
        "timestamp": datetime.utcnow().isoformat(),
        "agents_completed": [
            k for k in ["deepfake_result", "voice_result", "document_result", "phishing_result"]
            if state.get(k) is not None
        ],
    }
    return {"execution_trace": [trace_entry]}


async def risk_assessment_node(state: GraphState) -> dict:
    """Run the Risk Assessment Agent on all completed upstream results."""
    start = time.time()
    agent = RiskAssessmentAgent()

    from app.models.schemas import DeepfakeResult, VoiceResult, DocumentResult, PhishingResult

    metadata: dict[str, Any] = {}
    if state.get("deepfake_result"):
        metadata["deepfake_result"] = DeepfakeResult(**state["deepfake_result"])
    if state.get("voice_result"):
        metadata["voice_result"] = VoiceResult(**state["voice_result"])
    if state.get("document_result"):
        metadata["document_result"] = DocumentResult(**state["document_result"])
    if state.get("phishing_result"):
        metadata["phishing_result"] = PhishingResult(**state["phishing_result"])

    result = await agent.analyze("", metadata=metadata)
    elapsed = time.time() - start

    trace_entry = {
        "node": "risk_assessment",
        "timestamp": datetime.utcnow().isoformat(),
        "fraud_probability": result.fraud_probability,
        "recommended_action": result.recommended_action.value,
        "execution_time_ms": elapsed * 1000,
    }

    return {
        "risk_assessment": result.model_dump(),
        "execution_trace": [trace_entry],
    }


async def decision_engine_node(state: GraphState) -> dict:
    """Run the Decision Engine to produce the final verdict."""
    start = time.time()
    engine = DecisionEngine()

    from app.models.schemas import RiskAssessmentResult
    risk_result = RiskAssessmentResult(**state["risk_assessment"]) if state.get("risk_assessment") else None

    agent_results: dict[str, Any] = {}
    for key in ["deepfake_result", "voice_result", "document_result", "phishing_result"]:
        if state.get(key):
            agent_results[key.replace("_result", "")] = state[key]

    verdict = engine.decide(risk_result, agent_results)
    elapsed = time.time() - start

    trace_entry = {
        "node": "decision_engine",
        "timestamp": datetime.utcnow().isoformat(),
        "classification": verdict.classification.value,
        "risk_score": verdict.risk_score,
        "threat_severity": verdict.threat_severity.value,
        "execution_time_ms": elapsed * 1000,
    }

    return {
        "final_verdict": verdict.model_dump(),
        "status": CaseStatus.COMPLETED.value,
        "execution_trace": [trace_entry],
    }


# ── Graph Builder ────────────────────────────────────────────────────────────

def build_analysis_graph() -> StateGraph:
    """Build the LangGraph StateGraph for the fraud detection pipeline.

    Flow:
        route → [deepfake, voice, document, phishing] (parallel fan-out)
             → join → risk_assessment → decision_engine → END
    """
    graph = StateGraph(GraphState)

    # Add nodes
    graph.add_node("route", route_node)
    graph.add_node("deepfake", deepfake_node)
    graph.add_node("voice", voice_node)
    graph.add_node("document", document_node)
    graph.add_node("phishing", phishing_node)
    graph.add_node("join_results", join_results_node)
    graph.add_node("risk_assessment", risk_assessment_node)
    graph.add_node("decision_engine", decision_engine_node)

    # Set entry point
    graph.set_entry_point("route")

    # After routing, fan out to all agent nodes
    # (each node self-checks if it should run via applicable_agents)
    graph.add_edge("route", "deepfake")
    graph.add_edge("route", "voice")
    graph.add_edge("route", "document")
    graph.add_edge("route", "phishing")

    # All agents converge at join
    graph.add_edge("deepfake", "join_results")
    graph.add_edge("voice", "join_results")
    graph.add_edge("document", "join_results")
    graph.add_edge("phishing", "join_results")

    # Join → Risk Assessment → Decision Engine → END
    graph.add_edge("join_results", "risk_assessment")
    graph.add_edge("risk_assessment", "decision_engine")
    graph.add_edge("decision_engine", END)

    return graph


def compile_graph():
    """Compile the analysis graph for execution."""
    graph = build_analysis_graph()
    return graph.compile()


async def run_pipeline(initial_state: dict[str, Any]) -> dict[str, Any]:
    """Execute the full analysis pipeline on a case.

    Args:
        initial_state: GraphState dict with case_id, input_type, artifact_path, metadata.

    Returns:
        Final GraphState with all results populated.
    """
    # Ensure required fields
    initial_state.setdefault("execution_trace", [])
    initial_state.setdefault("status", CaseStatus.PENDING.value)
    initial_state.setdefault("metadata", {})

    pipeline_start = {
        "node": "pipeline_start",
        "timestamp": datetime.utcnow().isoformat(),
        "case_id": initial_state.get("case_id"),
        "input_type": initial_state.get("input_type"),
    }
    initial_state["execution_trace"].append(pipeline_start)

    try:
        compiled = compile_graph()
        final_state = await compiled.ainvoke(initial_state)

        # Add pipeline completion trace
        final_state["execution_trace"].append({
            "node": "pipeline_complete",
            "timestamp": datetime.utcnow().isoformat(),
            "status": final_state.get("status"),
        })

        return final_state

    except Exception as e:
        logger.error("Pipeline execution failed for case %s: %s", initial_state.get("case_id"), e)
        initial_state["status"] = CaseStatus.FAILED.value
        initial_state["error_message"] = str(e)
        initial_state["execution_trace"].append({
            "node": "pipeline_error",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
        })
        return initial_state
