"""
RabbitMQ Connection Manager — async connection initialization & in-memory event bus fallback.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable

from app.config import settings

logger = logging.getLogger(__name__)

try:
    import aio_pika
    HAS_AIO_PIKA = True
except ImportError:
    aio_pika = None
    HAS_AIO_PIKA = False


class RabbitMQConnection:
    """Connection manager for RabbitMQ event bus."""

    _instance: RabbitMQConnection | None = None

    def __init__(self):
        self.connection = None
        self.channel = None
        self.is_connected = False
        self._local_event_queue: list[dict[str, Any]] = []
        self._local_subscribers: dict[str, list[Callable]] = {}

    @classmethod
    def get_instance(cls) -> RabbitMQConnection:
        if cls._instance is None:
            cls._instance = RabbitMQConnection()
        return cls._instance

    async def connect(self) -> bool:
        """Establish connection to RabbitMQ broker."""
        if not HAS_AIO_PIKA:
            logger.info("aio-pika not installed — using in-memory event bus fallback")
            return False

        try:
            self.connection = await aio_pika.connect_robust(
                settings.RABBITMQ_URL,
                timeout=3.0,
            )
            self.channel = await self.connection.channel()
            self.is_connected = True
            logger.info("Connected to RabbitMQ Event Bus at %s", settings.RABBITMQ_URL)
            return True
        except Exception as e:
            logger.warning("RabbitMQ broker connection failed (%s) — using in-memory event bus fallback", e)
            self.is_connected = False
            return False

    async def close(self) -> None:
        """Close RabbitMQ connection."""
        if self.connection:
            await self.connection.close()
            self.is_connected = False
            logger.info("RabbitMQ connection closed")


def get_rabbitmq_connection() -> RabbitMQConnection:
    return RabbitMQConnection.get_instance()
