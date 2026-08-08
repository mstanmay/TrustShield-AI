"""
API Middleware — CORS, request-id injection, structured request logging.
"""

from __future__ import annotations

import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.observability import get_logger

logger = get_logger("api.middleware")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Inject a unique request ID into every request/response for tracing."""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        start_time = time.time()
        response: Response = await call_next(request)
        elapsed_ms = (time.time() - start_time) * 1000

        response.headers["X-Request-ID"] = request_id

        logger.info(
            "request_completed",
            request_id=request_id,
            method=request.method,
            path=str(request.url.path),
            status_code=response.status_code,
            elapsed_ms=round(elapsed_ms, 2),
        )

        return response
