"""
Complaints API (STEP 6) — Generate, review, and download SEBI SCORES complaint PDFs.

Workflow:
1. POST /complaints/{case_id}/generate → draft (status: DRAFT_READY)
2. PATCH /complaints/{case_id} → user reviews/edits (status: USER_REVIEWED)
3. POST /complaints/{case_id}/confirm → marks READY_FOR_SUBMISSION
4. GET /complaints/{case_id}/pdf → download PDF

NO auto-submission to SEBI — requires explicit user action.
"""

from __future__ import annotations

import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.complaint_assistant.generator import ComplaintGenerator
from app.complaint_assistant.pdf_renderer import ComplaintPDFRenderer
from app.core.database import get_db_session
from app.core.storage import object_storage
from app.models.database import Case, Complaint
from app.models.enums import ComplaintStatus
from app.models.schemas import ComplaintDraft, ComplaintResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/complaints", tags=["complaints"])


class ComplaintEditPayload(BaseModel):
    """Edits a user can make to a complaint draft."""
    complainant_name: str | None = None
    subject: str | None = None
    complaint_body: str | None = None


@router.post("/{case_id}/generate", response_model=ComplaintResponse)
async def generate_complaint(
    case_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Generate a complaint draft from a completed case.

    Also accessible as: POST /api/v1/dashboard/complaints/draft
    """
    # Load case
    result = await db.execute(select(Case).where(Case.case_id == case_id))
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    if case.status != "completed":
        raise HTTPException(status_code=400, detail="Case analysis not yet complete")

    # Build case data dict
    case_data = {
        "case_id": case.case_id,
        "input_type": case.input_type,
        "uploaded_at": case.uploaded_at.isoformat() if case.uploaded_at else None,
        "deepfake_result": case.deepfake_result,
        "voice_result": case.voice_result,
        "document_result": case.document_result,
        "phishing_result": case.phishing_result,
        "risk_assessment": case.risk_assessment_result,
        "final_verdict": case.verdict.__dict__ if case.verdict else {},
    }
    if case.verdict:
        case_data["final_verdict"] = {
            "classification": case.verdict.classification,
            "risk_score": case.verdict.risk_score,
            "threat_severity": case.verdict.threat_severity,
            "explanation": case.verdict.explanation,
        }

    # Generate draft
    generator = ComplaintGenerator()
    draft = generator.generate_draft(case_data)

    # Persist complaint record
    existing = await db.execute(select(Complaint).where(Complaint.case_id == case_id))
    complaint = existing.scalar_one_or_none()

    if complaint:
        # Update existing draft
        complaint.status = ComplaintStatus.DRAFT_READY.value
        complaint.subject = draft.subject
        complaint.complaint_body = draft.complaint_body
        complaint.evidence_summary = draft.evidence_summary
        complaint.involved_urls = draft.involved_urls
        complaint.involved_domains = draft.involved_domains
        complaint.involved_phone_numbers = draft.involved_phone_numbers
        complaint.verdict_summary = draft.verdict_summary
        complaint.draft_json = draft.model_dump()
        complaint.generated_at = datetime.utcnow()
    else:
        complaint = Complaint(
            case_id=case_id,
            status=ComplaintStatus.DRAFT_READY.value,
            subject=draft.subject,
            complaint_body=draft.complaint_body,
            evidence_summary=draft.evidence_summary,
            involved_urls=draft.involved_urls,
            involved_domains=draft.involved_domains,
            involved_phone_numbers=draft.involved_phone_numbers,
            verdict_summary=draft.verdict_summary,
            draft_json=draft.model_dump(),
        )
        db.add(complaint)

    await db.flush()

    return ComplaintResponse(
        case_id=case_id,
        status=ComplaintStatus.DRAFT_READY,
        draft=draft,
        message="Complaint draft generated. Review and confirm before submission.",
    )


@router.patch("/{case_id}", response_model=ComplaintResponse)
async def edit_complaint(
    case_id: str,
    edits: ComplaintEditPayload,
    db: AsyncSession = Depends(get_db_session),
):
    """Review and edit a complaint draft."""
    result = await db.execute(select(Complaint).where(Complaint.case_id == case_id))
    complaint = result.scalar_one_or_none()

    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint draft not found. Generate one first.")

    if edits.complainant_name:
        complaint.complainant_name = edits.complainant_name
    if edits.subject:
        complaint.subject = edits.subject
    if edits.complaint_body:
        complaint.complaint_body = edits.complaint_body

    complaint.status = ComplaintStatus.USER_REVIEWED.value

    # Update draft JSON
    draft_data: dict[str, Any] = dict(complaint.draft_json) if isinstance(complaint.draft_json, dict) else {}
    if edits.complainant_name:
        draft_data["complainant_name"] = edits.complainant_name
    if edits.subject:
        draft_data["subject"] = edits.subject
    if edits.complaint_body:
        draft_data["complaint_body"] = edits.complaint_body
    complaint.draft_json = draft_data

    await db.flush()

    return ComplaintResponse(
        case_id=case_id,
        status=ComplaintStatus.USER_REVIEWED,
        draft=ComplaintDraft(**draft_data) if draft_data else None,
        message="Draft updated. Use POST /confirm to mark ready for submission.",
    )


@router.post("/{case_id}/confirm", response_model=ComplaintResponse)
async def confirm_complaint(
    case_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Confirm a reviewed complaint draft — marks it READY_FOR_SUBMISSION."""
    result = await db.execute(select(Complaint).where(Complaint.case_id == case_id))
    complaint = result.scalar_one_or_none()

    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint draft not found")

    # Generate PDF
    draft_data: dict[str, Any] = dict(complaint.draft_json) if isinstance(complaint.draft_json, dict) else {}
    draft = ComplaintDraft(**draft_data)
    draft.status = ComplaintStatus.READY_FOR_SUBMISSION

    renderer = ComplaintPDFRenderer()
    pdf_bytes = renderer.render(draft)

    # Upload PDF to storage
    try:
        pdf_key = object_storage.upload_complaint_pdf(case_id, pdf_bytes)
        complaint.pdf_path = pdf_key
    except Exception as e:
        logger.error("Failed to upload complaint PDF: %s", e)

    complaint.status = ComplaintStatus.READY_FOR_SUBMISSION.value
    complaint.confirmed_at = datetime.utcnow()

    await db.flush()

    pdf_url = None
    if complaint.pdf_path:
        try:
            pdf_url = object_storage.get_presigned_url(complaint.pdf_path)
        except Exception:
            pass

    return ComplaintResponse(
        case_id=case_id,
        status=ComplaintStatus.READY_FOR_SUBMISSION,
        draft=draft,
        pdf_download_url=pdf_url,
        message="Complaint confirmed and PDF generated. Ready for manual submission to SEBI SCORES.",
    )


@router.get("/{case_id}/pdf")
async def download_complaint_pdf(
    case_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Download the generated complaint PDF."""
    result = await db.execute(select(Complaint).where(Complaint.case_id == case_id))
    complaint = result.scalar_one_or_none()

    if not complaint or not complaint.pdf_path:
        raise HTTPException(status_code=404, detail="Complaint PDF not found. Generate and confirm first.")

    try:
        pdf_data = object_storage.download_by_key(complaint.pdf_path)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to retrieve PDF from storage")

    import io
    return StreamingResponse(
        io.BytesIO(pdf_data),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=complaint_{case_id}.pdf"},
    )
