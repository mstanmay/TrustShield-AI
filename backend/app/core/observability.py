"""
Observability — OpenTelemetry tracing + structured JSON logging.
Provides a @traced_agent decorator that wraps every agent call with a span
recording input/output/latency/confidence for full pipeline inspectability.
"""

from __future__ import annotations

import functools
import logging
import time
from typing import Any, Callable

import structlog

from app.config import settings

# ── Structured Logging Setup ─────────────────────────────────────────────────

def add_trace_id_processor(logger, method_name, event_dict):
    """Processor adding current trace_id to every log event for correlation."""
    try:
        from tracing.propagation import TracePropagation
        event_dict["trace_id"] = TracePropagation.get_current_trace_id()
    except Exception:
        pass
    return event_dict


def setup_logging() -> None:
    """Configure structlog for JSON-formatted structured logging with trace correlation."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            add_trace_id_processor,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(settings.LOG_LEVEL)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Also configure stdlib logging to use structlog
    logging.basicConfig(
        format="%(message)s",
        level=logging.getLevelName(settings.LOG_LEVEL),
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger bound with a name."""
    return structlog.get_logger(name)


# ── OpenTelemetry Setup ──────────────────────────────────────────────────────

_tracer = None


def setup_otel() -> None:
    """Initialize OpenTelemetry tracer and meter providers."""
    global _tracer

    if not settings.OTEL_ENABLED:
        return

    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import (
            BatchSpanProcessor,
            ConsoleSpanExporter,
        )
        from opentelemetry.sdk.resources import Resource

        resource = Resource.create(
            {
                "service.name": settings.OTEL_SERVICE_NAME,
                "service.version": settings.APP_VERSION,
            }
        )

        provider = TracerProvider(resource=resource)

        # Use console exporter for local dev; swap to OTLP for production
        processor = BatchSpanProcessor(ConsoleSpanExporter())
        provider.add_span_processor(processor)

        trace.set_tracer_provider(provider)
        _tracer = trace.get_tracer(settings.OTEL_SERVICE_NAME)

        logger = get_logger("observability")
        logger.info("OpenTelemetry tracing initialized", service=settings.OTEL_SERVICE_NAME)
    except ImportError:
        logger = get_logger("observability")
        logger.warning("OpenTelemetry SDK not installed — tracing disabled")


def get_tracer():
    """Get the global OpenTelemetry tracer."""
    global _tracer
    if _tracer is None:
        try:
            from opentelemetry import trace
            _tracer = trace.get_tracer(settings.OTEL_SERVICE_NAME)
        except ImportError:
            pass
    return _tracer


# ── Agent Tracing Decorator ──────────────────────────────────────────────────

try:
    from opentelemetry import trace
except ImportError:
    trace = None


def traced_agent(agent_name: str) -> Callable:
    """Decorator that wraps an agent's analyze() call with an OpenTelemetry span.

    Records:
    - input metadata
    - output result summary
    - confidence_score
    - execution latency
    - errors
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            logger = get_logger(f"agent.{agent_name}")
            tracer = get_tracer()
            start_time = time.time()

            span_context = None
            if tracer:
                span_context = tracer.start_span(
                    f"agent.{agent_name}.analyze",
                    attributes={
                        "agent.name": agent_name,
                        "agent.input_keys": str(list(kwargs.keys())),
                    },
                )

            try:
                result = await func(*args, **kwargs)
                elapsed_ms = (time.time() - start_time) * 1000

                # Log structured output
                logger.info(
                    "agent_completed",
                    agent=agent_name,
                    confidence_score=getattr(result, "confidence_score", None),
                    execution_time_ms=elapsed_ms,
                    evidence_count=len(getattr(result, "evidence", [])),
                )

                # Record in span
                if span_context:
                    span_context.set_attribute("agent.confidence_score", getattr(result, "confidence_score", 0))
                    span_context.set_attribute("agent.execution_time_ms", elapsed_ms)
                    span_context.set_attribute("agent.evidence_count", len(getattr(result, "evidence", [])))
                    if trace:
                        span_context.set_status(trace.StatusCode.OK if not getattr(result, "error", None) else trace.StatusCode.ERROR)
                    span_context.end()

                # Attach execution time to result
                if hasattr(result, "execution_time_ms"):
                    result.execution_time_ms = elapsed_ms

                return result
            except Exception as e:
                elapsed_ms = (time.time() - start_time) * 1000
                logger.error("agent_failed", agent=agent_name, error=str(e), execution_time_ms=elapsed_ms)
                if span_context:
                    span_context.set_attribute("agent.error", str(e))
                    if trace:
                        span_context.set_status(trace.StatusCode.ERROR, str(e))
                    span_context.end()
                raise

        return wrapper
    return decorator

