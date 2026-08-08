"""
Alerts API — Browser protection alerts + WebSocket push + webhook registration.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.models.database import AlertSubscription, Case, Verdict
from app.models.enums import ThreatSeverity
from app.models.schemas import AlertItem, AlertsResponse

router = APIRouter(prefix="/api/v1/dashboard", tags=["alerts"])

# In-memory WebSocket connections (for demo; use Redis pub/sub in production)
_ws_connections: list[WebSocket] = []


@router.get("/alerts", response_model=AlertsResponse)
async def get_alerts(
    severity: str | None = Query(None, description="Filter by severity"),
    hours: int = Query(24, description="Lookback window in hours"),
    limit: int = Query(50),
    db: AsyncSession = Depends(get_db_session),
):
    """Get recent browser protection alerts for fraudulent/suspicious cases."""
    cutoff = datetime.utcnow() - timedelta(hours=hours)

    query = (
        select(Case, Verdict)
        .join(Verdict, Case.case_id == Verdict.case_id)
        .where(
            Case.completed_at >= cutoff,
            Verdict.classification.in_(["Fraudulent", "Suspicious"]),
        )
        .order_by(Case.completed_at.desc())
        .limit(limit)
    )

    if severity:
        query = query.where(Verdict.threat_severity == severity)

    result = await db.execute(query)
    rows = result.all()

    alerts = []
    for case, verdict in rows:
        # Extract URLs from phishing results
        urls = []
        if case.phishing_result and isinstance(case.phishing_result, dict):
            urls = case.phishing_result.get("analyzed_urls", [])[:5]

        alert_type = "fraud_detected" if verdict.classification == "Fraudulent" else "suspicious_activity"

        alerts.append(AlertItem(
            alert_id=str(uuid.uuid4()),
            case_id=case.case_id,
            alert_type=alert_type,
            severity=ThreatSeverity(verdict.threat_severity),
            message=f"{verdict.classification}: {verdict.explanation[:200]}" if verdict.explanation else verdict.classification,
            created_at=case.completed_at or case.uploaded_at,
            urls=urls,
        ))

    return AlertsResponse(alerts=alerts, total=len(alerts))


@router.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    """WebSocket endpoint for real-time alert push to browser extensions."""
    await websocket.accept()
    _ws_connections.append(websocket)

    try:
        while True:
            # Keep connection alive, receive any messages from client
            data = await websocket.receive_text()
            # Client can send "ping" to keep alive
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        _ws_connections.remove(websocket)


@router.post("/alerts/webhook")
async def register_webhook(
    webhook_url: str,
    user_id: str | None = None,
    db: AsyncSession = Depends(get_db_session),
):
    """Register a webhook URL for alert notifications."""
    subscription = AlertSubscription(
        subscription_type="webhook",
        webhook_url=webhook_url,
        user_id=uuid.UUID(user_id) if user_id else None,
    )
    db.add(subscription)
    await db.flush()

    return {"status": "registered", "subscription_id": str(subscription.id)}


async def broadcast_alert(alert: AlertItem) -> None:
    """Broadcast an alert to all connected WebSocket clients.
    Called internally when a new fraudulent case is detected."""
    message = alert.model_dump_json()
    disconnected = []

    for ws in _ws_connections:
        try:
            await ws.send_text(message)
        except Exception:
            disconnected.append(ws)

    for ws in disconnected:
        _ws_connections.remove(ws)
