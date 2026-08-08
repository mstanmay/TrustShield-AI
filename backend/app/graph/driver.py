"""
Neo4j Graph Driver — manages Bolt protocol connections & in-memory graph database fallback.
"""

from __future__ import annotations

import logging
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)

try:
    from neo4j import GraphDatabase
    HAS_NEO4J_DRIVER = True
except ImportError:
    GraphDatabase = None
    HAS_NEO4J_DRIVER = False


class Neo4jGraphDriver:
    """Connection manager for Neo4j Fraud Intelligence Graph Database."""

    _instance: Neo4jGraphDriver | None = None

    def __init__(self):
        self.driver = None
        self.is_connected = False
        self._local_nodes: dict[str, dict[str, Any]] = {}
        self._local_edges: list[dict[str, Any]] = []

        if HAS_NEO4J_DRIVER:
            try:
                self.driver = GraphDatabase.driver(
                    settings.NEO4J_URI,
                    auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
                )
                # Verify connectivity
                self.driver.verify_connectivity()
                self.is_connected = True
                logger.info("Connected to Neo4j Graph Database at %s", settings.NEO4J_URI)
            except Exception as e:
                logger.warning("Neo4j connection unavailable (%s) — using memory graph store fallback", e)
                self.driver = None
                self.is_connected = False
        else:
            logger.info("neo4j package not installed — using memory graph store fallback")

    @classmethod
    def get_instance(cls) -> Neo4jGraphDriver:
        if cls._instance is None:
            cls._instance = Neo4jGraphDriver()
        return cls._instance

    def close(self):
        """Close Neo4j driver connection."""
        if self.driver:
            self.driver.close()
            self.is_connected = False
            logger.info("Neo4j graph driver closed")


def get_neo4j_driver() -> Neo4jGraphDriver:
    return Neo4jGraphDriver.get_instance()
