"""
RabbitMQ Exchange & Queue Topology — exchange declarations, retry queues, and Dead Letter Queues (DLQ).
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Exchanges
EXCHANGE_EVENTS_TOPIC = "sebi.events.topic"
EXCHANGE_EVENTS_DLX = "sebi.events.dlx"

# Queues
QUEUE_CASE_PROCESSING = "sebi.case.processing.queue"
QUEUE_CASE_RETRY = "sebi.case.retry.queue"
QUEUE_DEAD_LETTER = "sebi.case.dlq"
QUEUE_NOTIFICATIONS = "sebi.notifications.queue"

# Routing Keys
ROUTING_KEY_CASE_UPLOADED = "case.uploaded"
ROUTING_KEY_ANALYSIS_REQUESTED = "analysis.requested"
ROUTING_KEY_ANALYSIS_COMPLETED = "analysis.completed"
ROUTING_KEY_ANALYSIS_FAILED = "analysis.failed"
ROUTING_KEY_ALERT_TRIGGERED = "alert.triggered"
ROUTING_KEY_DEAD_LETTER = "case.dlq"


class QueueTopology:
    """Topology descriptor for RabbitMQ exchange and queue declarations."""

    @staticmethod
    def get_topology_spec() -> dict[str, Any]:
        """Return specifications for exchanges, queues, bindings, and DLQ settings."""
        return {
            "exchanges": [
                {"name": EXCHANGE_EVENTS_TOPIC, "type": "topic", "durable": True},
                {"name": EXCHANGE_EVENTS_DLX, "type": "direct", "durable": True},
            ],
            "queues": [
                {
                    "name": QUEUE_CASE_PROCESSING,
                    "durable": True,
                    "arguments": {
                        "x-dead-letter-exchange": EXCHANGE_EVENTS_DLX,
                        "x-dead-letter-routing-key": ROUTING_KEY_DEAD_LETTER,
                    },
                    "bindings": [
                        {"exchange": EXCHANGE_EVENTS_TOPIC, "routing_key": ROUTING_KEY_CASE_UPLOADED},
                        {"exchange": EXCHANGE_EVENTS_TOPIC, "routing_key": ROUTING_KEY_ANALYSIS_REQUESTED},
                    ],
                },
                {
                    "name": QUEUE_CASE_RETRY,
                    "durable": True,
                    "arguments": {
                        "x-message-ttl": 10000,  # 10s retry delay
                        "x-dead-letter-exchange": EXCHANGE_EVENTS_TOPIC,
                        "x-dead-letter-routing-key": ROUTING_KEY_ANALYSIS_REQUESTED,
                    },
                    "bindings": [],
                },
                {
                    "name": QUEUE_DEAD_LETTER,
                    "durable": True,
                    "arguments": {},
                    "bindings": [
                        {"exchange": EXCHANGE_EVENTS_DLX, "routing_key": ROUTING_KEY_DEAD_LETTER},
                    ],
                },
                {
                    "name": QUEUE_NOTIFICATIONS,
                    "durable": True,
                    "arguments": {},
                    "bindings": [
                        {"exchange": EXCHANGE_EVENTS_TOPIC, "routing_key": ROUTING_KEY_ANALYSIS_COMPLETED},
                        {"exchange": EXCHANGE_EVENTS_TOPIC, "routing_key": ROUTING_KEY_ALERT_TRIGGERED},
                    ],
                },
            ],
        }
