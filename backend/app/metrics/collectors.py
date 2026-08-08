"""
Prometheus Collectors — custom metric counters, gauges, and histograms.
"""

from __future__ import annotations

import logging

try:
    from prometheus_client import Counter, Gauge, Histogram, REGISTRY
    HAS_PROMETHEUS = True
except ImportError:
    Counter = Gauge = Histogram = None
    REGISTRY = None
    HAS_PROMETHEUS = False

logger = logging.getLogger(__name__)


if HAS_PROMETHEUS:
    # HTTP Metrics
    HTTP_REQUESTS_TOTAL = Counter(
        "sebi_http_requests_total",
        "Total count of HTTP requests",
        ["method", "endpoint", "status_code"],
    )

    HTTP_REQUEST_DURATION_SECONDS = Histogram(
        "sebi_http_request_duration_seconds",
        "HTTP request duration in seconds",
        ["method", "endpoint"],
        buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
    )

    # Scam & Alert Metrics
    SCAMS_DETECTED_TOTAL = Counter(
        "sebi_scams_detected_total",
        "Total number of verified scams detected",
        ["threat_type", "severity"],
    )

    HIGH_RISK_ALERTS_TOTAL = Counter(
        "sebi_high_risk_alerts_total",
        "Total number of high risk security alerts triggered",
        ["alert_type"],
    )

    # Agent Performance Metrics
    AGENT_EXECUTION_SECONDS = Histogram(
        "sebi_agent_execution_seconds",
        "Execution processing time per AI agent",
        ["agent_name"],
        buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
    )

    MODEL_CONFIDENCE_SCORE = Gauge(
        "sebi_model_confidence_score",
        "Current model confidence score per AI module",
        ["model_name"],
    )

    # Database Latency Metrics
    VECTOR_SEARCH_LATENCY_SECONDS = Histogram(
        "sebi_vector_search_latency_seconds",
        "Qdrant vector similarity search latency",
        ["collection_name"],
        buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5),
    )

    GRAPH_TRAVERSAL_LATENCY_SECONDS = Histogram(
        "sebi_graph_traversal_latency_seconds",
        "Neo4j graph database traversal latency",
        ["query_type"],
        buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5),
    )
else:
    # Dummy fallbacks if prometheus_client is missing
    HTTP_REQUESTS_TOTAL = None
    HTTP_REQUEST_DURATION_SECONDS = None
    SCAMS_DETECTED_TOTAL = None
    HIGH_RISK_ALERTS_TOTAL = None
    AGENT_EXECUTION_SECONDS = None
    MODEL_CONFIDENCE_SCORE = None
    VECTOR_SEARCH_LATENCY_SECONDS = None
    GRAPH_TRAVERSAL_LATENCY_SECONDS = None


def record_scam_detected(threat_type: str, severity: str = "CRITICAL"):
    """Helper to increment detected scam counter."""
    if SCAMS_DETECTED_TOTAL:
        SCAMS_DETECTED_TOTAL.labels(threat_type=threat_type, severity=severity).inc()


def record_agent_execution(agent_name: str, duration_seconds: float):
    """Helper to record agent processing time."""
    if AGENT_EXECUTION_SECONDS:
        AGENT_EXECUTION_SECONDS.labels(agent_name=agent_name).observe(duration_seconds)


def record_vector_search(collection_name: str, duration_seconds: float):
    """Helper to record vector search query latency."""
    if VECTOR_SEARCH_LATENCY_SECONDS:
        VECTOR_SEARCH_LATENCY_SECONDS.labels(collection_name=collection_name).observe(duration_seconds)


def record_graph_traversal(query_type: str, duration_seconds: float):
    """Helper to record graph traversal latency."""
    if GRAPH_TRAVERSAL_LATENCY_SECONDS:
        GRAPH_TRAVERSAL_LATENCY_SECONDS.labels(query_type=query_type).observe(duration_seconds)
