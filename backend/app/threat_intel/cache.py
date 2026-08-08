"""
Threat Intel Cache Manager — Redis caching for reputation scores with 12h TTL.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from app.core.redis_client import get_redis

logger = logging.getLogger(__name__)


class ThreatIntelCache:
    """Redis cache manager for Threat Intelligence queries."""

    TTL_SECONDS = 43200  # 12 hours

    async def get_cached(self, key_prefix: str, identifier: str) -> dict[str, Any] | None:
        """Fetch cached threat intel entry."""
        try:
            redis = await get_redis()
            if redis:
                raw = await redis.get(f"intel:{key_prefix}:{identifier}")
                if raw:
                    return json.loads(raw)
        except Exception as e:
            logger.debug("Threat intel cache lookup skipped: %s", e)
        return None

    async def set_cached(self, key_prefix: str, identifier: str, data: dict[str, Any]) -> None:
        """Set threat intel entry in Redis cache."""
        try:
            redis = await get_redis()
            if redis:
                await redis.setex(
                    f"intel:{key_prefix}:{identifier}",
                    self.TTL_SECONDS,
                    json.dumps(data),
                )
        except Exception as e:
            logger.debug("Threat intel cache set skipped: %s", e)
