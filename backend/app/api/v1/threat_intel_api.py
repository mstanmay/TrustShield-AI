"""
Threat Intelligence REST API Router — endpoints:
- GET /api/v1/threat-intel/domain
- GET /api/v1/threat-intel/ip
- GET /api/v1/threat-intel/file-hash
"""

from __future__ import annotations

from fastapi import APIRouter, Query, status

from app.threat_intel.schemas import (
    DomainReputationResponse,
    FileHashReputationResponse,
    IPReputationResponse,
)
from app.threat_intel.service import ThreatIntelService

router = APIRouter(prefix="/api/v1/threat-intel", tags=["threat-intelligence"])


@router.get("/domain", response_model=DomainReputationResponse)
async def get_domain_threat_intel(
    domain: str = Query(..., min_length=3, description="Domain name to check (e.g., sebl.gov.in)"),
):
    """Retrieve domain reputation score, Whois age, and CERT-In blacklist status."""
    service = ThreatIntelService.get_instance()
    return await service.get_domain_reputation(domain)


@router.get("/ip", response_model=IPReputationResponse)
async def get_ip_threat_intel(
    ip_address: str = Query(..., min_length=7, description="IPv4 or IPv6 address to check"),
):
    """Retrieve IP address reputation, AbuseIPDB confidence score, geolocation, and TOR exit node status."""
    service = ThreatIntelService.get_instance()
    return await service.get_ip_reputation(ip_address)


@router.get("/file-hash", response_model=FileHashReputationResponse)
async def get_file_hash_threat_intel(
    file_hash: str = Query(..., min_length=32, description="File hash (SHA256, MD5, or SHA1) to scan"),
):
    """Retrieve file hash malware reputation across VirusTotal engine database."""
    service = ThreatIntelService.get_instance()
    return await service.get_file_hash_reputation(file_hash)
