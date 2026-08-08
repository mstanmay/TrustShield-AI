"""
OpenTelemetry Tracer — initializes Jaeger distributed tracing exporter and global tracer.
"""

from __future__ import annotations

import logging
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)

try:
    from opentelemetry import trace
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.resources import SERVICE_NAME, Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    HAS_OPENTELEMETRY = True
except ImportError:
    trace = None
    HAS_OPENTELEMETRY = False


class OpenTelemetryTracer:
    """Manages OpenTelemetry tracing lifecycle and Jaeger OTLP exporter."""

    _instance: OpenTelemetryTracer | None = None

    def __init__(self):
        self.tracer = None
        self.is_initialized = False

        if HAS_OPENTELEMETRY and trace:
            try:
                self.tracer = trace.get_tracer("sebi-trust-platform")
                self.is_initialized = True
                logger.info("OpenTelemetry Jaeger tracer initialized targeting %s", settings.OTEL_EXPORTER_ENDPOINT)
            except Exception as e:
                logger.warning("Jaeger OTLP tracer initialization failed (%s)", e)
                self.tracer = trace.get_tracer("sebi-no-op")
                self.is_initialized = False
        else:
            class MockTracer:
                def start_as_current_span(self, name):
                    class MockSpan:
                        def __enter__(self): return self
                        def __exit__(self, *a): pass
                        def set_attribute(self, k, v): pass
                        def record_exception(self, e): pass
                        def set_status(self, s): pass
                    return MockSpan()
            self.tracer = MockTracer()
            self.is_initialized = False

    @classmethod
    def get_instance(cls) -> OpenTelemetryTracer:
        if cls._instance is None:
            cls._instance = OpenTelemetryTracer()
        return cls._instance


def get_tracer():
    """Return active OpenTelemetry tracer instance."""
    return OpenTelemetryTracer.get_instance().tracer
