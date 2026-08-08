"""
Metadata Extractor — extracts regulatory authority, circular reference, date, and domain tags.
"""

from __future__ import annotations

import re
from typing import Any


class MetadataExtractor:
    """Extracts structured metadata from regulatory documents and advisories."""

    AUTHORITY_PATTERNS = [
        (r"SEBI|Securities and Exchange Board of India", "SEBI"),
        (r"NSE|National Stock Exchange", "NSE"),
        (r"BSE|Bombay Stock Exchange", "BSE"),
        (r"RBI|Reserve Bank of India", "RBI"),
        (r"CERT-In|Indian Computer Emergency Response Team", "CERT-In"),
    ]

    REF_NUMBER_PATTERNS = [
        r"SEBI/HO/[A-Z0-9/-]+",
        r"NSE/[A-Z0-9/-]+",
        r"BSE/[A-Z0-9/-]+",
        r"RBI/\d{4}-\d{2}/\d+",
        r"CERTIn-[A-Z0-9-]+",
    ]

    SCAM_TYPE_PATTERNS = [
        (r"deepfake|ai generated|synthetic voice|cloned audio", "deepfake_voice_scam"),
        (r"whatsapp|telegram|guaranteed return|tip provider|group channel", "social_media_advisory"),
        (r"phishing|fake website|typosquat|domain spoofing|fake url", "phishing_domain"),
        (r"circular trading|pump and dump|wash trade|insider", "market_manipulation"),
        (r"qr code|payment gateway|upi scam|mule account", "payment_fraud"),
    ]

    def extract(self, text: str, initial_meta: dict[str, Any] | None = None) -> dict[str, Any]:
        """Extract metadata from document text."""
        meta = dict(initial_meta or {})

        # Authority
        if "authority" not in meta:
            for pattern, auth_name in self.AUTHORITY_PATTERNS:
                if re.search(pattern, text, re.IGNORECASE):
                    meta["authority"] = auth_name
                    break
            meta.setdefault("authority", "GENERAL_REGULATION")

        # Ref Number
        if "ref_number" not in meta:
            for pattern in self.REF_NUMBER_PATTERNS:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    meta["ref_number"] = match.group(0)
                    break
            meta.setdefault("ref_number", "UNKNOWN_REF")

        # Scam / Regulatory Category
        categories = []
        for pattern, cat in self.SCAM_TYPE_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                categories.append(cat)
        meta["categories"] = categories if categories else ["general_compliance"]

        # Date extraction heuristic
        date_match = re.search(
            r"\b(\d{1,2}[-/th|st|nd|rd\s]+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[-/,\s]+\d{2,4})\b",
            text,
            re.IGNORECASE,
        )
        if date_match:
            meta["effective_date"] = date_match.group(0)

        return meta
