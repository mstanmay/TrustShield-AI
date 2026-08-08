"""
MLflow Model Registry — registers production model versions and manages lifecycle stages.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from mlflow.models.schemas import ModelVersionInfo

logger = logging.getLogger(__name__)


class ModelRegistry:
    """Registry for production ML model versions."""

    _instance: ModelRegistry | None = None

    def __init__(self):
        self._registered_models: dict[str, list[ModelVersionInfo]] = {}
        self._initialize_seed_models()

    @classmethod
    def get_instance(cls) -> ModelRegistry:
        if cls._instance is None:
            cls._instance = ModelRegistry()
        return cls._instance

    def _initialize_seed_models(self):
        """Seed registry with initial production model versions."""
        seeds = [
            ("DeepfakeDetectionModel", "v1.2.0", "Production", "Landmark jitter & facial temporal artifact classifier"),
            ("VoiceCloningDetector", "v1.1.0", "Production", "F0 contour & spectral flatness audio fingerprint model"),
            ("DocumentVerificationOCR", "v2.0.1", "Production", "Tesseract OCR & SEBI circular format validator"),
            ("PhishingURLScanner", "v1.5.0", "Production", "Levenshtein typosquatting & reputation scoring model"),
            ("RiskAssessmentLLM", "v4.6.0", "Production", "Anthropic Claude 4.6 Thinking + RAG reasoning engine"),
        ]

        now_str = datetime.utcnow().isoformat()
        for name, ver, stage, desc in seeds:
            version_info = ModelVersionInfo(
                model_name=name,
                version=ver,
                stage=stage,
                run_id=f"run-{name.lower()}-001",
                source=f"models://{name}/{ver}",
                creation_timestamp=now_str,
                description=desc,
            )
            self._registered_models.setdefault(name, []).append(version_info)

    def register_model_version(
        self,
        model_name: str,
        version: str,
        run_id: str,
        stage: str = "Production",
        description: str | None = None,
    ) -> ModelVersionInfo:
        """Register a new version of a model into the registry."""
        version_info = ModelVersionInfo(
            model_name=model_name,
            version=version,
            stage=stage,
            run_id=run_id,
            source=f"models://{model_name}/{version}",
            creation_timestamp=datetime.utcnow().isoformat(),
            description=description or f"Registered version {version} of {model_name}",
        )
        self._registered_models.setdefault(model_name, []).append(version_info)
        logger.info("Registered model '%s' version %s in stage '%s'", model_name, version, stage)
        return version_info

    def get_registered_models(self) -> list[ModelVersionInfo]:
        """Return all active production model versions."""
        production_models = []
        for name, versions in self._registered_models.items():
            if versions:
                production_models.append(versions[-1])
        return production_models
