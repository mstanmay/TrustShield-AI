"""
JWT Manager — token verification, blacklisting, and revocation checking backed by Redis.
"""

from __future__ import annotations

import logging
from typing import Any

from app.core.redis_client import get_redis

logger = logging.getLogger(__name__)


class JWTBlacklistManager:
    """Manages JWT token blacklisting and instant revocation."""

    _instance: JWTBlacklistManager | None = None
    _local_blacklist: set[str] = set()

    @classmethod
    def get_instance(cls) -> JWTBlacklistManager:
        if cls._instance is None:
            cls._instance = JWTBlacklistManager()
        return cls._instance

    async def revoke_token(self, token_jti: str, expire_seconds: int = 86400) -> bool:
        """Revoke a JWT token by adding its JTI identifier to the blacklist."""
        key = f"jwt:blacklist:{token_jti}"
        try:
            redis = await get_redis()
            if redis:
                await redis.setex(key, expire_seconds, "REVOKED")
        except Exception:
            pass

        self._local_blacklist.add(token_jti)
        logger.info("JWT token JTI '%s' revoked and blacklisted", token_jti)
        return True

    async def is_token_revoked(self, token_jti: str) -> bool:
        """Check if a JWT token JTI is blacklisted."""
        if token_jti in self._local_blacklist:
            return True

        key = f"jwt:blacklist:{token_jti}"
        try:
            redis = await get_redis()
            if redis:
                val = await redis.get(key)
                if val:
                    return True
        except Exception:
            pass

        return False
