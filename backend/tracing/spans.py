"""
Trace Spans — helper decorators and context managers for distributed tracing spans.
"""

from __future__ import annotations

import functools
import logging
from contextlib import contextmanager
from typing import Any, Callable

from tracing.tracer import get_tracer

logger = logging.getLogger(__name__)


@contextmanager
def trace_span(span_name: str, attributes: dict[str, Any] | None = None):
    """Context manager for recording an OpenTelemetry trace span."""
    tracer = get_tracer()
    attributes = attributes or {}

    if tracer:
        with tracer.start_as_current_span(span_name) as span:
            for k, v in attributes.items():
                span.set_attribute(k, str(v))
            try:
                yield span
            except Exception as e:
                span.record_exception(e)
                span.set_status(trace.Status(trace.StatusCode.ERROR, str(e)))
                raise
    else:
        yield None


def traced(span_name: str, attributes: dict[str, Any] | None = None):
    """Decorator for tracing function execution spans."""
    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            name = span_name or f"{func.__module__}.{func.__name__}"
            with trace_span(name, attributes):
                return func(*args, **kwargs)
        return wrapper
    return decorator
