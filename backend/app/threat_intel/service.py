"""
Threat Intelligence Service — high-level service orchestrating feed lookups and Redis caching.
"""

from __future__ import annotations

import logging
from typing import Any

from app.threat_intel.cache import ThreatIntelCache
from app.threat_intel.feed import ThreatIntelFeedCollector
from app.threat_intel.schemas import (
    DomainReputationResponse,
    FileHashReputationResponse,
    IPReputationResponse,
)

logger = logging.getLogger(__name__)


class ThreatIntelService:
    """Orchestrates Threat Intelligence lookups with Redis caching."""

    _instance: ThreatIntelService | None = None

    def __init__(self):
        self.feed_collector = ThreatIntelFeedCollector()
        self.cache = ThreatIntelCache()

    @classmethod
    def get_instance(cls) -> ThreatIntelService:
        if cls._instance is None:
            cls._instance = ThreatIntelService()
        return cls._instance

    async def get_domain_reputation(self, domain: str) -> DomainReputationResponse:
        """Fetch domain reputation with Redis caching."""
        domain_clean = domain.lower().strip()

        # Check Cache
        cached_data = await self.cache.get_cached("domain", domain_clean)
        if cached_data:
            cached_data["cached"] = True
            return DomainReputationResponse(**cached_data)

        # Query Feeds
        res = await self.feed_collector.query_domain(domain_clean)

        # Cache Result
        await self.cache.set_cached("domain", domain_clean, res.model_dump())
        return res

    async def get_ip_reputation(self, ip_address: str) -> IPReputationResponse:
        """Fetch IP address reputation with Redis caching."""
        ip_clean = ip_address.strip()

        # Check Cache
        cached_data = await self.cache.get_cached("ip", ip_clean)
        if cached_data:
            cached_data["cached"] = True
            return IPReputationResponse(**cached_data)

        # Query Feeds
        res = await self.feed_collector.query_ip(ip_clean)

        # Cache Result
        await self.cache.set_cached("ip", ip_clean, res.model_dump())
        return res

    async def get_file_hash_reputation(self, file_hash: str) -> FileHashReputationResponse:
        """Fetch file hash reputation with Redis caching."""
        hash_clean = file_hash.lower().strip()

        # Check Cache
        cached_data = await self.cache.get_cached("hash", hash_clean)
        if cached_data:
            cached_data["cached"] = True
            return FileHashReputationResponse(**cached_data)

        # Query Feeds
        res = await self.feed_collector.query_file_hash(hash_clean)

        # Cache Result
        await self.cache.set_cached("hash", hash_clean, res.model_dump())
        return res
