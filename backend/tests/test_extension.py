"""
Unit tests for Phase 7 Browser Extension Services — real-time URL, text, DOM scanning, and active threat feed.
"""

from __future__ import annotations

import pytest
import time

from app.extension.schemas import (
    ExtensionScanDOMRequest,
    ExtensionScanTextRequest,
    ExtensionScanURLRequest,
)
from app.extension.service import BrowserExtensionService


class TestBrowserExtensionService:
    """Unit test suite for Browser Extension real-time services."""

    @pytest.mark.asyncio
    async def test_scan_url_typosquatting(self):
        service = BrowserExtensionService.get_instance()
        req = ExtensionScanURLRequest(url="https://sebl.gov.in/login")

        start = time.perf_counter()
        res = await service.scan_url(req)
        elapsed_ms = (time.perf_counter() - start) * 1000.0

        assert res.is_phishing is True
        assert res.risk_score >= 0.90
        assert res.action_recommended == "BLOCK"
        assert elapsed_ms < 300.0  # SLA < 300ms

    @pytest.mark.asyncio
    async def test_scan_url_legitimate(self):
        service = BrowserExtensionService.get_instance()
        req = ExtensionScanURLRequest(url="https://sebi.gov.in/circulars.html")

        res = await service.scan_url(req)
        assert res.is_phishing is False
        assert res.risk_score < 0.20
        assert res.action_recommended == "ALLOW"

    @pytest.mark.asyncio
    async def test_scan_text_scam_keywords(self):
        service = BrowserExtensionService.get_instance()
        req = ExtensionScanTextRequest(
            text="Join our Telegram pump group for guaranteed 100% profit insider stock tips!"
        )

        res = await service.scan_text(req)
        assert res.contains_scam_keywords is True
        assert len(res.detected_keywords) >= 2
        assert res.action_recommended == "WARN"

    @pytest.mark.asyncio
    async def test_scan_dom_impersonation(self):
        service = BrowserExtensionService.get_instance()
        req = ExtensionScanDOMRequest(
            page_url="https://fake-sebi-portal.xyz/login",
            dom_text_snippet="Welcome to Official SEBI Investor Verification Portal",
            form_actions=["http://fake-sebi-portal.xyz/submit"],
            has_sebi_logo_mention=True,
        )

        res = await service.scan_dom(req)
        assert res.is_impersonating_sebi is True
        assert res.risk_score >= 0.80
        assert res.action_recommended == "BLOCK"

    @pytest.mark.asyncio
    async def test_get_active_threats(self):
        service = BrowserExtensionService.get_instance()
        threats_res = await service.get_active_threats()

        assert threats_res.total_active_threats >= 3
        assert any(t.type == "Phishing Domain" for t in threats_res.threats)
