"""
Document Chunker — splits documents into overlapping semantic chunks for vector indexing.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class DocumentChunk:
    """Represents a chunk of a document with position and metadata."""
    chunk_id: str
    doc_id: str
    content: str
    chunk_index: int
    total_chunks: int
    metadata: dict[str, Any] = field(default_factory=dict)


class DocumentChunker:
    """Splits raw text documents into overlapping chunks."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(
        self,
        doc_id: str,
        text: str,
        base_metadata: dict[str, Any] | None = None,
    ) -> list[DocumentChunk]:
        """Split text into DocumentChunks with overlap and metadata."""
        base_metadata = base_metadata or {}
        if not text.strip():
            return []

        # Split into paragraphs first
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
        chunks_text: list[str] = []

        current_chunk = ""
        for p in paragraphs:
            if len(current_chunk) + len(p) + 2 <= self.chunk_size:
                current_chunk = f"{current_chunk}\n\n{p}".strip()
            else:
                if current_chunk:
                    chunks_text.append(current_chunk)
                # Handle paragraph larger than chunk_size
                if len(p) > self.chunk_size:
                    sub_parts = self._split_by_words(p)
                    chunks_text.extend(sub_parts[:-1])
                    current_chunk = sub_parts[-1] if sub_parts else ""
                else:
                    current_chunk = p

        if current_chunk:
            chunks_text.append(current_chunk)

        # Apply overlap across boundaries
        overlapped_chunks = self._add_overlap(chunks_text)

        total = len(overlapped_chunks)
        result: list[DocumentChunk] = []

        for idx, chunk_str in enumerate(overlapped_chunks):
            cid = f"{doc_id}_chunk_{idx+1}"
            meta = {
                **base_metadata,
                "doc_id": doc_id,
                "chunk_index": idx,
                "total_chunks": total,
                "char_length": len(chunk_str),
            }
            result.append(DocumentChunk(
                chunk_id=cid,
                doc_id=doc_id,
                content=chunk_str,
                chunk_index=idx,
                total_chunks=total,
                metadata=meta,
            ))

        return result

    def _split_by_words(self, text: str) -> list[str]:
        words = text.split()
        chunks = []
        current = []
        curr_len = 0

        for w in words:
            if curr_len + len(w) + 1 > self.chunk_size:
                chunks.append(" ".join(current))
                current = [w]
                curr_len = len(w)
            else:
                current.append(w)
                curr_len += len(w) + 1

        if current:
            chunks.append(" ".join(current))
        return chunks

    def _add_overlap(self, chunks: list[str]) -> list[str]:
        if len(chunks) <= 1 or self.chunk_overlap <= 0:
            return chunks

        overlapped = [chunks[0]]
        for i in range(1, len(chunks)):
            prev_tail = chunks[i-1][-self.chunk_overlap:]
            overlapped.append(f"... {prev_tail}\n{chunks[i]}")
        return overlapped
