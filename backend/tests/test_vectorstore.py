"""
Unit tests for Phase 3 Qdrant Vector Database — client, collections, store, search, and RAG integration.
"""

from __future__ import annotations

import pytest

from app.rag.pipeline.rag_pipeline import RAGPipeline
from app.vectorstore.client import QdrantVectorClient, get_qdrant_client
from app.vectorstore.collections import (
    COLLECTION_CASE_EMBEDDINGS,
    COLLECTION_FRAUD_PATTERNS,
    COLLECTION_SEBI_KNOWLEDGE,
    QdrantCollectionManager,
)
from app.vectorstore.search import QdrantVectorSearch
from app.vectorstore.store import QdrantVectorStore


class TestQdrantVectorStore:
    """Unit test suite for Qdrant vector database integration."""

    def test_client_singleton(self):
        client1 = get_qdrant_client()
        client2 = get_qdrant_client()
        assert client1 is client2

    def test_collection_manager_status(self):
        mgr = QdrantCollectionManager()
        status = mgr.ensure_collections()
        assert status[COLLECTION_SEBI_KNOWLEDGE] is True
        assert status[COLLECTION_CASE_EMBEDDINGS] is True
        assert status[COLLECTION_FRAUD_PATTERNS] is True

    def test_vector_store_point_upsert_and_search(self):
        store = QdrantVectorStore()
        search = QdrantVectorSearch()

        # Vector of size 384
        dummy_vector = [0.1] * 384
        payload = {
            "title": "SEBI Deepfake Advisory 2024",
            "authority": "SEBI",
            "category": "deepfake",
        }

        # Upsert point
        success = store.upsert_point(
            collection_name=COLLECTION_SEBI_KNOWLEDGE,
            point_id="point-101",
            vector=dummy_vector,
            payload=payload,
        )
        assert success is True

        # Perform nearest neighbor search
        results = search.nearest_neighbors(
            collection_name=COLLECTION_SEBI_KNOWLEDGE,
            vector=dummy_vector,
            top_k=3,
        )
        assert len(results) >= 1
        assert results[0]["similarity_score"] > 0

    def test_case_similarity_search(self):
        store = QdrantVectorStore()
        search = QdrantVectorSearch()

        vector = search.generator.generate_embedding("WhatsApp guaranteed stock returns scam")
        store.upsert_point(
            collection_name=COLLECTION_CASE_EMBEDDINGS,
            point_id="case-999",
            vector=vector,
            payload={"case_id": "case-999", "summary": "WhatsApp scam"},
        )

        cases = search.search_similar_cases("WhatsApp guaranteed stock tips scam", top_k=2)
        assert len(cases) >= 1
        assert cases[0]["metadata"]["case_id"] == "case-999"

    def test_fraud_pattern_search(self):
        store = QdrantVectorStore()
        search = QdrantVectorSearch()

        vector = search.generator.generate_embedding("https://sebl.gov.in/login")
        store.upsert_point(
            collection_name=COLLECTION_FRAUD_PATTERNS,
            point_id="scam-domain-1",
            vector=vector,
            payload={"pattern_type": "domain", "domain": "sebl.gov.in"},
        )

        patterns = search.search_similar_fraud_patterns("https://sebl.gov.in/login", top_k=2)
        assert len(patterns) >= 1

    def test_rag_pipeline_uses_qdrant_vector_store(self):
        pipeline = RAGPipeline()
        count = pipeline.initialize_corpus()
        assert count > 0

        # Verify Qdrant search responds with seeded RAG context
        retrieved = pipeline.retrieve_context("Telegram unregistered stock recommendations", top_k=3)
        assert len(retrieved) > 0
        assert "SEBI" in str(retrieved) or "Advisory" in str(retrieved)
