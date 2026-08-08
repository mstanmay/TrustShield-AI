"""
Complaint Evidence Collector — gathers all artifacts, agent evidence,
verdict, timestamps, URLs/domains/phone numbers from a case.
"""

from __future__ import annotations

import logging
import re
from datetime import datetime
from typing import Any

from app.models.schemas import ComplaintDraft

logger = logging.getLogger(__name__)


class ComplaintCollector:
    """Collects and structures evidence from a completed case for complaint generation."""

    def collect(self, case_data: dict[str, Any]) -> ComplaintDraft:
        """Gather all evidence from a case into a structured complaint draft.

        Args:
            case_data: Full case data including all agent results and verdict.

        Returns:
            ComplaintDraft with all fields populated.
        """
        case_id = case_data.get("case_id", "unknown")
        verdict = case_data.get("final_verdict", {})
        risk_assessment = case_data.get("risk_assessment", {})

        # Collect URLs from all agents
        all_urls: set[str] = set()
        all_domains: set[str] = set()
        all_phones: set[str] = set()
        evidence_summary: list[dict[str, Any]] = []
        timestamps: list[str] = []

        # Timestamp from case
        uploaded_at = case_data.get("uploaded_at")
        if uploaded_at:
            timestamps.append(f"Uploaded: {uploaded_at}")
        timestamps.append(f"Analysis completed: {datetime.utcnow().isoformat()}")

        # ── Collect from each agent result ───────────────────────────────

        # Deepfake agent
        deepfake = case_data.get("deepfake_result")
        if deepfake:
            evidence_summary.append({
                "agent": "Deepfake Detection",
                "confidence": deepfake.get("confidence_score", 0),
                "result": deepfake.get("result", ""),
                "key_findings": [
                    e.get("finding", "") for e in deepfake.get("evidence", [])
                ],
            })

        # Voice agent
        voice = case_data.get("voice_result")
        if voice:
            evidence_summary.append({
                "agent": "Voice Analysis",
                "confidence": voice.get("confidence_score", 0),
                "result": voice.get("result", ""),
                "key_findings": [
                    e.get("finding", "") for e in voice.get("evidence", [])
                ],
            })

        # Document agent
        doc = case_data.get("document_result")
        if doc:
            evidence_summary.append({
                "agent": "Document Verification",
                "confidence": doc.get("confidence_score", 0),
                "result": doc.get("result", ""),
                "key_findings": [
                    e.get("finding", "") for e in doc.get("evidence", [])
                ],
            })
            # Extract URLs and phones from OCR text
            ocr_text = doc.get("ocr_text", "")
            urls = re.findall(r'https?://[^\s<>"]+', ocr_text)
            all_urls.update(urls)
            phones = re.findall(r'(?:\+91|91|0)?[6-9]\d{9}', ocr_text)
            all_phones.update(phones)

            if doc.get("extracted_urls"):
                all_urls.update(doc["extracted_urls"])

        # Phishing agent
        phishing = case_data.get("phishing_result")
        if phishing:
            evidence_summary.append({
                "agent": "Phishing Intelligence",
                "confidence": phishing.get("confidence_score", 0),
                "result": phishing.get("result", ""),
                "key_findings": [
                    e.get("finding", "") for e in phishing.get("evidence", [])
                ],
            })
            if phishing.get("analyzed_urls"):
                all_urls.update(phishing["analyzed_urls"])
            if phishing.get("qr_decoded_url"):
                all_urls.add(phishing["qr_decoded_url"])

        # Extract domains from URLs
        from urllib.parse import urlparse
        for url in all_urls:
            try:
                parsed = urlparse(url)
                if parsed.hostname:
                    all_domains.add(parsed.hostname)
            except Exception:
                pass

        # ── Build complaint body ─────────────────────────────────────────
        verdict_summary = ""
        if verdict:
            verdict_summary = (
                f"Classification: {verdict.get('classification', 'N/A')}\n"
                f"Risk Score: {verdict.get('risk_score', 0):.2%}\n"
                f"Threat Severity: {verdict.get('threat_severity', 'N/A')}\n"
                f"Explanation: {verdict.get('explanation', 'N/A')}"
            )

        subject = f"Fraud Report — Case {case_id}"
        if verdict.get("classification") == "Fraudulent":
            subject = f"URGENT: Fraudulent Activity Detected — Case {case_id}"
        elif verdict.get("classification") == "Suspicious":
            subject = f"Suspicious Activity Report — Case {case_id}"

        complaint_body = self._generate_complaint_body(
            case_id=case_id,
            evidence_summary=evidence_summary,
            verdict=verdict,
            risk_assessment=risk_assessment,
            urls=list(all_urls),
            domains=list(all_domains),
            phones=list(all_phones),
        )

        return ComplaintDraft(
            case_id=case_id,
            subject=subject,
            complaint_body=complaint_body,
            evidence_summary=evidence_summary,
            involved_urls=list(all_urls),
            involved_domains=list(all_domains),
            involved_phone_numbers=list(all_phones),
            timestamps=timestamps,
            verdict_summary=verdict_summary,
        )

    def _generate_complaint_body(
        self,
        case_id: str,
        evidence_summary: list[dict[str, Any]],
        verdict: dict[str, Any],
        risk_assessment: dict[str, Any],
        urls: list[str],
        domains: list[str],
        phones: list[str],
    ) -> str:
        """Generate the structured complaint body text."""
        sections = [
            "COMPLAINT REPORT",
            "=" * 60,
            f"\nCase Reference: {case_id}",
            f"Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}",
            f"\nClassification: {verdict.get('classification', 'N/A')}",
            f"Risk Score: {verdict.get('risk_score', 0):.2%}",
            f"Threat Severity: {verdict.get('threat_severity', 'N/A')}",
            "\n" + "-" * 60,
            "\nDETAILED ANALYSIS:",
        ]

        for agent_summary in evidence_summary:
            sections.append(f"\n  Agent: {agent_summary['agent']}")
            sections.append(f"  Confidence: {agent_summary['confidence']:.2%}")
            sections.append(f"  Result: {agent_summary['result']}")
            if agent_summary.get("key_findings"):
                sections.append("  Key Findings:")
                for finding in agent_summary["key_findings"][:5]:
                    sections.append(f"    • {finding}")

        if urls:
            sections.append(f"\n{'—' * 60}")
            sections.append("\nINVOLVED URLs:")
            for url in urls[:10]:
                sections.append(f"  • {url}")

        if domains:
            sections.append("\nINVOLVED DOMAINS:")
            for domain in domains[:10]:
                sections.append(f"  • {domain}")

        if phones:
            sections.append("\nINVOLVED PHONE NUMBERS:")
            for phone in phones[:10]:
                sections.append(f"  • {phone}")

        if risk_assessment.get("explainable_reasoning"):
            sections.append(f"\n{'—' * 60}")
            sections.append("\nAI REASONING:")
            sections.append(risk_assessment["explainable_reasoning"])

        sections.append(f"\n{'=' * 60}")
        sections.append("END OF REPORT")

        return "\n".join(sections)
