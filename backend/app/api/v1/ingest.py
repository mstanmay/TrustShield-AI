"""
Ingestion API (STEP 1) — POST /api/v1/ingest

Accepts multipart file uploads or URL/text submissions.
Validates input via magic bytes, runs malware scan hook, stores artifact in S3,
creates a Case record in Postgres, and dispatches a Celery analysis task.
Returns case_id immediately; processing is async.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.malware_scanner import get_malware_scanner
from app.core.database import get_db_session
from app.core.file_detection import detect_input_type, is_likely_qr_code
from app.core.storage import object_storage
from app.models.database import Case
from app.models.enums import CaseStatus, InputType
from app.models.schemas import IngestRequest, IngestResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["ingestion"])


@router.post("/ingest", response_model=IngestResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest(
    file: UploadFile | None = File(None),
    url: str | None = Form(None),
    text_content: str | None = Form(None),
    input_type_hint: str | None = Form(None),
    db: AsyncSession = Depends(get_db_session),
):
    """Ingest a file, URL, or text for fraud analysis.

    Accepts:
    - File upload (video, image, audio, PDF, .eml, QR code image)
    - URL submission
    - Text content (WhatsApp/Telegram message paste, email body)

    Returns case_id immediately; processing is async via Celery.
    """
    case_id = str(uuid.uuid4())
    artifact_path = ""
    original_filename = ""
    detected_type: InputType | None = None
    metadata: dict = {}

    if file:
        # ── File Upload Path ─────────────────────────────────────────
        file_data = await file.read()
        original_filename = file.filename or "unknown"

        if not file_data:
            raise HTTPException(status_code=400, detail="Empty file uploaded")

        # 1. Magic-bytes type detection
        detected_type = detect_input_type(
            data=file_data,
            filename=original_filename,
            content_type=file.content_type,
        )

        if not detected_type:
            # Try input_type_hint
            if input_type_hint:
                try:
                    detected_type = InputType(input_type_hint)
                except ValueError:
                    raise HTTPException(status_code=400, detail=f"Unknown input type: {input_type_hint}")
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Could not detect file type. Please provide input_type_hint.",
                )

        # Check if image might contain QR code
        if detected_type == InputType.IMAGE and is_likely_qr_code(file_data):
            metadata["may_contain_qr"] = True
            if input_type_hint == "qr_code":
                detected_type = InputType.QR_CODE

        # 2. Malware scan hook
        scanner = get_malware_scanner()
        scan_result = await scanner.scan(file_data, original_filename)
        if not scan_result.is_clean:
            raise HTTPException(
                status_code=400,
                detail=f"File flagged by malware scanner: {scan_result.threat_name}",
            )

        # 3. Upload to object storage
        try:
            artifact_path = object_storage.upload_artifact(
                case_id=case_id,
                filename=original_filename,
                file_data=file_data,
                content_type=file.content_type or "application/octet-stream",
            )
        except Exception as e:
            logger.error("Failed to upload artifact: %s", e)
            raise HTTPException(status_code=500, detail="Failed to store artifact")

    elif url:
        # ── URL Submission Path ──────────────────────────────────────
        detected_type = InputType.URL
        metadata["url"] = url

    elif text_content:
        # ── Text Content Path (WhatsApp/Telegram/Email body) ─────────
        if input_type_hint:
            try:
                detected_type = InputType(input_type_hint)
            except ValueError:
                detected_type = InputType.WHATSAPP_MESSAGE
        else:
            detected_type = InputType.WHATSAPP_MESSAGE

        metadata["text_content"] = text_content

    else:
        raise HTTPException(
            status_code=400,
            detail="Must provide file, url, or text_content",
        )

    # 4. Create Case record in database
    case = Case(
        case_id=case_id,
        input_type=detected_type.value,
        original_filename=original_filename,
        artifact_path=artifact_path,
        status=CaseStatus.PENDING.value,
        uploaded_at=datetime.utcnow(),
    )
    db.add(case)
    await db.flush()

    # 5. Publish CaseUploadedEvent to RabbitMQ Event Bus & Celery Queue
    try:
        from app.events.publisher import EventPublisher
        from app.events.schemas import CaseUploadedEvent
        
        publisher = EventPublisher()
        event = CaseUploadedEvent(
            event_id=f"evt-{uuid.uuid4().hex[:12]}",
            event_type="case.uploaded",
            correlation_id=case_id,
            case_id=case_id,
            input_type=detected_type.value,
            artifact_path=artifact_path,
            original_filename=original_filename,
            metadata=metadata,
        )
        await publisher.publish_case_uploaded(event)

        from app.tasks.analysis_task import run_analysis
        run_analysis.delay(case_id)
        logger.info("Dispatched RabbitMQ event & Celery analysis task for case %s (type: %s)", case_id, detected_type.value)
    except Exception as e:
        logger.error("Failed to dispatch event / Celery task: %s", e)
        case.status = CaseStatus.FAILED.value
        case.error_message = f"Event publish / task dispatch failed: {e}"

    return IngestResponse(
        case_id=case_id,
        status=CaseStatus.PENDING,
        message=f"Case created and queued for analysis (input type: {detected_type.value})",
    )
