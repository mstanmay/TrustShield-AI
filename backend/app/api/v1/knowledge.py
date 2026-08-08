"""
Knowledge API Router — RAG knowledge base endpoints:
- POST /api/v1/knowledge/index
- GET /api/v1/knowledge/search
- POST /api/v1/knowledge/query
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.rag.services.get_service import get_knowledge_service_dependency

router = APIRouter(prefix="/api/v1/knowledge", tags=["knowledge-rag"])


class IndexDocumentRequest(BaseModel):
    """Payload for indexing a new regulatory document."""
    title: str = Field(..., min_length=3, max_length=500)
    content: str = Field(..., min_length=10)
    doc_type: str = Field(default="circular", description="circular | advisory | regulation | awareness")
    authority: str | None = Field(default="SEBI", description="SEBI | NSE | BSE | RBI | CERT-In")
    metadata: dict[str, Any] = Field(default_factory=dict)


class IndexDocumentResponse(BaseModel):
    """Response after document indexing."""
    title: str
    doc_type: str
    authority: str
    chunks_indexed: int
    status: str = "indexed"


class RAGQueryRequest(BaseModel):
    """Payload for RAG query execution."""
    query: str = Field(..., min_length=3)
    top_k: int = Field(default=4, ge=1, le=20)
    authority: str | None = Field(default=None)


@router.post("/index", response_model=IndexDocumentResponse, status_code=status.HTTP_201_CREATED)
async def index_document(
    payload: IndexDocumentRequest,
):
    """Index a new regulatory circular, advisory, or regulation into the RAG knowledge base."""
    service = get_knowledge_service_dependency()
    result = service.index_document(
        title=payload.title,
        content=payload.content,
        doc_type=payload.doc_type,
        authority=payload.authority,
        metadata=payload.metadata,
    )
    return IndexDocumentResponse(**result)


@router.get("/search")
async def search_knowledge(
    q: str = Query(..., min_length=2, description="Search query string"),
    top_k: int = Query(5, ge=1, le=20),
    authority: str | None = Query(None, description="SEBI | NSE | BSE | RBI | CERT-In"),
    category: str | None = Query(None),
):
    """Semantic + keyword hybrid search over SEBI/NSE/BSE/RBI circulars & advisories."""
    service = get_knowledge_service_dependency()
    results = service.search(
        query=q,
        top_k=top_k,
        authority=authority,
        category=category,
    )
    return {
        "query": q,
        "results_count": len(results),
        "results": results,
    }


@router.post("/query")
async def query_rag(
    payload: RAGQueryRequest,
):
    """Execute a RAG query to retrieve relevant regulatory context for AI synthesis."""
    service = get_knowledge_service_dependency()
    response = service.query_rag(
        query=payload.query,
        top_k=payload.top_k,
        authority=payload.authority,
    )
    return response
