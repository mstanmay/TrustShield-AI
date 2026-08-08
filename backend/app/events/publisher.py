"""
Event Publisher — publishes asynchronous events onto RabbitMQ exchange topics.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from app.events.connection import get_rabbitmq_connection
from app.events.exchange import (
    EXCHANGE_EVENTS_TOPIC,
    ROUTING_KEY_ALERT_TRIGGERED,
    ROUTING_KEY_ANALYSIS_COMPLETED,
    ROUTING_KEY_ANALYSIS_FAILED,
    ROUTING_KEY_ANALYSIS_REQUESTED,
    ROUTING_KEY_CASE_UPLOADED,
)
from app.events.schemas import (
    AlertTriggeredEvent,
    AnalysisCompletedEvent,
    AnalysisFailedEvent,
    AnalysisRequestedEvent,
    CaseUploadedEvent,
)

logger = logging.getLogger(__name__)


class EventPublisher:
    """Publishes domain events to RabbitMQ topic exchange."""

    def __init__(self):
        self.connection_mgr = get_rabbitmq_connection()

    async def publish_case_uploaded(self, event: CaseUploadedEvent) -> bool:
        """Publish `case.uploaded` event."""
        return await self._publish(ROUTING_KEY_CASE_UPLOADED, event.model_dump())

    async def publish_analysis_requested(self, event: AnalysisRequestedEvent) -> bool:
        """Publish `analysis.requested` event."""
        return await self._publish(ROUTING_KEY_ANALYSIS_REQUESTED, event.model_dump())

    async def publish_analysis_completed(self, event: AnalysisCompletedEvent) -> bool:
        """Publish `analysis.completed` event."""
        return await self._publish(ROUTING_KEY_ANALYSIS_COMPLETED, event.model_dump())

    async def publish_analysis_failed(self, event: AnalysisFailedEvent) -> bool:
        """Publish `analysis.failed` event."""
        return await self._publish(ROUTING_KEY_ANALYSIS_FAILED, event.model_dump())

    async def publish_alert_triggered(self, event: AlertTriggeredEvent) -> bool:
        """Publish `alert.triggered` event."""
        return await self._publish(ROUTING_KEY_ALERT_TRIGGERED, event.model_dump())

    async def _publish(self, routing_key: str, payload: dict[str, Any]) -> bool:
        """Internal message publishing implementation."""
        if self.connection_mgr.is_connected and self.connection_mgr.channel:
            import aio_pika
            try:
                exchange = await self.connection_mgr.channel.get_exchange(EXCHANGE_EVENTS_TOPIC)
                message_body = json.dumps(payload).encode("utf-8")
                await exchange.publish(
                    aio_pika.Message(
                        body=message_body,
                        content_type="application/json",
                        headers={"routing_key": routing_key},
                    ),
                    routing_key=routing_key,
                )
                logger.info("Published RabbitMQ event '%s' (routing_key: %s)", payload.get("event_id"), routing_key)
                return True
            except Exception as e:
                logger.warning("RabbitMQ publish failed (%s) — pushing to in-memory event bus", e)

        # Fallback memory event store
        self.connection_mgr._local_event_queue.append({
            "routing_key": routing_key,
            "payload": payload,
        })
        logger.info("Pushed in-memory event '%s' (routing_key: %s)", payload.get("event_id"), routing_key)

        # Invoke local subscribers if registered
        subscribers = self.connection_mgr._local_subscribers.get(routing_key, [])
        for sub in subscribers:
            try:
                if callable(sub):
                    sub(payload)
            except Exception as sub_err:
                logger.error("Error in local event subscriber: %s", sub_err)

        return True
