"""
Graph Schemas — Pydantic models for Graph Nodes, Edges, Subgraphs, and Fraud Networks.
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class GraphNode(BaseModel):
    """Represents an entity node in the Neo4j fraud graph."""
    id: str
    label: str  # Victim | Email | URL | Domain | Wallet | PhoneNumber | TelegramGroup | WhatsAppGroup | ScamCampaign | Case
    name: str
    properties: dict[str, Any] = Field(default_factory=dict)
    risk_score: float = Field(default=0.0, ge=0.0, le=1.0)


class GraphEdge(BaseModel):
    """Represents a relationship edge between two entity nodes."""
    source_id: str
    target_id: str
    relationship_type: str  # TARGETS | OPERATES | LINKED_TO | HOSTED_ON | PART_OF | SUSPECTED_BY
    properties: dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class SubGraph(BaseModel):
    """Subgraph payload for a case or entity neighborhood."""
    case_id: str | None = None
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    total_nodes: int
    total_edges: int


class EntityResolutionResult(BaseModel):
    """Result of entity resolution cross-case matching."""
    primary_entity_id: str
    linked_entity_ids: list[str]
    match_confidence: float
    resolution_type: str
    shared_identifiers: list[str]


class CommunityCluster(BaseModel):
    """Community detection cluster representing an organized scam campaign hub."""
    cluster_id: str
    campaign_name: str
    member_nodes: list[GraphNode]
    primary_threat_type: str
    risk_level: str
