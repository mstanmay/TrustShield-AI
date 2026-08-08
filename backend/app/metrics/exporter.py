"""
Prometheus Exporter — exposes GET /metrics in standard Prometheus text format.
"""

from __future__ import annotations

from fastapi import APIRouter, Response

try:
    from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
    HAS_PROMETHEUS = True
except ImportError:
    generate_latest = None
    CONTENT_TYPE_LATEST = "text/plain"
    HAS_PROMETHEUS = False

router = APIRouter(tags=["metrics"])


@router.get("/metrics")
async def metrics_endpoint():
    """Prometheus Scrape Endpoint — exports system, MLOps, vector DB, and scam metrics."""
    if HAS_PROMETHEUS and generate_latest:
        data = generate_latest()
        return Response(content=data, media_type=CONTENT_TYPE_LATEST)
    
    return Response(
        content="# Prometheus metrics exposition format\n# prometheus_client not installed\n",
        media_type="text/plain",
    )
