"""
Threat Intelligence Schemas — request & response models for domains, IPs, and file hashes.
"""

from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class DomainReputationResponse(BaseModel):
    """Domain reputation threat intel payload."""
    domain: str
    is_malicious: bool
    risk_score: float = Field(..., ge=0.0, le=1.0)
    threat_category: str  # Phishing | Typosquatting | Scam Portal | Clean
    domain_age_days: int | None = None
    whois_registrar: str | None = None
    virustotal_positives: int = 0
    virustotal_total_engines: int = 70
    cert_in_blacklisted: bool = False
    cached: bool = False
    details: dict[str, Any] = Field(default_factory=dict)


class IPReputationResponse(BaseModel):
    """IP address reputation threat intel payload."""
    ip_address: str
    is_malicious: bool
    risk_score: float = Field(..., ge=0.0, le=1.0)
    abuse_confidence_score: int = Field(default=0, ge=0, le=100)
    country_code: str = "IN"
    isp: str = "Unknown ISP"
    tor_exit_node: bool = False
    vpn_proxy_detected: bool = False
    reported_scam_count: int = 0
    cached: bool = False


class FileHashReputationResponse(BaseModel):
    """File hash (SHA256/MD5) threat intel payload."""
    file_hash: str
    hash_type: str  # SHA256 | MD5 | SHA1
    is_malware: bool
    risk_score: float = Field(..., ge=0.0, le=1.0)
    malware_family: str | None = None
    virustotal_positives: int = 0
    virustotal_total_engines: int = 70
    threat_description: str
    cached: bool = False
