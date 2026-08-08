"""
Phishing Intelligence Agent (3d)

Analyzes URLs, QR codes, and messaging links for phishing indicators:
- WHOIS domain age / registrant lookup
- SSL certificate validation / issuer check
- Domain reputation (pluggable ReputationProvider — VirusTotal / Google Safe Browsing)
- Typosquatting detection against known SEBI / exchange / broker domains
- QR payload decoding + re-validation of decoded URL

Uses python-whois for WHOIS, ssl module for cert checks, pyzbar for QR decoding.
"""

from __future__ import annotations

import logging
import re
import ssl
import socket
from datetime import datetime
from typing import Any
from urllib.parse import urlparse

from app.agents.base import BaseAgent
from app.adapters.reputation_provider import get_reputation_provider
from app.core.observability import traced_agent
from app.models.enums import AgentType
from app.models.schemas import Evidence, PhishingResult

logger = logging.getLogger(__name__)

# Known legitimate SEBI-related domains
KNOWN_SEBI_DOMAINS = [
    "sebi.gov.in",
    "scores.gov.in",
    "bseindia.com",
    "nseindia.com",
    "cdslindia.com",
    "nsdl.co.in",
    "amfiindia.com",
    "msei.in",
    "bsebti.com",
    "nse-india.com",
    "moneycontrol.com",
    "zerodha.com",
    "groww.in",
    "upstox.com",
    "angelone.in",
    "icicidirect.com",
    "hdfcsec.com",
    "kotaksecurities.com",
    "5paisa.com",
    "sharekhan.com",
]


class PhishingIntelligenceAgent(BaseAgent):
    """Agent 3d: Phishing detection for URLs, QR codes, messaging links."""

    @property
    def agent_type(self) -> AgentType:
        return AgentType.PHISHING

    def __init__(self):
        self._reputation = get_reputation_provider()

    @traced_agent("phishing")
    async def _analyze_impl(self, input_path: str, metadata: dict[str, Any]) -> PhishingResult:
        """Run phishing analysis on URLs / QR codes / messaging content."""
        evidence: list[Evidence] = []
        raw_output: dict[str, Any] = {}
        analyzed_urls: list[str] = []
        typosquat_matches: list[dict[str, Any]] = []
        reputation_scores: dict[str, float] = {}
        qr_decoded_url: str | None = None

        # Collect URLs to analyze
        urls: list[str] = []

        # Direct URL input
        if metadata.get("url"):
            urls.append(metadata["url"])

        # URLs extracted from text content (WhatsApp/Telegram/email)
        if metadata.get("text_content"):
            text_urls = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', metadata["text_content"])
            urls.extend(text_urls)

        # URLs extracted by document agent
        if metadata.get("extracted_urls"):
            urls.extend(metadata["extracted_urls"])

        # QR code decoding
        if metadata.get("input_type") in ("qr_code", "QR_CODE", "image", "IMAGE"):
            decoded = await self._decode_qr(input_path, metadata.get("file_data", b""))
            if decoded:
                qr_decoded_url = decoded
                urls.append(decoded)
                evidence.append(Evidence(
                    finding=f"QR code decoded to URL: {decoded}",
                    severity="info",
                    detail={"qr_url": decoded},
                ))

        # Deduplicate
        urls = list(set(urls))
        analyzed_urls = urls
        raw_output["urls_analyzed"] = urls

        if not urls:
            return PhishingResult(
                result="No URLs found to analyze",
                confidence_score=0.0,
                evidence=evidence,
                raw_model_output=raw_output,
                analyzed_urls=[],
                qr_decoded_url=qr_decoded_url,
            )

        # Analyze each URL
        max_confidence = 0.0
        for url in urls[:10]:  # Cap at 10 URLs
            url_confidence, url_evidence, url_data = await self._analyze_single_url(url)
            evidence.extend(url_evidence)
            max_confidence = max(max_confidence, url_confidence)

            if url_data.get("typosquat_matches"):
                typosquat_matches.extend(url_data["typosquat_matches"])
            if url_data.get("reputation_score") is not None:
                reputation_scores[url] = url_data["reputation_score"]

            raw_output[f"url_analysis_{url[:50]}"] = url_data

        # Overall result
        if max_confidence > 0.7:
            result_text = "HIGH phishing risk — multiple indicators of fraudulent URL(s) detected"
        elif max_confidence > 0.4:
            result_text = "MODERATE phishing risk — some suspicious URL characteristics found"
        elif max_confidence > 0.15:
            result_text = "LOW risk — minor URL anomalies, likely legitimate"
        else:
            result_text = "URLs appear legitimate — no phishing indicators found"

        return PhishingResult(
            result=result_text,
            confidence_score=max_confidence,
            evidence=evidence,
            raw_model_output=raw_output,
            analyzed_urls=analyzed_urls,
            domain_age_days=raw_output.get("domain_age_days"),
            ssl_valid=raw_output.get("ssl_valid"),
            ssl_issuer=raw_output.get("ssl_issuer"),
            registrant_info=raw_output.get("registrant_info", {}),
            typosquat_matches=typosquat_matches,
            reputation_scores=reputation_scores,
            qr_decoded_url=qr_decoded_url,
        )

    async def _analyze_single_url(self, url: str) -> tuple[float, list[Evidence], dict[str, Any]]:
        """Analyze a single URL for phishing indicators. Returns (confidence, evidence, data)."""
        evidence: list[Evidence] = []
        data: dict[str, Any] = {}
        confidence = 0.0

        parsed = urlparse(url)
        domain = parsed.hostname or ""
        data["domain"] = domain

        # ── 1. Typosquatting Detection ───────────────────────────────────
        typo_matches = self._check_typosquatting(domain)
        if typo_matches:
            data["typosquat_matches"] = typo_matches
            best_match = typo_matches[0]
            confidence += 0.4
            evidence.append(Evidence(
                finding=f"Domain '{domain}' is suspiciously similar to known domain '{best_match['known_domain']}' "
                        f"(edit distance: {best_match['distance']})",
                severity="critical",
                detail=best_match,
            ))

        # ── 2. WHOIS Domain Age ──────────────────────────────────────────
        try:
            import whois as python_whois
            w = python_whois.whois(domain)
            creation_date = w.creation_date
            if isinstance(creation_date, list):
                creation_date = creation_date[0]
            if creation_date:
                age_days = (datetime.utcnow() - creation_date).days
                data["domain_age_days"] = age_days
                data["registrant_info"] = {
                    "registrar": getattr(w, "registrar", None),
                    "org": getattr(w, "org", None),
                    "country": getattr(w, "country", None),
                }

                if age_days < 30:
                    confidence += 0.3
                    evidence.append(Evidence(
                        finding=f"Domain registered very recently ({age_days} days ago)",
                        severity="critical",
                        detail={"domain_age_days": age_days},
                    ))
                elif age_days < 180:
                    confidence += 0.15
                    evidence.append(Evidence(
                        finding=f"Domain is relatively new ({age_days} days old)",
                        severity="warning",
                        detail={"domain_age_days": age_days},
                    ))
        except Exception as e:
            logger.warning("WHOIS lookup failed for %s: %s", domain, e)
            data["whois_error"] = str(e)

        # ── 3. SSL Certificate Check ─────────────────────────────────────
        if parsed.scheme == "https":
            ssl_info = await self._check_ssl(domain)
            data.update(ssl_info)
            if not ssl_info.get("ssl_valid", True):
                confidence += 0.2
                evidence.append(Evidence(
                    finding=f"SSL certificate issue: {ssl_info.get('ssl_error', 'unknown')}",
                    severity="warning",
                    detail=ssl_info,
                ))
        else:
            # HTTP-only site claiming to be financial
            confidence += 0.15
            evidence.append(Evidence(
                finding="URL uses HTTP (not HTTPS) — unusual for financial services",
                severity="warning",
                detail={"scheme": parsed.scheme},
            ))

        # ── 4. Domain Reputation Check ───────────────────────────────────
        try:
            rep_result = await self._reputation.check_url(url)
            data["reputation_score"] = rep_result.risk_score
            if rep_result.is_malicious:
                confidence += 0.4
                evidence.append(Evidence(
                    finding=f"Domain flagged as malicious by {rep_result.provider} (score: {rep_result.risk_score:.2f})",
                    severity="critical",
                    detail={"provider": rep_result.provider, "score": rep_result.risk_score},
                ))
        except Exception as e:
            logger.warning("Reputation check failed: %s", e)

        # ── 5. URL Pattern Heuristics ────────────────────────────────────
        # Suspicious URL patterns
        suspicious_patterns = [
            (r"@", "URL contains @ symbol (credential phishing pattern)"),
            (r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", "URL uses raw IP address instead of domain"),
            (r"bit\.ly|tinyurl|t\.co|goo\.gl|is\.gd|rebrand\.ly", "URL uses link shortener"),
            (r"login|signin|verify|secure|account|update|confirm", "URL contains sensitive action keywords"),
        ]
        for pattern, description in suspicious_patterns:
            if re.search(pattern, url, re.IGNORECASE):
                confidence += 0.1
                evidence.append(Evidence(
                    finding=description,
                    severity="warning",
                    detail={"pattern": pattern, "url": url[:100]},
                ))

        confidence = min(confidence, 1.0)
        return confidence, evidence, data

    def _check_typosquatting(self, domain: str) -> list[dict[str, Any]]:
        """Check if domain is a typosquatting variant of known SEBI/financial domains."""
        matches = []
        domain_lower = domain.lower().replace("www.", "")

        for known in KNOWN_SEBI_DOMAINS:
            distance = self._levenshtein_distance(domain_lower, known)
            # Close but not exact match
            if 0 < distance <= 3:
                matches.append({
                    "known_domain": known,
                    "suspicious_domain": domain_lower,
                    "distance": distance,
                })

        # Sort by distance (closest match first)
        matches.sort(key=lambda x: x["distance"])
        return matches

    @staticmethod
    def _levenshtein_distance(s1: str, s2: str) -> int:
        """Compute Levenshtein edit distance between two strings."""
        if len(s1) < len(s2):
            return PhishingIntelligenceAgent._levenshtein_distance(s2, s1)
        if len(s2) == 0:
            return len(s1)

        prev_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            curr_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = prev_row[j + 1] + 1
                deletions = curr_row[j] + 1
                substitutions = prev_row[j] + (c1 != c2)
                curr_row.append(min(insertions, deletions, substitutions))
            prev_row = curr_row

        return prev_row[-1]

    async def _check_ssl(self, domain: str) -> dict[str, Any]:
        """Check SSL certificate validity and issuer."""
        result: dict[str, Any] = {"ssl_valid": False}
        try:
            ctx = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=5) as sock:
                with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    if cert:
                        result["ssl_valid"] = True
                        result["ssl_issuer"] = str(cert.get("issuer", ""))
                        result["ssl_subject"] = str(cert.get("subject", ""))
                        result["ssl_not_after"] = cert.get("notAfter", "")
                        result["ssl_serial"] = cert.get("serialNumber", "")
        except ssl.SSLCertVerificationError as e:
            result["ssl_error"] = f"Certificate verification failed: {e}"
        except socket.timeout:
            result["ssl_error"] = "Connection timed out"
        except Exception as e:
            result["ssl_error"] = str(e)

        return result

    async def _decode_qr(self, input_path: str, file_data: bytes = b"") -> str | None:
        """Decode QR code from image and extract URL payload."""
        try:
            from PIL import Image
            from pyzbar.pyzbar import decode
            import io

            if file_data:
                img = Image.open(io.BytesIO(file_data))
            else:
                img = Image.open(input_path)

            decoded_objects = decode(img)
            for obj in decoded_objects:
                data = obj.data.decode("utf-8", errors="ignore")
                # Check if decoded content is a URL
                if data.startswith("http://") or data.startswith("https://"):
                    return data
                # Some QR codes have URLs without scheme
                if "." in data and "/" in data:
                    return f"https://{data}"

            return None
        except ImportError:
            logger.warning("pyzbar or Pillow not installed — QR decoding unavailable")
            return None
        except Exception as e:
            logger.error("QR decoding failed: %s", e)
            return None
