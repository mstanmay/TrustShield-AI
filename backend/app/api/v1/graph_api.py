"""
Fraud Intelligence Graph API Router — endpoints:
- GET /api/v1/graph/case
- GET /api/v1/graph/entity
- GET /api/v1/graph/network
- GET /api/v1/graph/communities
- GET /api/v1/graph/resolve
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, status

from app.graph.algorithms import GraphAnalyticsEngine
from app.graph.repository import FraudGraphRepository
from app.graph.schemas import CommunityCluster, EntityResolutionResult, SubGraph
from app.graph.traversal import GraphTraversalEngine

router = APIRouter(prefix="/api/v1/graph", tags=["fraud-graph"])


@router.get("/case", response_model=SubGraph)
async def get_case_graph(
    case_id: str = Query(..., min_length=1, description="Case ID or reference number"),
):
    """Retrieve entity relationship subgraph for a specific case."""
    repo = FraudGraphRepository()
    return repo.get_case_subgraph(case_id)


@router.get("/entity", response_model=SubGraph)
async def get_entity_neighborhood(
    entity_id: str = Query(..., min_length=1, description="Entity Node ID (e.g. ENT-9012 or phone/URL)"),
    hops: int = Query(2, ge=1, le=5),
):
    """Retrieve K-hop neighborhood graph surrounding a specific entity."""
    traversal = GraphTraversalEngine()
    return traversal.get_entity_neighborhood(entity_id=entity_id, hops=hops)


@router.get("/network", response_model=SubGraph)
async def get_full_network():
    """Retrieve complete cross-case fraud intelligence network for UI visualization."""
    repo = FraudGraphRepository()
    return repo.get_full_network()


@router.get("/communities", response_model=list[CommunityCluster])
async def get_scam_communities():
    """Retrieve detected scam campaign communities (Louvain clusters)."""
    analytics = GraphAnalyticsEngine()
    return analytics.detect_communities()


@router.get("/resolve", response_model=EntityResolutionResult)
async def resolve_entity(
    identifier: str = Query(..., min_length=1, description="Entity phone, email, URL, or domain to resolve"),
):
    """Resolve an entity identifier across multiple cases and return cross-case links."""
    analytics = GraphAnalyticsEngine()
    return analytics.resolve_entity(identifier)
