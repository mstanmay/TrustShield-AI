"""
Cases API — GET /api/v1/cases/{case_id}
Full case details including all agent results and verdict.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.models.database import Case, Verdict
from app.models.enums import CaseStatus, InputType
from app.models.schemas import CaseResponse

router = APIRouter(prefix="/api/v1", tags=["cases"])


@router.get("/cases/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: str,
    db: AsyncSession = Depends(get_db_session),
):
    """Get full case details including all agent results and final verdict."""
    result = await db.execute(select(Case).where(Case.case_id == case_id))
    case = result.scalar_one_or_none()

    if not case:
        raise HTTPException(status_code=404, detail=f"Case {case_id} not found")

    # Build verdict data
    verdict_data = None
    if case.verdict:
        verdict_data = {
            "classification": case.verdict.classification,
            "risk_score": case.verdict.risk_score,
            "threat_severity": case.verdict.threat_severity,
            "explanation": case.verdict.explanation,
            "evidence_breakdown": case.verdict.evidence_breakdown or {},
            "reasoning_chain": case.verdict.reasoning_chain or [],
        }

    return CaseResponse(
        case_id=case.case_id,
        input_type=InputType(case.input_type),
        status=CaseStatus(case.status),
        uploaded_at=case.uploaded_at,
        deepfake_result=case.deepfake_result,
        voice_result=case.voice_result,
        document_result=case.document_result,
        phishing_result=case.phishing_result,
        risk_assessment=case.risk_assessment_result,
        final_verdict=verdict_data,
        execution_trace=case.execution_trace or [],
    )


@router.get("/cases", response_model=list[CaseResponse])
async def list_cases(
    status: str | None = None,
    input_type: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db_session),
):
    """List cases with optional filtering."""
    query = select(Case).order_by(Case.uploaded_at.desc()).limit(limit).offset(offset)

    if status:
        query = query.where(Case.status == status)
    if input_type:
        query = query.where(Case.input_type == input_type)

    result = await db.execute(query)
    cases = result.scalars().all()

    return [
        CaseResponse(
            case_id=c.case_id,
            input_type=InputType(c.input_type),
            status=CaseStatus(c.status),
            uploaded_at=c.uploaded_at,
            deepfake_result=c.deepfake_result,
            voice_result=c.voice_result,
            document_result=c.document_result,
            phishing_result=c.phishing_result,
            risk_assessment=c.risk_assessment_result,
            final_verdict={
                "classification": c.verdict.classification,
                "risk_score": c.verdict.risk_score,
                "threat_severity": c.verdict.threat_severity,
                "explanation": c.verdict.explanation,
                "evidence_breakdown": c.verdict.evidence_breakdown or {},
                "reasoning_chain": c.verdict.reasoning_chain or [],
            } if c.verdict else None,
            execution_trace=c.execution_trace or [],
        )
        for c in cases
    ]
