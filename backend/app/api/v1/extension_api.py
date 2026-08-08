"""
Browser Extension API Router — fast real-time endpoints (< 300ms SLA):
- POST /api/v1/extension/scan-url
- POST /api/v1/extension/scan-text
- POST /api/v1/extension/scan-dom
- GET /api/v1/extension/active-threats
"""

from __future__ import annotations

from fastapi import APIRouter, status

from app.extension.schemas import (
    ActiveThreatsResponse,
    ExtensionScanDOMRequest,
    ExtensionScanDOMResponse,
    ExtensionScanTextRequest,
    ExtensionScanTextResponse,
    ExtensionScanURLRequest,
    ExtensionScanURLResponse,
)
from app.extension.service import BrowserExtensionService

router = APIRouter(prefix="/api/v1/extension", tags=["browser-extension"])


@router.post("/scan-url", response_model=ExtensionScanURLResponse)
async def extension_scan_url(payload: ExtensionScanURLRequest):
    """Fast real-time URL scanning (< 100ms) for Chrome/Edge address bar & link hovers."""
    service = BrowserExtensionService.get_instance()
    return await service.scan_url(payload)


@router.post("/scan-text", response_model=ExtensionScanTextResponse)
async def extension_scan_text(payload: ExtensionScanTextRequest):
    """Fast snippet text scanning for financial scam keywords & unregistered advisory claims."""
    service = BrowserExtensionService.get_instance()
    return await service.scan_text(payload)


@router.post("/scan-dom", response_model=ExtensionScanDOMResponse)
async def extension_scan_dom(payload: ExtensionScanDOMRequest):
    """Fast DOM structure inspection for SEBI logo impersonation and phishing login forms."""
    service = BrowserExtensionService.get_instance()
    return await service.scan_dom(payload)


@router.get("/active-threats", response_model=ActiveThreatsResponse)
async def extension_active_threats():
    """Live active threat feed for Chrome extension badge count & popup alert warnings."""
    service = BrowserExtensionService.get_instance()
    return await service.get_active_threats()
