"""
Qdrant Collection Manager — creates and manages Qdrant vector collections:
- sebi_regulatory_knowledge
- case_embeddings
- fraud_patterns
"""

from __future__ import annotations

import logging
from typing import Any

from app.config import settings
from app.vectorstore.client import get_qdrant_client

logger = logging.getLogger(__name__)

COLLECTION_SEBI_KNOWLEDGE = "sebi_regulatory_knowledge"
COLLECTION_CASE_EMBEDDINGS = "case_embeddings"
COLLECTION_FRAUD_PATTERNS = "fraud_patterns"


class QdrantCollectionManager:
    """Manages Qdrant vector collection schemas and creation."""

    def __init__(self):
        self.qclient = get_qdrant_client()

    def ensure_collections(self) -> dict[str, bool]:
        """Ensure all required vector collections exist in Qdrant."""
        status = {
            COLLECTION_SEBI_KNOWLEDGE: False,
            COLLECTION_CASE_EMBEDDINGS: False,
            COLLECTION_FRAUD_PATTERNS: False,
        }

        if not self.qclient.is_connected or not self.qclient.client:
            logger.info("Qdrant not connected — fallback memory store active for collections")
            for c in status:
                self.qclient._local_fallback_store.setdefault(c, [])
                status[c] = True
            return status

        from qdrant_client.http import models

        collections_to_create = [
            (COLLECTION_SEBI_KNOWLEDGE, settings.QDRANT_VECTOR_SIZE),
            (COLLECTION_CASE_EMBEDDINGS, settings.QDRANT_VECTOR_SIZE),
            (COLLECTION_FRAUD_PATTERNS, settings.QDRANT_VECTOR_SIZE),
        ]

        try:
            existing = [c.name for c in self.qclient.client.get_collections().collections]
            for col_name, vec_size in collections_to_create:
                if col_name not in existing:
                    logger.info("Creating Qdrant collection '%s' (vector size: %d)", col_name, vec_size)
                    self.qclient.client.create_collection(
                        collection_name=col_name,
                        vectors_config=models.VectorParams(
                            size=vec_size,
                            distance=models.Distance.COSINE,
                        ),
                    )
                status[col_name] = True
        except Exception as e:
            logger.error("Failed to ensure Qdrant collections: %s", e)

        return status
