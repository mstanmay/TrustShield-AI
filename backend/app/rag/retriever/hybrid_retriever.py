"""
Hybrid Retriever — combines dense vector search and sparse keyword BM25 retrieval.
"""

from __future__ import annotations

import re
from typing import Any

from app.rag.embeddings.generator import EmbeddingGenerator
from app.rag.retriever.ranker import ContextRanker


class HybridRetriever:
    """Performs hybrid vector + keyword retrieval over stored document chunks."""

    def __init__(
        self,
        embedding_generator: EmbeddingGenerator | None = None,
        ranker: ContextRanker | None = None,
    ):
        self.generator = embedding_generator or EmbeddingGenerator()
        self.ranker = ranker or ContextRanker()

    def search(
        self,
        query: str,
        index_records: list[dict[str, Any]],
        top_k: int = 5,
        authority_filter: str | None = None,
        category_filter: str | None = None,
    ) -> list[dict[str, Any]]:
        """Perform hybrid search over indexed document chunk records."""
        if not index_records or not query.strip():
            return []

        # 1. Dense vector search
        query_vector = self.generator.generate_embedding(query)
        query_tokens = set(re.findall(r"\w+", query.lower()))

        results = []
        for record in index_records:
            metadata = record.get("metadata", {})

            # Optional metadata filtering
            if authority_filter and metadata.get("authority") != authority_filter:
                continue
            if category_filter and category_filter not in metadata.get("categories", []):
                continue

            # Dense similarity
            doc_vector = record.get("vector", [])
            dense_sim = self.generator.cosine_similarity(query_vector, doc_vector)

            # Sparse keyword overlap score
            content = record.get("content", "").lower()
            content_tokens = set(re.findall(r"\w+", content))
            overlap_count = len(query_tokens.intersection(content_tokens))
            sparse_score = overlap_count / (len(query_tokens) + 1e-5)

            # Hybrid score (60% dense + 40% sparse)
            hybrid_score = (0.60 * dense_sim) + (0.40 * min(sparse_score, 1.0))

            results.append({
                "chunk_id": record.get("chunk_id"),
                "doc_id": record.get("doc_id"),
                "content": record.get("content"),
                "similarity_score": round(hybrid_score, 4),
                "metadata": metadata,
            })

        # 2. Context ranking
        return self.ranker.rank(results, top_k=top_k)
