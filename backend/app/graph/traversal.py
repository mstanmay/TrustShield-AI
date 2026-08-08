"""
Graph Traversal Engine — K-hop neighborhood discovery and shortest path entity correlation.
"""

from __future__ import annotations

import logging
from typing import Any

from app.graph.repository import FraudGraphRepository
from app.graph.schemas import GraphEdge, GraphNode, SubGraph

logger = logging.getLogger(__name__)


class GraphTraversalEngine:
    """Performs graph traversal queries and entity neighborhood discovery."""

    def __init__(self):
        self.repo = FraudGraphRepository()

    def get_entity_neighborhood(self, entity_id: str, hops: int = 2) -> SubGraph:
        """Fetch K-hop neighborhood subgraph surrounding an entity ID."""
        full_network = self.repo.get_full_network()

        visited_nodes: set[str] = {entity_id}
        frontier: set[str] = {entity_id}

        for _ in range(hops):
            next_frontier: set[str] = set()
            for edge in full_network.edges:
                if edge.source_id in frontier:
                    next_frontier.add(edge.target_id)
                elif edge.target_id in frontier:
                    next_frontier.add(edge.source_id)
            visited_nodes.update(next_frontier)
            frontier = next_frontier

        sub_nodes = [n for n in full_network.nodes if n.id in visited_nodes]
        sub_edges = [
            e for e in full_network.edges
            if e.source_id in visited_nodes and e.target_id in visited_nodes
        ]

        return SubGraph(
            case_id=entity_id,
            nodes=sub_nodes,
            edges=sub_edges,
            total_nodes=len(sub_nodes),
            total_edges=len(sub_edges),
        )

    def find_shortest_path(self, source_id: str, target_id: str) -> list[GraphEdge]:
        """Find shortest relationship path between two entities in the graph."""
        full_network = self.repo.get_full_network()

        # BFS shortest path search
        queue = [[source_id]]
        visited = {source_id}

        while queue:
            path = queue.pop(0)
            node = path[-1]
            if node == target_id:
                # Reconstruct edges along path
                edge_path = []
                for i in range(len(path) - 1):
                    u, v = path[i], path[i+1]
                    for e in full_network.edges:
                        if (e.source_id == u and e.target_id == v) or (e.source_id == v and e.target_id == u):
                            edge_path.append(e)
                            break
                return edge_path

            for e in full_network.edges:
                neighbor = None
                if e.source_id == node:
                    neighbor = e.target_id
                elif e.target_id == node:
                    neighbor = e.source_id

                if neighbor and neighbor not in visited:
                    visited.add(neighbor)
                    new_path = list(path)
                    new_path.append(neighbor)
                    queue.append(new_path)

        return []
