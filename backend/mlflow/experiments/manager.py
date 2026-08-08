"""
MLflow Experiment Manager — creates experiments, records runs, and tracks precision, recall, F1, ROC, latency.
"""

from __future__ import annotations

import logging
import time
import uuid
from datetime import datetime
from typing import Any

from app.config import settings
from mlflow.models.schemas import ModelMetrics, RunInfo

logger = logging.getLogger(__name__)

try:
    import mlflow
    HAS_MLFLOW_LIB = True
except ImportError:
    mlflow = None
    HAS_MLFLOW_LIB = False


class ExperimentManager:
    """Manages MLflow experiment tracking and metric logging."""

    _instance: ExperimentManager | None = None

    def __init__(self):
        self.tracking_uri = settings.MLFLOW_TRACKING_URI
        self.experiment_name = settings.MLFLOW_EXPERIMENT_NAME
        self.is_server_connected = False
        self._local_runs: list[RunInfo] = []

        if HAS_MLFLOW_LIB:
            try:
                mlflow.set_tracking_uri(self.tracking_uri)
                mlflow.set_experiment(self.experiment_name)
                self.is_server_connected = True
                logger.info("Connected to MLflow tracking server at %s", self.tracking_uri)
            except Exception as e:
                logger.warning("MLflow tracking server unavailable (%s) — using local MLOps run store", e)
                self.is_server_connected = False
        else:
            logger.info("mlflow package not installed — using local MLOps run store")

    @classmethod
    def get_instance(cls) -> ExperimentManager:
        if cls._instance is None:
            cls._instance = ExperimentManager()
        return cls._instance

    def log_run(
        self,
        model_name: str,
        metrics: ModelMetrics,
        parameters: dict[str, Any] | None = None,
        tags: dict[str, Any] | None = None,
    ) -> RunInfo:
        """Log an experiment run with precision, recall, F1, ROC, latency, and confidence."""
        run_id = f"run-{uuid.uuid4().hex[:12]}"
        now_str = datetime.utcnow().isoformat()
        parameters = parameters or {}
        tags = tags or {"service": "sebi-ai-platform", "agent": model_name}

        if self.is_server_connected and mlflow:
            try:
                with mlflow.start_run(run_name=f"{model_name}-eval") as run:
                    run_id = run.info.run_id
                    mlflow.log_params(parameters)
                    mlflow.set_tags(tags)
                    mlflow.log_metrics({
                        "precision": metrics.precision,
                        "recall": metrics.recall,
                        "f1_score": metrics.f1_score,
                        "roc_auc": metrics.roc_auc,
                        "latency_ms": metrics.latency_ms,
                        "inference_time_ms": metrics.inference_time_ms,
                        "confidence": metrics.confidence,
                    })
            except Exception as e:
                logger.warning("MLflow server log failed: %s", e)

        run_info = RunInfo(
            run_id=run_id,
            experiment_id="exp-1",
            model_name=model_name,
            status="FINISHED",
            metrics=metrics,
            parameters=parameters,
            tags=tags,
            start_time=now_str,
            end_time=now_str,
        )

        self._local_runs.append(run_info)
        logger.info("Logged MLflow run %s for model '%s'", run_id, model_name)
        return run_info

    def get_recent_runs(self, limit: int = 20) -> list[RunInfo]:
        """Return recently logged experiment runs."""
        return list(reversed(self._local_runs))[:limit]
