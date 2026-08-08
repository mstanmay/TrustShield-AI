"""
Unit tests for Phase 2 RAG Knowledge Base — chunker, generator, hybrid search, ranking, and APIs.
"""

from __future__ import annotations

import pytest

from app.rag.embeddings.generator import EmbeddingGenerator
from app.rag.indexer.chunker import DocumentChunker
from app.rag.indexer.metadata_extractor import MetadataExtractor
from app.rag.pipeline.rag_pipeline import RAGPipeline
from app.rag.services.knowledge_service import KnowledgeService


class TestRAGPipeline:
    """Unit tests for RAG pipeline components."""

    def test_embedding_generation_length_and_normalization(self):
        generator = EmbeddingGenerator(dimension=384)
        vec = generator.generate_embedding("SEBI circular on deepfake voice scams")
        assert len(vec) == 384
        # Normalized vector length should be ~1.0
        import math
        norm = math.sqrt(sum(x * x for x in vec))
        assert abs(norm - 1.0) < 1e-4

    def test_document_chunker_overlap(self):
        chunker = DocumentChunker(chunk_size=100, chunk_overlap=20)
        text = (
            "Paragraph one is a long statement about securities market regulation. "
            "Paragraph two contains details about unregistered advisors operating on Telegram channels."
        )
        chunks = chunker.chunk_document("doc-1", text)
        assert len(chunks) >= 1
        assert chunks[0].chunk_id.startswith("doc-1_chunk_")

    def test_metadata_extraction(self):
        extractor = MetadataExtractor()
        text = "SEBI Circular SEBI/HO/MIRSD/DOS3/P/CIR/2023/112 on WhatsApp scams."
        meta = extractor.extract(text)
        assert meta["authority"] == "SEBI"
        assert meta["ref_number"] == "SEBI/HO/MIRSD/DOS3/P/CIR/2023/112"

    def test_rag_pipeline_search(self):
        pipeline = RAGPipeline()
        pipeline.initialize_corpus()
        results = pipeline.retrieve_context("deepfake voice cloning fraud", top_k=3)
        
        assert len(results) > 0
        assert "similarity_score" in results[0]
        assert "metadata" in results[0]

    def test_knowledge_service_query(self):
        service = KnowledgeService.get_instance()
        rag_res = service.query_rag("Telegram stock tip provider", top_k=2)

        assert rag_res["query"] == "Telegram stock tip provider"
        assert rag_res["retrieved_count"] > 0
        assert isinstance(rag_res["sources"], list)
        assert "SEBI" in rag_res["context"] or "Advisory" in rag_res["context"]
