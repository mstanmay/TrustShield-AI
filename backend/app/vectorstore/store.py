"""
Qdrant Vector Store Adapter — point upserting, batch indexing, and payload management.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from app.rag.embeddings.generator import EmbeddingGenerator
from app.vectorstore.client import get_qdrant_client
from app.vectorstore.collections import (
    COLLECTION_CASE_EMBEDDINGS,
    COLLECTION_FRAUD_PATTERNS,
    COLLECTION_SEBI_KNOWLEDGE,
    QdrantCollectionManager,
)

logger = logging.getLogger(__name__)


class QdrantVectorStore:
    """Unified Vector Store supporting Qdrant server and fallback in-memory store."""

    def __init__(self):
        self.qclient = get_qdrant_client()
        self.collection_mgr = QdrantCollectionManager()
        self.collection_mgr.ensure_collections()

    def upsert_point(
        self,
        collection_name: str,
        point_id: str,
        vector: list[float],
        payload: dict[str, Any],
    ) -> bool:
        """Upsert a single vector point into a collection."""
        if self.qclient.is_connected and self.qclient.client:
            from qdrant_client.http import models
            try:
                # Convert UUID string or generate numeric ID
                pid = str(uuid.uuid5(uuid.NAMESPACE_DNS, point_id))
                self.qclient.client.upsert(
                    collection_name=collection_name,
                    points=[
                        models.PointStruct(
                            id=pid,
                            vector=vector,
                            payload=payload,
                        )
                    ],
                )
                return True
            except Exception as e:
                logger.warning("Qdrant upsert failed: %s — using local memory store", e)

        # Fallback memory store
        store = self.qclient._local_fallback_store.setdefault(collection_name, [])
        # Remove existing if point_id matches
        store[:] = [p for p in store if p.get("point_id") != point_id]
        store.append({
            "point_id": point_id,
            "vector": vector,
            "payload": payload,
        })
        return True

    def upsert_batch(
        self,
        collection_name: str,
        records: list[dict[str, Any]],
    ) -> int:
        """Batch upsert multiple records into a collection."""
        count = 0
        for rec in records:
            pid = rec.get("chunk_id") or rec.get("id") or str(uuid.uuid4())
            vec = rec.get("vector") or rec.get("embedding") or []
            payload = rec.get("metadata") or rec.get("payload") or rec
            if vec and self.upsert_point(collection_name, pid, vec, payload):
                count += 1
        return count
