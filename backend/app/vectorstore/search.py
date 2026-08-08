"""
Qdrant Vector Search Engine — similarity search, metadata filtering, case similarity, fraud pattern search.
"""

from __future__ import annotations

import logging
from typing import Any

from app.rag.embeddings.generator import EmbeddingGenerator
from app.vectorstore.client import get_qdrant_client
from app.vectorstore.collections import (
    COLLECTION_CASE_EMBEDDINGS,
    COLLECTION_FRAUD_PATTERNS,
    COLLECTION_SEBI_KNOWLEDGE,
)

logger = logging.getLogger(__name__)


class QdrantVectorSearch:
    """High-level Vector Search engine for nearest neighbors, case similarity, and fraud pattern detection."""

    def __init__(self):
        self.qclient = get_qdrant_client()
        self.generator = EmbeddingGenerator()

    def search_similar_documents(
        self,
        query: str,
        top_k: int = 5,
        authority: str | None = None,
        category: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search regulatory knowledge collection for document similarity."""
        query_vector = self.generator.generate_embedding(query)
        return self._search_collection(
            collection_name=COLLECTION_SEBI_KNOWLEDGE,
            query_vector=query_vector,
            top_k=top_k,
            filter_authority=authority,
            filter_category=category,
        )

    def search_similar_cases(
        self,
        case_summary_text: str,
        top_k: int = 5,
        min_score: float = 0.3,
    ) -> list[dict[str, Any]]:
        """Search past cases to find historically similar fraud cases."""
        query_vector = self.generator.generate_embedding(case_summary_text)
        results = self._search_collection(
            collection_name=COLLECTION_CASE_EMBEDDINGS,
            query_vector=query_vector,
            top_k=top_k,
        )
        return [r for r in results if r.get("similarity_score", 0) >= min_score]

    def search_similar_fraud_patterns(
        self,
        input_text_or_url: str,
        top_k: int = 5,
        pattern_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """Search known fraud patterns collection for matching scam signatures."""
        query_vector = self.generator.generate_embedding(input_text_or_url)
        return self._search_collection(
            collection_name=COLLECTION_FRAUD_PATTERNS,
            query_vector=query_vector,
            top_k=top_k,
            filter_pattern_type=pattern_type,
        )

    def nearest_neighbors(
        self,
        collection_name: str,
        vector: list[float],
        top_k: int = 5,
    ) -> list[dict[str, Any]]:
        """Perform raw nearest neighbor search on a given vector."""
        return self._search_collection(
            collection_name=collection_name,
            query_vector=vector,
            top_k=top_k,
        )

    def _search_collection(
        self,
        collection_name: str,
        query_vector: list[float],
        top_k: int = 5,
        filter_authority: str | None = None,
        filter_category: str | None = None,
        filter_pattern_type: str | None = None,
    ) -> list[dict[str, Any]]:
        """Internal search router (Qdrant server or fallback memory store)."""
        if self.qclient.is_connected and self.qclient.client:
            from qdrant_client.http import models
            try:
                must_filters = []
                if filter_authority:
                    must_filters.append(
                        models.FieldCondition(
                            key="authority",
                            match=models.MatchValue(value=filter_authority),
                        )
                    )
                if filter_pattern_type:
                    must_filters.append(
                        models.FieldCondition(
                            key="pattern_type",
                            match=models.MatchValue(value=filter_pattern_type),
                        )
                    )

                query_filter = models.Filter(must=must_filters) if must_filters else None

                hits = self.qclient.client.search(
                    collection_name=collection_name,
                    query_vector=query_vector,
                    query_filter=query_filter,
                    limit=top_k,
                )

                return [
                    {
                        "point_id": str(hit.id),
                        "similarity_score": round(float(hit.score), 4),
                        "payload": hit.payload or {},
                        "metadata": hit.payload or {},
                    }
                    for hit in hits
                ]
            except Exception as e:
                logger.warning("Qdrant search failed: %s — falling back to memory store", e)

        # Fallback memory search
        fallback_store = self.qclient._local_fallback_store.get(collection_name, [])
        results = []
        for p in fallback_store:
            payload = p.get("payload", {})
            if filter_authority and payload.get("authority") != filter_authority:
                continue
            if filter_pattern_type and payload.get("pattern_type") != filter_pattern_type:
                continue

            sim = self.generator.cosine_similarity(query_vector, p.get("vector", []))
            results.append({
                "point_id": p.get("point_id"),
                "similarity_score": round(sim, 4),
                "payload": payload,
                "metadata": payload,
                "content": payload.get("content", ""),
            })

        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        return results[:top_k]
