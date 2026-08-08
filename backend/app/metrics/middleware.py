"""
Prometheus Middleware — intercepts FastAPI requests to record HTTP metrics.
"""

from __future__ import annotations

import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.metrics.collectors import (
    HTTP_REQUEST_DURATION_SECONDS,
    HTTP_REQUESTS_TOTAL,
)


class PrometheusMetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for measuring HTTP request throughput and latency for Prometheus."""

    async def dispatch(self, request: Request, call_next) -> Response:
        # Ignore metrics scrape endpoint itself to avoid metrics recursion
        if request.url.path == "/metrics":
            return await call_next(request)

        start_time = time.perf_counter()
        response = await call_next(request)
        duration = time.perf_counter() - start_time

        method = request.method
        endpoint = request.url.path
        status_code = str(response.status_code)

        if HTTP_REQUESTS_TOTAL:
            HTTP_REQUESTS_TOTAL.labels(
                method=method,
                endpoint=endpoint,
                status_code=status_code,
            ).inc()

        if HTTP_REQUEST_DURATION_SECONDS:
            HTTP_REQUEST_DURATION_SECONDS.labels(
                method=method,
                endpoint=endpoint,
            ).observe(duration)

        return response
