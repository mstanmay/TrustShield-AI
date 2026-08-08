"""
MLflow Schemas — Pydantic models for tracking metrics, model versions, and MLOps dashboard data.
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class ModelMetrics(BaseModel):
    """Core classification & operational metrics for ML models."""
    precision: float = Field(..., ge=0.0, le=1.0)
    recall: float = Field(..., ge=0.0, le=1.0)
    f1_score: float = Field(..., ge=0.0, le=1.0)
    roc_auc: float = Field(..., ge=0.0, le=1.0)
    latency_ms: float = Field(..., ge=0.0)
    inference_time_ms: float = Field(..., ge=0.0)
    confidence: float = Field(..., ge=0.0, le=1.0)


class RunInfo(BaseModel):
    """Information on an individual MLflow experiment run."""
    run_id: str
    experiment_id: str
    model_name: str
    status: str = "FINISHED"
    metrics: ModelMetrics
    parameters: dict[str, Any] = Field(default_factory=dict)
    tags: dict[str, Any] = Field(default_factory=dict)
    start_time: str
    end_time: str | None = None


class ModelVersionInfo(BaseModel):
    """Registered production model version."""
    model_name: str
    version: str
    stage: str = "Production"  # "Staging" | "Production" | "Archived"
    run_id: str
    source: str
    creation_timestamp: str
    description: str | None = None


class MLOpsDashboardData(BaseModel):
    """Aggregated MLOps dashboard statistics."""
    total_experiments: int
    active_runs_count: int
    registered_models_count: int
    production_models: list[ModelVersionInfo]
    recent_runs: list[RunInfo]
    aggregated_metrics: dict[str, ModelMetrics]
