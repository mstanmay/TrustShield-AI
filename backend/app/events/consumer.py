"""
Event Consumer — consumes RabbitMQ messages, routes to Celery/LangGraph, and handles retries / DLQ.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Callable

from app.events.connection import get_rabbitmq_connection
from app.events.exchange import (
    QUEUE_CASE_PROCESSING,
    QUEUE_CASE_RETRY,
    QUEUE_DEAD_LETTER,
    QUEUE_NOTIFICATIONS,
)

logger = logging.getLogger(__name__)


class EventConsumer:
    """Consumes asynchronous events from RabbitMQ queues."""

    def __init__(self):
        self.connection_mgr = get_rabbitmq_connection()

    def subscribe_local(self, routing_key: str, callback: Callable[[dict[str, Any]], None]) -> None:
        """Register a callback for local in-memory event bus subscribers."""
        subs = self.connection_mgr._local_subscribers.setdefault(routing_key, [])
        subs.append(callback)

    async def consume_case_processing_queue(
        self, handler: Callable[[dict[str, Any]], Any]
    ) -> None:
        """Consume messages from `sebi.case.processing.queue`."""
        if not self.connection_mgr.is_connected or not self.connection_mgr.channel:
            logger.info("RabbitMQ not connected — listening via in-memory subscriber model")
            return

        try:
            queue = await self.connection_mgr.channel.get_queue(QUEUE_CASE_PROCESSING)
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        payload = json.loads(message.body.decode("utf-8"))
                        logger.info("Received event on %s: %s", QUEUE_CASE_PROCESSING, payload.get("event_id"))
                        await handler(payload)
        except Exception as e:
            logger.error("Error consuming from processing queue: %s", e)

    def route_to_dlq(self, payload: dict[str, Any], error_reason: str) -> dict[str, Any]:
        """Route failed message to Dead Letter Queue (DLQ)."""
        dlq_entry = {
            "dlq_id": f"dlq-{payload.get('case_id', 'unknown')}",
            "original_payload": payload,
            "error_reason": error_reason,
            "status": "DEAD_LETTERED",
        }
        logger.warning("Message landed in Dead Letter Queue (DLQ): %s (Reason: %s)", dlq_entry["dlq_id"], error_reason)
        return dlq_entry
