"""
Dashboard APIs (STEP 5) — Threat Intelligence, Heatmap, and Emerging Trends endpoints.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.models.database import Case, Verdict
from app.models.schemas import (
    HeatmapDataPoint,
    HeatmapResponse,
    ThreatIntelResponse,
    TrendCluster,
    TrendsResponse,
)

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


@router.get("/threat-intel", response_model=ThreatIntelResponse)
async def get_threat_intel(
    days: int = Query(30, description="Number of days to aggregate"),
    db: AsyncSession = Depends(get_db_session),
):
    """Aggregated threat intelligence statistics."""
    cutoff = datetime.utcnow() - timedelta(days=days)

    # Total cases
    total_result = await db.execute(
        select(func.count(Case.id)).where(Case.uploaded_at >= cutoff)
    )
    total_cases = total_result.scalar() or 0

    # Classification counts
    classification_query = (
        select(Verdict.classification, func.count(Verdict.id))
        .join(Case, Case.case_id == Verdict.case_id)
        .where(Case.uploaded_at >= cutoff)
        .group_by(Verdict.classification)
    )
    classification_result = await db.execute(classification_query)
    counts = dict(classification_result.all())

    fraudulent_count = counts.get("Fraudulent", 0)
    suspicious_count = counts.get("Suspicious", 0)
    genuine_count = counts.get("Genuine", 0)

    # Average risk score
    avg_query = (
        select(func.avg(Verdict.risk_score))
        .join(Case, Case.case_id == Verdict.case_id)
        .where(Case.uploaded_at >= cutoff)
    )
    avg_result = await db.execute(avg_query)
    avg_risk_score = float(avg_result.scalar() or 0)

    # Top threat types (by input type)
    threat_types_query = (
        select(Case.input_type, func.count(Case.id))
        .join(Verdict, Case.case_id == Verdict.case_id)
        .where(
            Case.uploaded_at >= cutoff,
            Verdict.classification.in_(["Fraudulent", "Suspicious"]),
        )
        .group_by(Case.input_type)
        .order_by(func.count(Case.id).desc())
        .limit(5)
    )
    threat_types_result = await db.execute(threat_types_query)
    top_threat_types = [
        {"input_type": row[0], "count": row[1]}
        for row in threat_types_result.all()
    ]

    # Recent cases
    recent_query = (
        select(Case)
        .where(Case.uploaded_at >= cutoff, Case.status == "completed")
        .order_by(Case.uploaded_at.desc())
        .limit(10)
    )
    recent_result = await db.execute(recent_query)
    recent_cases = [
        {
            "case_id": c.case_id,
            "input_type": c.input_type,
            "status": c.status,
            "uploaded_at": c.uploaded_at.isoformat() if c.uploaded_at else None,
        }
        for c in recent_result.scalars().all()
    ]

    return ThreatIntelResponse(
        total_cases=total_cases,
        fraudulent_count=fraudulent_count,
        suspicious_count=suspicious_count,
        genuine_count=genuine_count,
        avg_risk_score=avg_risk_score,
        top_threat_types=top_threat_types,
        recent_cases=recent_cases,
    )


@router.get("/heatmap", response_model=HeatmapResponse)
async def get_heatmap(
    days: int = Query(30, description="Number of days to aggregate"),
    db: AsyncSession = Depends(get_db_session),
):
    """Geo/time aggregation of fraud cases for heatmap visualization."""
    cutoff = datetime.utcnow() - timedelta(days=days)

    # Group by geo_region and time bucket (day)
    heatmap_query = (
        select(
            Case.geo_region,
            func.date_trunc("day", Case.uploaded_at).label("time_bucket"),
            func.count(Case.id).label("case_count"),
            func.avg(Verdict.risk_score).label("avg_severity"),
        )
        .outerjoin(Verdict, Case.case_id == Verdict.case_id)
        .where(Case.uploaded_at >= cutoff)
        .group_by(Case.geo_region, func.date_trunc("day", Case.uploaded_at))
        .order_by(func.date_trunc("day", Case.uploaded_at).desc())
    )

    result = await db.execute(heatmap_query)
    rows = result.all()

    data_points = []
    regions = set()
    for row in rows:
        region = row[0] or "Unknown"
        regions.add(region)
        data_points.append(HeatmapDataPoint(
            region=region,
            count=row[2],
            avg_severity=float(row[3] or 0),
            time_bucket=row[1].isoformat() if row[1] else "",
        ))

    return HeatmapResponse(
        data_points=data_points,
        total_regions=len(regions),
    )


@router.get("/trends", response_model=TrendsResponse)
async def get_trends(
    days: int = Query(30, description="Analysis period in days"),
    db: AsyncSession = Depends(get_db_session),
):
    """Emerging scam trends — clusters of similar fraudulent cases.

    # TODO: upgrade to trained model — implement embedding-based clustering.
    Current implementation uses simple input_type + severity grouping.
    """
    cutoff = datetime.utcnow() - timedelta(days=days)

    # Fetch recent fraudulent/suspicious cases
    query = (
        select(Case, Verdict)
        .join(Verdict, Case.case_id == Verdict.case_id)
        .where(
            Case.uploaded_at >= cutoff,
            Verdict.classification.in_(["Fraudulent", "Suspicious"]),
        )
        .order_by(Case.uploaded_at.desc())
        .limit(200)
    )
    result = await db.execute(query)
    rows = result.all()

    # Simple clustering by (input_type, threat_severity)
    clusters: dict[str, list] = {}
    for case, verdict in rows:
        cluster_key = f"{case.input_type}_{verdict.threat_severity}"
        if cluster_key not in clusters:
            clusters[cluster_key] = []
        clusters[cluster_key].append((case, verdict))

    trend_clusters = []
    for cluster_key, items in clusters.items():
        parts = cluster_key.split("_", 1)
        input_type = parts[0] if parts else "unknown"
        severity = parts[1] if len(parts) > 1 else "unknown"

        case_ids = [c.case_id for c, v in items]
        avg_risk = sum(v.risk_score for _, v in items) / len(items)

        # Extract common indicators from evidence
        common_indicators = []
        for case, _ in items[:5]:
            if case.phishing_result and isinstance(case.phishing_result, dict):
                for ev in case.phishing_result.get("evidence", [])[:2]:
                    if isinstance(ev, dict):
                        common_indicators.append(ev.get("finding", ""))

        trend_clusters.append(TrendCluster(
            cluster_id=cluster_key,
            label=f"{input_type.replace('_', ' ').title()} — {severity} Severity",
            case_count=len(items),
            avg_risk_score=avg_risk,
            representative_case_ids=case_ids[:5],
            common_indicators=list(set(common_indicators))[:5],
        ))

    # Sort by case count descending
    trend_clusters.sort(key=lambda x: x.case_count, reverse=True)

    return TrendsResponse(
        clusters=trend_clusters,
        analysis_period_days=days,
    )
