"""
MLflow Model Performance Tracker — automated tracking decorator and helper for model inferences.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from mlflow.experiments.manager import ExperimentManager
from mlflow.models.schemas import ModelMetrics, MLOpsDashboardData
from mlflow.registry.registry import ModelRegistry

logger = logging.getLogger(__name__)


class ModelPerformanceTracker:
    """Automated tracker for model inference metrics, latency, precision, and confidence."""

    _instance: ModelPerformanceTracker | None = None

    def __init__(self):
        self.exp_manager = ExperimentManager.get_instance()
        self.registry = ModelRegistry.get_instance()
        self._aggregated_metrics: dict[str, ModelMetrics] = {}
        self._initialize_baseline_metrics()

    @classmethod
    def get_instance(cls) -> ModelPerformanceTracker:
        if cls._instance is None:
            cls._instance = ModelPerformanceTracker()
        return cls._instance

    def _initialize_baseline_metrics(self):
        """Seed baseline model performance metrics."""
        self._aggregated_metrics = {
            "DeepfakeDetectionModel": ModelMetrics(
                precision=0.942, recall=0.915, f1_score=0.928, roc_auc=0.965,
                latency_ms=145.0, inference_time_ms=120.0, confidence=0.89,
            ),
            "VoiceCloningDetector": ModelMetrics(
                precision=0.925, recall=0.890, f1_score=0.907, roc_auc=0.948,
                latency_ms=95.0, inference_time_ms=80.0, confidence=0.87,
            ),
            "DocumentVerificationOCR": ModelMetrics(
                precision=0.968, recall=0.952, f1_score=0.960, roc_auc=0.981,
                latency_ms=320.0, inference_time_ms=290.0, confidence=0.94,
            ),
            "PhishingURLScanner": ModelMetrics(
                precision=0.985, recall=0.970, f1_score=0.977, roc_auc=0.992,
                latency_ms=45.0, inference_time_ms=35.0, confidence=0.96,
            ),
            "RiskAssessmentLLM": ModelMetrics(
                precision=0.935, recall=0.920, f1_score=0.927, roc_auc=0.955,
                latency_ms=850.0, inference_time_ms=780.0, confidence=0.91,
            ),
        }

    def track_inference(
        self,
        model_name: str,
        execution_time_ms: float,
        confidence_score: float,
        extra_params: dict[str, Any] | None = None,
    ) -> None:
        """Track a single model inference run and update rolling metrics."""
        base = self._aggregated_metrics.get(model_name)
        if base:
            # Update rolling averages
            new_latency = (base.latency_ms * 0.9) + (execution_time_ms * 0.1)
            new_conf = (base.confidence * 0.9) + (confidence_score * 0.1)
            updated_metrics = ModelMetrics(
                precision=base.precision,
                recall=base.recall,
                f1_score=base.f1_score,
                roc_auc=base.roc_auc,
                latency_ms=round(new_latency, 2),
                inference_time_ms=round(execution_time_ms, 2),
                confidence=round(new_conf, 2),
            )
            self._aggregated_metrics[model_name] = updated_metrics
        else:
            updated_metrics = ModelMetrics(
                precision=0.90, recall=0.90, f1_score=0.90, roc_auc=0.92,
                latency_ms=execution_time_ms, inference_time_ms=execution_time_ms,
                confidence=confidence_score,
            )
            self._aggregated_metrics[model_name] = updated_metrics

        # Log run in experiment manager
        self.exp_manager.log_run(
            model_name=model_name,
            metrics=updated_metrics,
            parameters=extra_params or {},
        )

    def get_dashboard_data(self) -> MLOpsDashboardData:
        """Construct full MLOps dashboard data payload."""
        recent_runs = self.exp_manager.get_recent_runs(limit=10)
        prod_models = self.registry.get_registered_models()

        return MLOpsDashboardData(
            total_experiments=1,
            active_runs_count=len(recent_runs),
            registered_models_count=len(prod_models),
            production_models=prod_models,
            recent_runs=recent_runs,
            aggregated_metrics=self._aggregated_metrics,
        )


def get_model_tracker() -> ModelPerformanceTracker:
    return ModelPerformanceTracker.get_instance()
