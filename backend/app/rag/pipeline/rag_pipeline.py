"""
RAG Pipeline — main orchestrator for indexing, retrieval, and prompt enrichment.
"""

from __future__ import annotations

import logging
from typing import Any

from app.rag.embeddings.generator import EmbeddingGenerator
from app.rag.indexer.document_indexer import DocumentIndexer
from app.rag.knowledge.regulatory_corpus import SEED_REGULATORY_DOCUMENTS
from app.rag.prompts.templates import (
    RAG_COMPLAINT_GENERATION_PROMPT,
    RAG_DOCUMENT_VERIFICATION_PROMPT,
    RAG_RISK_ASSESSMENT_PROMPT,
)
from app.rag.retriever.hybrid_retriever import HybridRetriever

from app.vectorstore.collections import COLLECTION_SEBI_KNOWLEDGE
from app.vectorstore.search import QdrantVectorSearch
from app.vectorstore.store import QdrantVectorStore

logger = logging.getLogger(__name__)


class RAGPipeline:
    """Complete RAG pipeline managing regulatory corpus index, retrieval, and context injection using Qdrant."""

    def __init__(self):
        self.generator = EmbeddingGenerator()
        self.indexer = DocumentIndexer(embedding_generator=self.generator)
        self.retriever = HybridRetriever(embedding_generator=self.generator)
        self.qstore = QdrantVectorStore()
        self.qsearch = QdrantVectorSearch()
        self._index: list[dict[str, Any]] = []

    def initialize_corpus(self) -> int:
        """Load and index default regulatory corpus into memory & Qdrant vector store."""
        logger.info("Initializing RAG pipeline regulatory corpus into Qdrant...")
        self._index.clear()

        for doc in SEED_REGULATORY_DOCUMENTS:
            records = self.indexer.process_document(
                title=doc["title"],
                content=doc["content"],
                doc_type=doc["doc_type"],
                authority=doc["authority"],
            )
            self._index.extend(records)
            self.qstore.upsert_batch(COLLECTION_SEBI_KNOWLEDGE, records)

        logger.info("Indexed %d knowledge chunks into Qdrant RAG corpus", len(self._index))
        return len(self._index)

    def add_document(
        self,
        title: str,
        content: str,
        doc_type: str = "circular",
        authority: str | None = None,
        extra_meta: dict[str, Any] | None = None,
    ) -> int:
        """Add and index a new document into RAG knowledge base & Qdrant.
        Automatically updates embeddings.
        """
        records = self.indexer.process_document(
            title=title,
            content=content,
            doc_type=doc_type,
            authority=authority,
            extra_meta=extra_meta,
        )
        self._index.extend(records)
        self.qstore.upsert_batch(COLLECTION_SEBI_KNOWLEDGE, records)
        logger.info("Added document '%s' (%d chunks) to Qdrant vector index", title, len(records))
        return len(records)

    def retrieve_context(
        self,
        query: str,
        top_k: int = 4,
        authority_filter: str | None = None,
        category_filter: str | None = None,
    ) -> list[dict[str, Any]]:
        """Retrieve relevant context chunks for a query."""
        if not self._index:
            self.initialize_corpus()

        return self.retriever.search(
            query=query,
            index_records=self._index,
            top_k=top_k,
            authority_filter=authority_filter,
            category_filter=category_filter,
        )

    def build_risk_assessment_prompt(self, query: str, case_evidence_str: str) -> tuple[str, list[dict[str, Any]]]:
        """Build a RAG-augmented prompt for risk assessment."""
        results = self.retrieve_context(query, top_k=3)
        context_str = self._format_context(results)

        prompt = RAG_RISK_ASSESSMENT_PROMPT.format(
            rag_context=context_str if context_str else "No direct regulatory matches found.",
            case_evidence=case_evidence_str,
        )
        return prompt, results

    def build_document_verification_prompt(self, document_text: str) -> tuple[str, list[dict[str, Any]]]:
        """Build a RAG-augmented prompt for document verification."""
        results = self.retrieve_context(document_text[:1000], top_k=3, authority_filter="SEBI")
        context_str = self._format_context(results)

        prompt = RAG_DOCUMENT_VERIFICATION_PROMPT.format(
            rag_context=context_str if context_str else "No official SEBI circular matches found.",
            document_text=document_text[:3000],
        )
        return prompt, results

    def build_complaint_prompt(self, case_summary_str: str) -> tuple[str, list[dict[str, Any]]]:
        """Build a RAG-augmented prompt for complaint generation."""
        results = self.retrieve_context(case_summary_str[:1000], top_k=3)
        context_str = self._format_context(results)

        prompt = RAG_COMPLAINT_GENERATION_PROMPT.format(
            rag_context=context_str if context_str else "Standard SEBI PFUTP Regulations apply.",
            case_summary=case_summary_str,
        )
        return prompt, results

    def get_indexed_records() -> list[dict[str, Any]]:
        """Return raw indexed records (for inspection / export)."""
        return self._index

    @staticmethod
    def _format_context(retrieved_items: list[dict[str, Any]]) -> str:
        formatted = []
        for i, item in enumerate(retrieved_items, 1):
            meta = item.get("metadata", {})
            auth = meta.get("authority", "REGULATORY")
            ref = meta.get("ref_number", "")
            title = meta.get("title", "")
            score = item.get("similarity_score", 0.0)

            header = f"[{i}] Authority: {auth} | Ref: {ref} | Title: {title} (Relevance: {score:.2f})"
            content = item.get("content", "").strip()
            formatted.append(f"{header}\n{content}")

        return "\n\n".join(formatted)
