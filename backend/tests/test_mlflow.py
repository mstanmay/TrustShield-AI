"""
Unit tests for Phase 4 MLflow MLOps — Experiment Tracking, Model Registry, Metrics, and Dashboard APIs.
"""

from __future__ import annotations

import pytest

from mlflow.experiments.manager import ExperimentManager
from mlflow.models.schemas import ModelMetrics
from mlflow.registry.registry import ModelRegistry
from mlflow.tracking.tracker import ModelPerformanceTracker, get_model_tracker


class TestMLflowMLOps:
    """Unit tests for MLflow lifecycle tracking and model registry."""

    def test_experiment_manager_log_run(self):
        exp_mgr = ExperimentManager.get_instance()
        metrics = ModelMetrics(
            precision=0.95,
            recall=0.92,
            f1_score=0.935,
            roc_auc=0.97,
            latency_ms=120.0,
            inference_time_ms=105.0,
            confidence=0.91,
        )

        run_info = exp_mgr.log_run(
            model_name="DeepfakeDetectionModel",
            metrics=metrics,
            parameters={"threshold": 0.65},
        )

        assert run_info.model_name == "DeepfakeDetectionModel"
        assert run_info.metrics.precision == 0.95
        assert run_info.metrics.f1_score == 0.935
        assert run_info.status == "FINISHED"

    def test_model_registry_seed_and_registration(self):
        registry = ModelRegistry.get_instance()
        prod_models = registry.get_registered_models()
        assert len(prod_models) >= 5

        # Register new version
        new_version = registry.register_model_version(
            model_name="DeepfakeDetectionModel",
            version="v2.0.0",
            run_id="run-test-002",
            stage="Production",
            description="Upgraded ResNet50 + Vision Transformer model",
        )
        assert new_version.version == "v2.0.0"
        assert new_version.stage == "Production"

    def test_model_tracker_dashboard_data(self):
        tracker = get_model_tracker()
        tracker.track_inference(
            model_name="PhishingURLScanner",
            execution_time_ms=42.0,
            confidence_score=0.98,
        )

        dashboard = tracker.get_dashboard_data()
        assert dashboard.registered_models_count >= 5
        assert "PhishingURLScanner" in dashboard.aggregated_metrics
        assert dashboard.aggregated_metrics["PhishingURLScanner"].precision >= 0.90
