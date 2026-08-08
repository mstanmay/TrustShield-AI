"""
Qdrant Vector Client — connection manager with Qdrant server connection & in-memory fallback.
"""

from __future__ import annotations

import logging
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)

try:
    from qdrant_client import QdrantClient
    from qdrant_client.http import models as rest_models
    HAS_QDRANT_CLIENT = True
except ImportError:
    QdrantClient = None
    rest_models = None
    HAS_QDRANT_CLIENT = False


class QdrantVectorClient:
    """Client connection manager for Qdrant Vector Database."""

    _instance: QdrantVectorClient | None = None

    def __init__(self):
        self.client = None
        self.is_connected = False
        self._local_fallback_store: dict[str, list[dict[str, Any]]] = {}

        if HAS_QDRANT_CLIENT:
            try:
                # Try connecting to Qdrant
                self.client = QdrantClient(
                    host=settings.QDRANT_HOST,
                    port=settings.QDRANT_PORT,
                    api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None,
                    timeout=3.0,
                )
                # Quick health check
                self.client.get_collections()
                self.is_connected = True
                logger.info("Connected to Qdrant Vector Database at %s:%d", settings.QDRANT_HOST, settings.QDRANT_PORT)
            except Exception as e:
                logger.warning("Qdrant connection unavailable (%s) — using memory vector store fallback", e)
                self.client = None
                self.is_connected = False
        else:
            logger.info("qdrant-client package not installed — using memory vector store fallback")

    @classmethod
    def get_instance(cls) -> QdrantVectorClient:
        if cls._instance is None:
            cls._instance = QdrantVectorClient()
        return cls._instance


def get_qdrant_client() -> QdrantVectorClient:
    return QdrantVectorClient.get_instance()
