"""
FastAPI application entry point — SEBI Fraud/Scam Detection Backend.

Registers all routers, middleware, and lifecycle handlers.
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.middleware import RequestIDMiddleware
from app.api.v1 import (
    alerts,
    auth,
    cases,
    complaints,
    dashboard,
    extension_api,
    graph_api,
    ingest,
    knowledge,
    models_api,
    threat_intel_api,
)
from app.config import settings
from app.core.database import close_db, init_db
from app.core.observability import setup_logging, setup_otel
from app.core.redis_client import close_redis, init_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    # Startup
    setup_logging()
    setup_otel()

    await init_db()
    await init_redis()

    # Initialize object storage bucket
    try:
        from app.core.storage import object_storage
        object_storage.ensure_bucket()
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("Could not initialize S3 bucket: %s", e)

    yield

    # Shutdown
    await close_db()
    await close_redis()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Multi-modal fraud and scam detection platform for protecting investors "
        "from SEBI-related scams. Supports video, image, audio, PDF, URL, email, "
        "QR code, WhatsApp, and Telegram input analysis."
    ),
    lifespan=lifespan,
)

# ── Middleware ────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.metrics.exporter import router as metrics_router
from app.metrics.middleware import PrometheusMetricsMiddleware
from app.security.headers import SecurityHeadersMiddleware
from app.security.rate_limiter import RateLimiterMiddleware

# ...

app.add_middleware(RequestIDMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimiterMiddleware)
app.add_middleware(PrometheusMetricsMiddleware)

# ── Routers ──────────────────────────────────────────────────────────────────

app.include_router(metrics_router)
app.include_router(auth.router)
app.include_router(ingest.router)
app.include_router(cases.router)
app.include_router(dashboard.router)
app.include_router(alerts.router)
app.include_router(complaints.router)
app.include_router(knowledge.router)
app.include_router(models_api.router)
app.include_router(graph_api.router)
app.include_router(extension_api.router)
app.include_router(threat_intel_api.router)

# Additional dashboard complaint draft endpoint (alias)
@app.post("/api/v1/dashboard/complaints/draft", tags=["complaints"])
async def dashboard_complaint_draft(case_id: str):
    """Alias: Complaint Generation Assistant entry point from dashboard."""
    from fastapi import Depends
    from app.core.database import get_db_session
    from app.api.v1.complaints import generate_complaint
    # This is an alias — the actual implementation is in complaints router
    # Direct users to POST /api/v1/complaints/{case_id}/generate
    return {"redirect": f"/api/v1/complaints/{case_id}/generate"}


# ── Health Check ─────────────────────────────────────────────────────────────

@app.get("/health", tags=["system"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/api/v1/info", tags=["system"])
async def root():
    """API info endpoint."""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


# ── Mount Frontend Static Assets (Single Localhost Server) ───────────────────

from pathlib import Path
from fastapi.staticfiles import StaticFiles

dist_dir = Path(__file__).resolve().parent.parent.parent / "dist"
if dist_dir.exists():
    app.mount("/", StaticFiles(directory=str(dist_dir), html=True), name="frontend")

