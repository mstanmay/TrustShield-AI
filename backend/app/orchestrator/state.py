"""
LangGraph orchestrator state — TypedDict form for LangGraph StateGraph compatibility.
Mirrors CaseState but uses TypedDict which LangGraph requires.
"""

from __future__ import annotations

import operator
from typing import Annotated, Any
from typing_extensions import TypedDict

from app.models.enums import AgentType, CaseStatus, InputType


class GraphState(TypedDict, total=False):
    """Shared state passed through LangGraph nodes.

    Uses TypedDict for LangGraph compatibility.
    Each node reads and updates relevant fields.
    """
    # Case identification
    case_id: str
    input_type: str  # InputType value
    artifact_path: str
    original_filename: str
    metadata: dict[str, Any]

    # Routing
    applicable_agents: list[str]  # AgentType values

    # Per-agent results (stored as serialized dicts)
    deepfake_result: dict[str, Any] | None
    voice_result: dict[str, Any] | None
    document_result: dict[str, Any] | None
    phishing_result: dict[str, Any] | None
    risk_assessment: dict[str, Any] | None
    final_verdict: dict[str, Any] | None

    # Status tracking
    status: str  # CaseStatus value
    error_message: str | None
    execution_trace: Annotated[list[dict[str, Any]], operator.add]

