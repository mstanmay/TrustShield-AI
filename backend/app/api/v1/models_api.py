"""
MLflow Model Dashboard API Router — MLOps tracking and model registry endpoints:
- GET /api/v1/models/dashboard
- GET /api/v1/models/experiments
- GET /api/v1/models/registry
- POST /api/v1/models/track
"""

from __future__ import annotations

from typing import Any
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from mlflow.experiments.manager import ExperimentManager
from mlflow.models.schemas import MLOpsDashboardData, ModelMetrics, ModelVersionInfo, RunInfo
from mlflow.registry.registry import ModelRegistry
from mlflow.tracking.tracker import get_model_tracker

router = APIRouter(prefix="/api/v1/models", tags=["mlops-models"])


class TrackInferenceRequest(BaseModel):
    """Payload for logging model inference performance."""
    model_name: str = Field(..., min_length=2)
    execution_time_ms: float = Field(..., ge=0.0)
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    extra_params: dict[str, Any] = Field(default_factory=dict)


class RegisterModelVersionRequest(BaseModel):
    """Payload for registering a new model version."""
    model_name: str
    version: str
    run_id: str
    stage: str = "Production"
    description: str | None = None


@router.get("/dashboard", response_model=MLOpsDashboardData)
async def get_model_dashboard():
    """Retrieve full MLOps model dashboard with Precision, Recall, F1, ROC, Latency, and Model Registry status."""
    tracker = get_model_tracker()
    return tracker.get_dashboard_data()


@router.get("/experiments", response_model=list[RunInfo])
async def list_experiments(limit: int = Query(20, ge=1, le=100)):
    """List recent MLflow experiment evaluation runs."""
    exp_mgr = ExperimentManager.get_instance()
    return exp_mgr.get_recent_runs(limit=limit)


@router.get("/registry", response_model=list[ModelVersionInfo])
async def list_model_registry():
    """List registered production models in the MLOps registry."""
    registry = ModelRegistry.get_instance()
    return registry.get_registered_models()


@router.post("/track", status_code=status.HTTP_201_CREATED)
async def track_model_inference(payload: TrackInferenceRequest):
    """Log a model inference metric run into MLflow tracking."""
    tracker = get_model_tracker()
    tracker.track_inference(
        model_name=payload.model_name,
        execution_time_ms=payload.execution_time_ms,
        confidence_score=payload.confidence_score,
        extra_params=payload.extra_params,
    )
    return {
        "status": "tracked",
        "model_name": payload.model_name,
        "execution_time_ms": payload.execution_time_ms,
        "confidence_score": payload.confidence_score,
    }


@router.post("/registry", response_model=ModelVersionInfo, status_code=status.HTTP_201_CREATED)
async def register_model_version(payload: RegisterModelVersionRequest):
    """Register a new production model version in the MLOps registry."""
    registry = ModelRegistry.get_instance()
    return registry.register_model_version(
        model_name=payload.model_name,
        version=payload.version,
        run_id=payload.run_id,
        stage=payload.stage,
        description=payload.description,
    )
