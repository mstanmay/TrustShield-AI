"""
Application configuration — loaded from environment variables / .env file.
All configurable values centralized here.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ── Application ──────────────────────────────────────────────────────
    APP_NAME: str = "TrustShield AI - SEBI Financial Trust and Fraud Intelligence Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # ── Database (PostgreSQL + pgvector) ─────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://sebi:sebi_secret@localhost:5432/sebi_fraud"
    DATABASE_SYNC_URL: str = "postgresql://sebi:sebi_secret@localhost:5432/sebi_fraud"

    # ── Redis ────────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── Object Storage (S3-compatible, e.g. MinIO) ───────────────────────
    S3_ENDPOINT_URL: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET_NAME: str = "sebi-artifacts"
    S3_REGION: str = "us-east-1"

    # ── JWT Auth ─────────────────────────────────────────────────────────
    JWT_SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_use_openssl_rand_hex_32"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # ── Anthropic LLM ────────────────────────────────────────────────────
    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL_NAME: str = "claude-sonnet-4-20250514"
    LLM_MAX_TOKENS: int = 4096
    LLM_TEMPERATURE: float = 0.1

    # ── Agent Weights (for Risk Assessment scoring) ──────────────────────
    WEIGHT_DEEPFAKE: float = 0.30
    WEIGHT_VOICE: float = 0.20
    WEIGHT_DOCUMENT: float = 0.25
    WEIGHT_PHISHING: float = 0.25

    # ── Agent Timeouts (seconds) ─────────────────────────────────────────
    AGENT_TIMEOUT_SECONDS: int = 120

    # ── Feature Flags ────────────────────────────────────────────────────
    ENABLE_MALWARE_SCAN: bool = False
    ENABLE_VIRUSTOTAL: bool = False
    VIRUSTOTAL_API_KEY: str = ""
    ENABLE_GOOGLE_SAFE_BROWSING: bool = False
    GOOGLE_SAFE_BROWSING_API_KEY: str = ""

    # ── OpenTelemetry ────────────────────────────────────────────────────
    OTEL_ENABLED: bool = True
    OTEL_SERVICE_NAME: str = "sebi-fraud-detection"
    OTEL_EXPORTER_ENDPOINT: str = "http://localhost:4317"

    # ── Celery ───────────────────────────────────────────────────────────
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    # ── Qdrant Vector DB ────────────────────────────────────────────────
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_GRPC_PORT: int = 6334
    QDRANT_API_KEY: str = ""
    # ── MLflow Tracking & Registry ─────────────────────────────────────
    # ── MLflow Tracking & Registry ─────────────────────────────────────
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"
    MLFLOW_EXPERIMENT_NAME: str = "sebi_fraud_detection_models"
    # ── RabbitMQ Event Bus ───────────────────────────────────────────────
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    # ── Neo4j Fraud Intelligence Graph ─────────────────────────────────
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "sebi_graph_secret"
    # ── Threat Intelligence Service ─────────────────────────────────────
    VIRUSTOTAL_API_KEY: str = ""
    ABUSEIPDB_API_KEY: str = ""

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }


# Singleton
settings = Settings()
