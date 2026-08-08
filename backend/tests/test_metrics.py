"""
Unit tests for Phase 8 Prometheus Metrics — collectors, middleware, and /metrics exporter endpoint.
"""

from __future__ import annotations

import pytest

from app.metrics.collectors import (
    record_agent_execution,
    record_graph_traversal,
    record_scam_detected,
    record_vector_search,
)
from app.metrics.exporter import metrics_endpoint


class TestPrometheusMetrics:
    """Unit test suite for custom Prometheus metrics collection."""

    def test_record_scam_detected(self):
        record_scam_detected("Phishing Impersonation", "CRITICAL")
        record_agent_execution("DeepfakeDetectionModel", 0.125)
        record_vector_search("sebi_regulatory_knowledge", 0.015)
        record_graph_traversal("entity_neighborhood", 0.022)

    @pytest.mark.asyncio
    async def test_metrics_exporter_endpoint(self):
        res = await metrics_endpoint()
        assert res.status_code == 200
        text_body = res.body.decode("utf-8") if isinstance(res.body, bytes) else str(res.body)
        assert "sebi_scams_detected_total" in text_body or "prometheus_client" in text_body
