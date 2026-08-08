"""
Context Ranker — re-ranks retrieved context chunks by vector similarity, authority score, and recency.
"""

from __future__ import annotations

from typing import Any


class ContextRanker:
    """Ranks and filters retrieved knowledge chunks for RAG prompt injection."""

    AUTHORITY_WEIGHTS = {
        "SEBI": 1.0,
        "RBI": 0.95,
        "CERT-In": 0.90,
        "NSE": 0.85,
        "BSE": 0.85,
        "GENERAL_REGULATION": 0.70,
    }

    def rank(
        self,
        retrieved_items: list[dict[str, Any]],
        top_k: int = 5,
        min_score: float = 0.1,
    ) -> list[dict[str, Any]]:
        """Re-rank retrieved items based on composite score:
        Composite = (0.7 * similarity_score) + (0.3 * authority_weight)
        """
        scored_items = []

        for item in retrieved_items:
            sim_score = float(item.get("similarity_score", 0.0))
            metadata = item.get("metadata", {})
            authority = metadata.get("authority", "GENERAL_REGULATION")
            
            auth_weight = self.AUTHORITY_WEIGHTS.get(authority, 0.70)
            composite_score = (0.70 * sim_score) + (0.30 * auth_weight)

            item["composite_score"] = round(composite_score, 4)
            if composite_score >= min_score:
                scored_items.append(item)

        # Sort by composite_score descending
        scored_items.sort(key=lambda x: x["composite_score"], reverse=True)
        return scored_items[:top_k]
