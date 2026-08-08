"""
Reputation Provider adapter — pluggable threat intelligence for URL/domain reputation.
Supports: stub (neutral), VirusTotal, Google Safe Browsing.
"""

from __future__ import annotations

import abc
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ReputationResult:
    """Result from a threat intel lookup."""
    provider: str
    is_malicious: bool = False
    risk_score: float = 0.0  # 0 = safe, 1 = malicious
    categories: list[str] = field(default_factory=list)
    detail: dict = field(default_factory=dict)


class ReputationProvider(abc.ABC):
    """Abstract interface for domain/URL reputation checking."""

    @abc.abstractmethod
    async def check_url(self, url: str) -> ReputationResult:
        """Check a URL against threat intelligence."""
        ...

    @abc.abstractmethod
    async def check_domain(self, domain: str) -> ReputationResult:
        """Check a domain against threat intelligence."""
        ...


class StubReputationProvider(ReputationProvider):
    """Stub provider — returns neutral reputation. For local dev only.

    # TODO: upgrade to trained model — connect to VirusTotal or Google Safe Browsing
    """

    async def check_url(self, url: str) -> ReputationResult:
        logger.warning("StubReputationProvider: no real lookup for URL %s", url)
        return ReputationResult(provider="stub", risk_score=0.0)

    async def check_domain(self, domain: str) -> ReputationResult:
        logger.warning("StubReputationProvider: no real lookup for domain %s", domain)
        return ReputationResult(provider="stub", risk_score=0.0)


class VirusTotalProvider(ReputationProvider):
    """VirusTotal API integration for URL/domain reputation.

    Requires VIRUSTOTAL_API_KEY environment variable.
    """

    def __init__(self, api_key: str):
        self._api_key = api_key
        self._base_url = "https://www.virustotal.com/api/v3"

    async def check_url(self, url: str) -> ReputationResult:
        try:
            import httpx
            import base64

            url_id = base64.urlsafe_b64encode(url.encode()).decode().rstrip("=")
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{self._base_url}/urls/{url_id}",
                    headers={"x-apikey": self._api_key},
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
                    malicious = stats.get("malicious", 0)
                    total = sum(stats.values()) or 1
                    risk_score = malicious / total
                    return ReputationResult(
                        provider="virustotal",
                        is_malicious=risk_score > 0.1,
                        risk_score=min(risk_score * 2, 1.0),  # Scale up
                        categories=data.get("data", {}).get("attributes", {}).get("categories", {}).values() if isinstance(data.get("data", {}).get("attributes", {}).get("categories"), dict) else [],
                        detail=stats,
                    )
                else:
                    logger.warning("VirusTotal URL check returned %d", resp.status_code)
        except Exception as e:
            logger.error("VirusTotal URL check failed: %s", e)

        return ReputationResult(provider="virustotal", risk_score=0.0)

    async def check_domain(self, domain: str) -> ReputationResult:
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{self._base_url}/domains/{domain}",
                    headers={"x-apikey": self._api_key},
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    stats = data.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
                    malicious = stats.get("malicious", 0)
                    total = sum(stats.values()) or 1
                    risk_score = malicious / total
                    return ReputationResult(
                        provider="virustotal",
                        is_malicious=risk_score > 0.1,
                        risk_score=min(risk_score * 2, 1.0),
                        detail=stats,
                    )
        except Exception as e:
            logger.error("VirusTotal domain check failed: %s", e)

        return ReputationResult(provider="virustotal", risk_score=0.0)


def get_reputation_provider() -> ReputationProvider:
    """Factory: returns the configured reputation provider."""
    from app.config import settings
    if settings.ENABLE_VIRUSTOTAL and settings.VIRUSTOTAL_API_KEY:
        return VirusTotalProvider(api_key=settings.VIRUSTOTAL_API_KEY)
    return StubReputationProvider()
