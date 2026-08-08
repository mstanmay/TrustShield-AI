"""
Rate Limiter — sliding window & token bucket rate limiter backed by Redis with local memory fallback.
"""

from __future__ import annotations

import logging
import time
from typing import Any
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.redis_client import get_redis

logger = logging.getLogger(__name__)


class RateLimiter:
    """Sliding window token bucket rate limiter."""

    _instance: RateLimiter | None = None

    def __init__(self):
        self._local_buckets: dict[str, list[float]] = {}

    @classmethod
    def get_instance(cls) -> RateLimiter:
        if cls._instance is None:
            cls._instance = RateLimiter()
        return cls._instance

    async def is_rate_limited(self, identifier: str, limit: int = 100, window_seconds: int = 60) -> bool:
        """Check if an IP or User identifier exceeds rate limit."""
        now = time.time()
        key = f"ratelimit:{identifier}"

        # Try Redis sliding window
        try:
            redis = await get_redis()
            if redis:
                pipe = redis.pipeline()
                pipe.zremrangebyscore(key, 0, now - window_seconds)
                pipe.zadd(key, {str(now): now})
                pipe.zcard(key)
                pipe.expire(key, window_seconds)
                results = await pipe.execute()
                count = results[2]
                return count > limit
        except Exception:
            pass

        # Local memory fallback sliding window
        timestamps = self._local_buckets.setdefault(key, [])
        cutoff = now - window_seconds
        self._local_buckets[key] = [t for t in timestamps if t > cutoff]
        self._local_buckets[key].append(now)

        return len(self._local_buckets[key]) > limit


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """FastAPI Middleware enforcing global & IP rate limits."""

    async def dispatch(self, request: Request, call_next) -> Response:
        limiter = RateLimiter.get_instance()
        client_ip = request.client.host if request.client else "127.0.0.1"

        # Stricter limit for auth/login endpoints
        limit = 10 if "/auth/login" in request.url.path else 120

        is_limited = await limiter.is_rate_limited(client_ip, limit=limit, window_seconds=60)
        if is_limited:
            logger.warning("Rate limit exceeded for client IP: %s (path: %s)", client_ip, request.url.path)
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please slow down and try again later."},
            )

        return await call_next(request)
