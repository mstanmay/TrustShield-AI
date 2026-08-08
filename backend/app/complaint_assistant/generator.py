"""
Complaint Generator — structures complaint data matching SEBI SCORES format fields.
Returns a draft requiring explicit user confirmation before marking ready for submission.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from app.complaint_assistant.collector import ComplaintCollector
from app.models.enums import ComplaintStatus
from app.models.schemas import ComplaintDraft

logger = logging.getLogger(__name__)


class ComplaintGenerator:
    """Generates structured SEBI SCORES complaint drafts from case data."""

    def __init__(self):
        self._collector = ComplaintCollector()

    def generate_draft(self, case_data: dict[str, Any]) -> ComplaintDraft:
        """Generate a complaint draft from completed case data.

        The draft is returned with status DRAFT_READY and requires
        explicit user confirmation before being marked READY_FOR_SUBMISSION.

        Args:
            case_data: Full case data including all agent results and verdict.

        Returns:
            ComplaintDraft ready for user review.
        """
        # Collect evidence
        draft = self._collector.collect(case_data)

        # Enrich complaint body with RAG-retrieved regulations
        try:
            from app.rag.pipeline.rag_pipeline import RAGPipeline
            rag_pipeline = RAGPipeline()
            query_str = f"{draft.subject} {draft.verdict_summary}"
            rag_results = rag_pipeline.retrieve_context(query_str, top_k=2)
            if rag_results:
                reg_context = RAGPipeline._format_context(rag_results)
                draft.complaint_body += f"\n\n{'—' * 60}\nRELEVANT SEBI/RBI REGULATORY REFERENCES (RAG):\n{reg_context}"
        except Exception as e:
            logger.debug("RAG regulatory enrichment in complaint generator skipped: %s", e)

        # Ensure draft status
        draft.status = ComplaintStatus.DRAFT_READY

        logger.info(
            "Generated complaint draft for case %s (status: %s)",
            draft.case_id,
            draft.status.value,
        )

        return draft

    def confirm_draft(
        self,
        draft: ComplaintDraft,
        complainant_name: str | None = None,
        edits: dict[str, Any] | None = None,
    ) -> ComplaintDraft:
        """Apply user edits and confirm a draft for submission.

        Args:
            draft: The draft to confirm.
            complainant_name: Optional complainant name to add.
            edits: Optional field-level edits (e.g., updated subject, body).

        Returns:
            Updated ComplaintDraft with status READY_FOR_SUBMISSION.
        """
        if complainant_name:
            draft.complainant_name = complainant_name

        if edits:
            if "subject" in edits:
                draft.subject = edits["subject"]
            if "complaint_body" in edits:
                draft.complaint_body = edits["complaint_body"]

        draft.status = ComplaintStatus.READY_FOR_SUBMISSION
        draft.generated_at = datetime.utcnow()

        logger.info(
            "Complaint draft confirmed for case %s (status: %s)",
            draft.case_id,
            draft.status.value,
        )

        return draft

    def to_scores_format(self, draft: ComplaintDraft) -> dict[str, Any]:
        """Convert a ComplaintDraft into SEBI SCORES submission format fields.

        This matches the fields expected by the SEBI SCORES portal.
        """
        return {
            "complaint_type": "Complaint against Intermediary / Listed Company",
            "entity_type": "Other",
            "entity_name": "Unknown — See Evidence",
            "complainant_name": draft.complainant_name or "Anonymous",
            "subject": draft.subject,
            "complaint_description": draft.complaint_body,
            "nature_of_complaint": "Fraudulent / Scam Activity",
            "evidence_attached": True,
            "evidence_documents": [
                {
                    "description": f"AI Analysis Report — Case {draft.case_id}",
                    "type": "pdf",
                }
            ],
            "involved_urls": draft.involved_urls,
            "involved_domains": draft.involved_domains,
            "involved_phone_numbers": draft.involved_phone_numbers,
            "timestamps": draft.timestamps,
            "risk_assessment_summary": draft.verdict_summary,
            "generated_at": draft.generated_at.isoformat(),
            "status": draft.status.value,
        }
