"""
Unit tests for the Complaint Assistant.
"""

from __future__ import annotations

import pytest

from app.complaint_assistant.collector import ComplaintCollector
from app.complaint_assistant.generator import ComplaintGenerator
from app.models.enums import ComplaintStatus


class TestComplaintCollector:
    """Tests for ComplaintCollector."""

    def test_collects_urls_from_phishing_result(self):
        collector = ComplaintCollector()
        case_data = {
            "case_id": "test-case-001",
            "phishing_result": {
                "analyzed_urls": ["https://fake.com", "https://scam.com"],
                "qr_decoded_url": "https://qr-scam.com",
                "evidence": [],
                "confidence_score": 0.8,
                "result": "High phishing risk",
            },
            "final_verdict": {
                "classification": "Fraudulent",
                "risk_score": 0.85,
                "threat_severity": "Critical",
                "explanation": "Test explanation",
            },
        }

        draft = collector.collect(case_data)

        assert "https://fake.com" in draft.involved_urls
        assert "https://scam.com" in draft.involved_urls
        assert "https://qr-scam.com" in draft.involved_urls
        assert draft.case_id == "test-case-001"

    def test_collects_phone_numbers_from_document(self):
        collector = ComplaintCollector()
        case_data = {
            "case_id": "test-case-002",
            "document_result": {
                "ocr_text": "Call 9876543210 for guaranteed returns!",
                "evidence": [],
                "confidence_score": 0.5,
                "result": "Moderate risk",
            },
            "final_verdict": {"classification": "Suspicious", "risk_score": 0.5, "threat_severity": "Medium"},
        }

        draft = collector.collect(case_data)
        assert "9876543210" in draft.involved_phone_numbers

    def test_generates_complaint_body(self):
        collector = ComplaintCollector()
        case_data = {
            "case_id": "test-case-003",
            "final_verdict": {"classification": "Fraudulent", "risk_score": 0.9, "threat_severity": "Critical"},
        }

        draft = collector.collect(case_data)
        assert "COMPLAINT REPORT" in draft.complaint_body
        assert "test-case-003" in draft.complaint_body


class TestComplaintGenerator:
    """Tests for ComplaintGenerator."""

    def test_generate_draft_status(self):
        generator = ComplaintGenerator()
        case_data = {
            "case_id": "test-case-004",
            "final_verdict": {"classification": "Suspicious", "risk_score": 0.5, "threat_severity": "Medium"},
        }

        draft = generator.generate_draft(case_data)
        assert draft.status == ComplaintStatus.DRAFT_READY

    def test_confirm_draft_changes_status(self):
        generator = ComplaintGenerator()
        case_data = {
            "case_id": "test-case-005",
            "final_verdict": {"classification": "Fraudulent", "risk_score": 0.8, "threat_severity": "High"},
        }

        draft = generator.generate_draft(case_data)
        confirmed = generator.confirm_draft(draft, complainant_name="Test User")

        assert confirmed.status == ComplaintStatus.READY_FOR_SUBMISSION
        assert confirmed.complainant_name == "Test User"

    def test_scores_format_conversion(self):
        generator = ComplaintGenerator()
        case_data = {
            "case_id": "test-case-006",
            "final_verdict": {"classification": "Fraudulent", "risk_score": 0.9, "threat_severity": "Critical"},
        }

        draft = generator.generate_draft(case_data)
        scores_data = generator.to_scores_format(draft)

        assert "complaint_type" in scores_data
        assert "subject" in scores_data
        assert scores_data["nature_of_complaint"] == "Fraudulent / Scam Activity"
        assert scores_data["status"] == "DRAFT_READY"
