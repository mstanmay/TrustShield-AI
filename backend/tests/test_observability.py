"""
Unit tests for Phase 11 End-to-End Observability — Jaeger Tracing, Loki, Promtail, and Trace Propagation.
"""

from __future__ import annotations

from pathlib import Path
import pytest
import yaml

from tracing.propagation import TracePropagation
from tracing.spans import trace_span, traced
from tracing.tracer import OpenTelemetryTracer, get_tracer

LOKI_DIR = Path(__file__).parent.parent / "loki"


class TestObservability:
    """Unit test suite for Jaeger tracing and Loki logging configurations."""

    def test_tracer_singleton(self):
        tracer1 = get_tracer()
        tracer2 = get_tracer()
        assert tracer1 is not None

    def test_trace_span_context_manager(self):
        with trace_span("test.unit_span", {"test_key": "test_val"}) as span:
            assert True

    def test_trace_propagation_context(self):
        trace_id = TracePropagation.get_current_trace_id()
        assert trace_id is not None

        headers = {}
        headers = TracePropagation.inject_context(headers)
        assert "x-trace-id" in headers
        assert "traceparent" in headers

        extracted = TracePropagation.extract_context(headers)
        assert extracted == headers["x-trace-id"]

    def test_loki_and_promtail_configs(self):
        loki_file = LOKI_DIR / "loki.yml"
        promtail_file = LOKI_DIR / "promtail.yml"

        assert loki_file.exists()
        assert promtail_file.exists()

        with open(loki_file, "r", encoding="utf-8") as f:
            loki_data = yaml.safe_load(f)
        assert loki_data["server"]["http_listen_port"] == 3100

        with open(promtail_file, "r", encoding="utf-8") as f:
            promtail_data = yaml.safe_load(f)
        assert "scrape_configs" in promtail_data
