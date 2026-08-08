"""
Knowledge Service — singleton service managing knowledge indexing, search, and RAG operations.
"""

from __future__ import annotations

import logging
from typing import Any

from app.rag.pipeline.rag_pipeline import RAGPipeline

logger = logging.getLogger(__name__)


class KnowledgeService:
    """Singleton service for RAG Knowledge Operations."""

    _instance: KnowledgeService | None = None

    def __init__(self):
        self.pipeline = RAGPipeline()
        self.pipeline.initialize_corpus()

    @classmethod
    def get_instance(cls) -> KnowledgeService:
        if cls._instance is None:
            cls._instance = KnowledgeService()
        return cls._instance

    def search(
        self,
        query: str,
        top_k: int = 5,
        authority: str | None = None,
        category: str | None = None,
    ) -> list[dict[str, Any]]:
        """Perform hybrid search over regulatory knowledge."""
        return self.pipeline.retrieve_context(
            query=query,
            top_k=top_k,
            authority_filter=authority,
            category_filter=category,
        )

    def index_document(
        self,
        title: str,
        content: str,
        doc_type: str = "circular",
        authority: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Index a new document and return summary."""
        chunks_count = self.pipeline.add_document(
            title=title,
            content=content,
            doc_type=doc_type,
            authority=authority,
            extra_meta=metadata,
        )
        return {
            "title": title,
            "doc_type": doc_type,
            "authority": authority or "GENERAL",
            "chunks_indexed": chunks_count,
            "status": "indexed",
        }

    def query_rag(
        self,
        query: str,
        top_k: int = 4,
        authority: str | None = None,
    ) -> dict[str, Any]:
        """Execute a RAG query and return structured context and answer prompt."""
        retrieved = self.search(query=query, top_k=top_k, authority=authority)
        formatted_context = self.pipeline._format_context(retrieved)

        return {
            "query": query,
            "retrieved_count": len(retrieved),
            "sources": [
                {
                    "title": r.get("metadata", {}).get("title"),
                    "authority": r.get("metadata", {}).get("authority"),
                    "ref_number": r.get("metadata", {}).get("ref_number"),
                    "relevance_score": r.get("similarity_score"),
                }
                for r in retrieved
            ],
            "context": formatted_context,
            "retrieved_chunks": retrieved,
        }


# Global singleton instance function
def get_knowledge_service() -> KnowledgeService:
    return KnowledgeService.get_instance()
