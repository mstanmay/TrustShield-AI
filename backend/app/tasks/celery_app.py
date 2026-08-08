"""
Celery application configuration.
Uses Redis as broker and result backend.
"""

from __future__ import annotations

from celery import Celery

from app.config import settings

celery_app = Celery(
    "sebi_fraud_detection",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_soft_time_limit=300,  # 5 min soft limit
    task_time_limit=600,  # 10 min hard limit
    result_expires=86400,  # Results expire after 24 hours
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["app.tasks"])
