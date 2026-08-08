"""
Document Indexer — coordinates chunking, metadata extraction, embedding generation, and indexing.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from app.rag.embeddings.generator import EmbeddingGenerator
from app.rag.indexer.chunker import DocumentChunk, DocumentChunker
from app.rag.indexer.metadata_extractor import MetadataExtractor

logger = logging.getLogger(__name__)


class DocumentIndexer:
    """Indexes regulatory documents, advisories, and circulars into vector & metadata storage."""

    def __init__(
        self,
        embedding_generator: EmbeddingGenerator | None = None,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
    ):
        self.generator = embedding_generator or EmbeddingGenerator()
        self.chunker = DocumentChunker(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        self.extractor = MetadataExtractor()

    def process_document(
        self,
        title: str,
        content: str,
        doc_type: str = "circular",
        authority: str | None = None,
        extra_meta: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Process a raw document into indexable record objects with embeddings.

        Returns:
            List of indexed chunk records ready for vector storage.
        """
        doc_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{doc_type}:{title}"))
        
        # 1. Extract metadata
        base_meta = self.extractor.extract(content, extra_meta)
        base_meta.update({
            "title": title,
            "doc_type": doc_type,
        })
        if authority:
            base_meta["authority"] = authority

        # 2. Chunk document
        chunks: list[DocumentChunk] = self.chunker.chunk_document(doc_id, content, base_meta)

        # 3. Generate embeddings
        indexed_records: list[dict[str, Any]] = []
        for chunk in chunks:
            vector = self.generator.generate_embedding(chunk.content)
            record = {
                "chunk_id": chunk.chunk_id,
                "doc_id": chunk.doc_id,
                "content": chunk.content,
                "vector": vector,
                "metadata": chunk.metadata,
            }
            indexed_records.append(record)

        logger.info(
            "Processed document '%s' (%s) into %d vector chunks",
            title,
            doc_id,
            len(indexed_records),
        )
        return indexed_records
