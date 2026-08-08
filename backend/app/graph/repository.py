"""
Neo4j Graph Repository — Cypher query execution for Node & Edge persistence and entity creation.
"""

from __future__ import annotations

import logging
from typing import Any

from app.graph.driver import get_neo4j_driver
from app.graph.schemas import GraphEdge, GraphNode, SubGraph

logger = logging.getLogger(__name__)


class FraudGraphRepository:
    """Repository managing Cypher persistence for fraud entities and relationship edges."""

    def __init__(self):
        self.gdriver = get_neo4j_driver()
        self._seed_sample_fraud_network()

    def _seed_sample_fraud_network(self):
        """Seed initial fraud intelligence network nodes and edges."""
        sample_nodes = [
            GraphNode(id="ENT-8942", label="Victim", name="Apex Capital FPI", properties={"type": "FPI Entity"}, risk_score=0.88),
            GraphNode(id="ENT-3310", label="PhoneNumber", name="+919876543210", properties={"carrier": "Jio", "type": "Sub-Account"}, risk_score=0.74),
            GraphNode(id="ENT-9012", label="TelegramGroup", name="Bulls_Hub_VIP", properties={"members": 14200, "channel": "Telegram"}, risk_score=0.94),
            GraphNode(id="ENT-1104", label="Domain", name="fake-sebi-portal.com", properties={"registrar": "NameCheap", "ssl": "Invalid"}, risk_score=0.82),
            GraphNode(id="ENT-001", label="ScamCampaign", name="XYZTECH Guaranteed Pump Campaign", properties={"status": "Active"}, risk_score=0.95),
            GraphNode(id="CASE-001", label="Case", name="Case #CASE-001", properties={"status": "COMPLETED"}, risk_score=0.85),
        ]

        sample_edges = [
            GraphEdge(source_id="ENT-9012", target_id="ENT-001", relationship_type="OPERATES", confidence=0.95),
            GraphEdge(source_id="ENT-1104", target_id="ENT-001", relationship_type="HOSTED_ON", confidence=0.90),
            GraphEdge(source_id="ENT-3310", target_id="ENT-9012", relationship_type="LINKED_TO", confidence=0.85),
            GraphEdge(source_id="ENT-8942", target_id="ENT-001", relationship_type="TARGETS", confidence=0.92),
            GraphEdge(source_id="CASE-001", target_id="ENT-001", relationship_type="LINKED_TO", confidence=1.0),
            GraphEdge(source_id="CASE-001", target_id="ENT-1104", relationship_type="LINKED_TO", confidence=1.0),
        ]

        for n in sample_nodes:
            self.create_node(n)

        for e in sample_edges:
            self.create_edge(e)

    def create_node(self, node: GraphNode) -> GraphNode:
        """Create or update a GraphNode in Neo4j (or local memory store)."""
        if self.gdriver.is_connected and self.gdriver.driver:
            query = (
                f"MERGE (n:{node.label} {{id: $id}}) "
                f"SET n.name = $name, n.risk_score = $risk_score, n += $properties "
                f"RETURN n"
            )
            try:
                with self.gdriver.driver.session() as session:
                    session.run(query, id=node.id, name=node.name, risk_score=node.risk_score, properties=node.properties)
            except Exception as e:
                logger.warning("Cypher query failed: %s — using memory graph store", e)

        # Fallback memory store
        self.gdriver._local_nodes[node.id] = node.model_dump()
        return node

    def create_edge(self, edge: GraphEdge) -> GraphEdge:
        """Create or update a GraphEdge relationship between two nodes."""
        if self.gdriver.is_connected and self.gdriver.driver:
            query = (
                f"MATCH (a {{id: $source_id}}), (b {{id: $target_id}}) "
                f"MERGE (a)-[r:{edge.relationship_type}]->(b) "
                f"SET r.confidence = $confidence, r += $properties "
                f"RETURN r"
            )
            try:
                with self.gdriver.driver.session() as session:
                    session.run(
                        query,
                        source_id=edge.source_id,
                        target_id=edge.target_id,
                        confidence=edge.confidence,
                        properties=edge.properties,
                    )
            except Exception as e:
                logger.warning("Cypher edge query failed: %s — using memory graph store", e)

        # Fallback memory store
        self.gdriver._local_edges.append(edge.model_dump())
        return edge

    def get_case_subgraph(self, case_id: str) -> SubGraph:
        """Fetch entity relationship subgraph for a specific case."""
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []

        for n_dict in self.gdriver._local_nodes.values():
            nodes.append(GraphNode(**n_dict))

        for e_dict in self.gdriver._local_edges:
            if e_dict["source_id"] == case_id or e_dict["target_id"] == case_id or case_id == "CASE-001":
                edges.append(GraphEdge(**e_dict))

        return SubGraph(
            case_id=case_id,
            nodes=nodes,
            edges=edges,
            total_nodes=len(nodes),
            total_edges=len(edges),
        )

    def get_full_network(self) -> SubGraph:
        """Fetch complete cross-case fraud intelligence network graph."""
        nodes = [GraphNode(**n) for n in self.gdriver._local_nodes.values()]
        edges = [GraphEdge(**e) for e in self.gdriver._local_edges]

        return SubGraph(
            case_id=None,
            nodes=nodes,
            edges=edges,
            total_nodes=len(nodes),
            total_edges=len(edges),
        )
