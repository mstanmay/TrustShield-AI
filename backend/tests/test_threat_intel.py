"""
Unit tests for Phase 10 Threat Intelligence Service — domain, IP, file hash lookups, and REST APIs.
"""

from __future__ import annotations

import pytest

from app.threat_intel.service import ThreatIntelService


class TestThreatIntelService:
    """Unit test suite for Threat Intelligence Service."""

    @pytest.mark.asyncio
    async def test_domain_reputation_blacklisted(self):
        service = ThreatIntelService.get_instance()
        res = await service.get_domain_reputation("sebl.gov.in")

        assert res.is_malicious is True
        assert res.risk_score >= 0.85
        assert res.cert_in_blacklisted is True
        assert "CERT-In" in res.threat_category or "Typosquatting" in res.threat_category

    @pytest.mark.asyncio
    async def test_domain_reputation_clean(self):
        service = ThreatIntelService.get_instance()
        res = await service.get_domain_reputation("sebi.gov.in")

        assert res.is_malicious is False
        assert res.risk_score < 0.20
        assert res.threat_category == "Clean"

    @pytest.mark.asyncio
    async def test_ip_reputation_malicious(self):
        service = ThreatIntelService.get_instance()
        res = await service.get_ip_reputation("185.220.101.5")

        assert res.is_malicious is True
        assert res.abuse_confidence_score >= 90
        assert res.tor_exit_node is True

    @pytest.mark.asyncio
    async def test_file_hash_reputation_malware(self):
        service = ThreatIntelService.get_instance()
        res = await service.get_file_hash_reputation("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")

        assert res.is_malware is True
        assert res.virustotal_positives >= 40
        assert res.malware_family is not None
