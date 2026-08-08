"""
Redis connection pool — used for caching, session data, and Celery broker.
"""

from __future__ import annotations

import logging

import redis.asyncio as aioredis

from app.config import settings

logger = logging.getLogger(__name__)

# Async Redis client for FastAPI
redis_client: aioredis.Redis | None = None


async def init_redis() -> aioredis.Redis | None:
    """Initialize the async Redis connection pool."""
    global redis_client
    try:
        redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=20,
            socket_connect_timeout=0.2,
            socket_timeout=0.2,
        )
        logger.info("Redis connection pool initialized")
        return redis_client
    except Exception as e:
        logger.warning("Redis connection failed (%s) — caching disabled", e)
        redis_client = None
        return None


async def close_redis() -> None:
    """Close the Redis connection pool."""
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None
        logger.info("Redis connection pool closed")


async def get_redis() -> aioredis.Redis:
    """FastAPI dependency: returns the Redis client."""
    if redis_client is None:
        await init_redis()
    return redis_client
