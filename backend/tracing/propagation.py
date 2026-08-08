"""
Trace Propagation — W3C context propagation helper for HTTP headers, RabbitMQ, and Celery tasks.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

logger = logging.getLogger(__name__)


class TracePropagation:
    """Helper for extracting and injecting W3C Trace Context (traceparent / tracestate)."""

    @staticmethod
    def get_current_trace_id() -> str:
        """Return active trace ID or generate a new trace ID correlation string."""
        try:
            from opentelemetry import trace
            span = trace.get_current_span()
            if span and span.get_span_context().is_valid:
                return f"{span.get_span_context().trace_id:032x}"
        except Exception:
            pass
        return f"trace-{uuid.uuid4().hex}"

    @staticmethod
    def inject_context(headers: dict[str, Any]) -> dict[str, Any]:
        """Inject current trace ID into dictionary headers for RabbitMQ / Celery task propagation."""
        trace_id = TracePropagation.get_current_trace_id()
        headers["x-trace-id"] = trace_id
        headers["traceparent"] = f"00-{trace_id}-0000000000000001-01"
        return headers

    @staticmethod
    def extract_context(headers: dict[str, Any]) -> str:
        """Extract trace ID from dictionary headers."""
        return headers.get("x-trace-id") or headers.get("traceparent") or f"trace-{uuid.uuid4().hex}"
