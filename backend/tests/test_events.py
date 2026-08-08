"""
Unit tests for Phase 5 RabbitMQ Event Bus — schemas, exchanges, publisher, consumer, and DLQ routing.
"""

from __future__ import annotations

import pytest
import uuid

from app.events.connection import get_rabbitmq_connection
from app.events.consumer import EventConsumer
from app.events.exchange import (
    EXCHANGE_EVENTS_DLX,
    EXCHANGE_EVENTS_TOPIC,
    QUEUE_CASE_PROCESSING,
    QUEUE_DEAD_LETTER,
    QueueTopology,
)
from app.events.publisher import EventPublisher
from app.events.schemas import (
    AlertTriggeredEvent,
    AnalysisCompletedEvent,
    CaseUploadedEvent,
)


class TestEventBus:
    """Unit tests for RabbitMQ event bus architecture."""

    def test_topology_spec(self):
        spec = QueueTopology.get_topology_spec()
        exchanges = [e["name"] for e in spec["exchanges"]]
        queues = [q["name"] for q in spec["queues"]]

        assert EXCHANGE_EVENTS_TOPIC in exchanges
        assert EXCHANGE_EVENTS_DLX in exchanges
        assert QUEUE_CASE_PROCESSING in queues
        assert QUEUE_DEAD_LETTER in queues

    @pytest.mark.asyncio
    async def test_publish_and_subscribe_local_event(self):
        publisher = EventPublisher()
        consumer = EventConsumer()

        received_events = []

        def on_case_uploaded(payload):
            received_events.append(payload)

        consumer.subscribe_local("case.uploaded", on_case_uploaded)

        case_id = str(uuid.uuid4())
        event = CaseUploadedEvent(
            event_id=f"evt-{uuid.uuid4().hex[:12]}",
            event_type="case.uploaded",
            correlation_id=case_id,
            case_id=case_id,
            input_type="url",
            artifact_path="",
            metadata={"url": "https://sebl.gov.in"},
        )

        success = await publisher.publish_case_uploaded(event)
        assert success is True
        assert len(received_events) == 1
        assert received_events[0]["case_id"] == case_id

    def test_dead_letter_queue_routing(self):
        consumer = EventConsumer()
        payload = {"case_id": "case-failed-101", "input_type": "url"}
        dlq_entry = consumer.route_to_dlq(payload, "Malformed document structure")

        assert dlq_entry["dlq_id"] == "dlq-case-failed-101"
        assert dlq_entry["status"] == "DEAD_LETTERED"
        assert dlq_entry["error_reason"] == "Malformed document structure"
