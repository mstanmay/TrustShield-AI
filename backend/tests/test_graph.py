"""
Unit tests for Phase 6 Neo4j Fraud Intelligence Graph — driver, repository, traversal, analytics, and APIs.
"""

from __future__ import annotations

import pytest

from app.graph.algorithms import GraphAnalyticsEngine
from app.graph.driver import get_neo4j_driver
from app.graph.repository import FraudGraphRepository
from app.graph.schemas import GraphEdge, GraphNode
from app.graph.traversal import GraphTraversalEngine


class TestFraudGraph:
    """Unit tests for Neo4j Fraud Intelligence Graph architecture."""

    def test_driver_singleton(self):
        driver1 = get_neo4j_driver()
        driver2 = get_neo4j_driver()
        assert driver1 is driver2

    def test_create_nodes_and_edges(self):
        repo = FraudGraphRepository()

        node1 = GraphNode(id="WALLET-001", label="Wallet", name="0x71C...49A", properties={"chain": "Polygon"}, risk_score=0.91)
        node2 = GraphNode(id="CAMPAIGN-77", label="ScamCampaign", name="Crypto Staking Mule Scam", risk_score=0.96)
        edge = GraphEdge(source_id="WALLET-001", target_id="CAMPAIGN-77", relationship_type="OPERATES", confidence=0.98)

        repo.create_node(node1)
        repo.create_node(node2)
        repo.create_edge(edge)

        subgraph = repo.get_full_network()
        assert subgraph.total_nodes >= 6
        assert any(n.id == "WALLET-001" for n in subgraph.nodes)

    def test_2hop_neighborhood_traversal(self):
        traversal = GraphTraversalEngine()
        subgraph = traversal.get_entity_neighborhood(entity_id="ENT-9012", hops=2)

        assert subgraph.total_nodes >= 2
        assert any(n.id == "ENT-9012" for n in subgraph.nodes)

    def test_shortest_path_discovery(self):
        traversal = GraphTraversalEngine()
        path = traversal.find_shortest_path(source_id="ENT-3310", target_id="ENT-001")

        assert isinstance(path, list)
        assert len(path) >= 1

    def test_community_detection_and_entity_resolution(self):
        analytics = GraphAnalyticsEngine()
        clusters = analytics.detect_communities()
        assert len(clusters) >= 1
        assert clusters[0].risk_level in ["CRITICAL", "HIGH"]

        resolution = analytics.resolve_entity("+919876543210")
        assert resolution.match_confidence > 0.8
        assert resolution.resolution_type == "EXACT_IDENTIFIER_MATCH"
