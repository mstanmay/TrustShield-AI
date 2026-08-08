"""
Analysis Task — Celery task that runs the full LangGraph pipeline for a case.
Fetches the case from DB, downloads the artifact, runs the pipeline, and persists results.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


def _run_async(coro):
    """Helper to run async code from sync Celery task context."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                return pool.submit(asyncio.run, coro).result()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


@celery_app.task(bind=True, name="run_analysis", max_retries=2)
def run_analysis(self, case_id: str) -> dict:
    """Run the full fraud detection pipeline for a case.

    1. Load case from database
    2. Download artifact from object storage (if applicable)
    3. Execute LangGraph pipeline
    4. Persist all results back to database

    Args:
        case_id: The case identifier to process.

    Returns:
        Dict with case_id, status, and classification.
    """
    logger.info("Starting analysis for case %s", case_id)

    try:
        result = _run_async(_run_analysis_async(case_id))
        return result
    except Exception as exc:
        logger.error("Analysis failed for case %s: %s", case_id, exc)
        # Update case status to FAILED
        _run_async(_update_case_status(case_id, "failed", str(exc)))
        raise self.retry(exc=exc, countdown=30)


async def _run_analysis_async(case_id: str) -> dict:
    """Async implementation of the analysis pipeline."""
    from sqlalchemy import select, update

    from app.core.database import AsyncSessionLocal
    from app.models.database import Case, Verdict
    from app.orchestrator.graph import run_pipeline

    # 1. Load case from database
    async with AsyncSessionLocal() as session:
        stmt = select(Case).where(Case.case_id == case_id)
        result = await session.execute(stmt)
        case = result.scalar_one_or_none()

        if not case:
            raise ValueError(f"Case {case_id} not found")

        # Update status to PROCESSING
        case.status = "processing"
        case.processing_started_at = datetime.utcnow()
        await session.commit()

        # Build initial state for the pipeline
        initial_state = {
            "case_id": case.case_id,
            "input_type": case.input_type,
            "artifact_path": case.artifact_path or "",
            "original_filename": case.original_filename or "",
            "metadata": {
                "source_ip": case.source_ip,
                "geo_region": case.geo_region,
            },
        }

    # 2. Download artifact to temp location if needed
    artifact_local_path = ""
    if initial_state["artifact_path"]:
        try:
            import tempfile
            from pathlib import Path
            from app.core.storage import object_storage

            data = object_storage.download_by_key(initial_state["artifact_path"])
            suffix = Path(initial_state["original_filename"]).suffix if initial_state["original_filename"] else ""
            tmp = tempfile.NamedTemporaryFile(suffix=suffix, delete=False)
            tmp.write(data)
            tmp.close()
            artifact_local_path = tmp.name
            initial_state["artifact_path"] = artifact_local_path
        except Exception as e:
            logger.warning("Failed to download artifact: %s", e)

    # 3. Run the LangGraph pipeline
    final_state = await run_pipeline(initial_state)

    # 4. Persist results back to database
    async with AsyncSessionLocal() as session:
        stmt = select(Case).where(Case.case_id == case_id)
        result = await session.execute(stmt)
        case = result.scalar_one_or_none()

        if case:
            case.status = final_state.get("status", "completed")
            case.deepfake_result = final_state.get("deepfake_result")
            case.voice_result = final_state.get("voice_result")
            case.document_result = final_state.get("document_result")
            case.phishing_result = final_state.get("phishing_result")
            case.risk_assessment_result = final_state.get("risk_assessment")
            case.execution_trace = final_state.get("execution_trace")
            case.applicable_agents = final_state.get("applicable_agents")
            case.error_message = final_state.get("error_message")
            case.completed_at = datetime.utcnow()

            # Create verdict record
            verdict_data = final_state.get("final_verdict")
            if verdict_data:
                verdict = Verdict(
                    case_id=case_id,
                    classification=verdict_data.get("classification", "Genuine"),
                    risk_score=verdict_data.get("risk_score", 0.0),
                    threat_severity=verdict_data.get("threat_severity", "Low"),
                    explanation=verdict_data.get("explanation", ""),
                    evidence_breakdown=verdict_data.get("evidence_breakdown"),
                    reasoning_chain=verdict_data.get("reasoning_chain"),
                )
                session.add(verdict)

            await session.commit()

    # Clean up temp file
    if artifact_local_path:
        from pathlib import Path
        Path(artifact_local_path).unlink(missing_ok=True)

    logger.info("Analysis completed for case %s: %s", case_id, final_state.get("status"))

    return {
        "case_id": case_id,
        "status": final_state.get("status", "completed"),
        "classification": final_state.get("final_verdict", {}).get("classification"),
        "risk_score": final_state.get("final_verdict", {}).get("risk_score"),
    }


async def _update_case_status(case_id: str, status: str, error: str = "") -> None:
    """Update a case's status in the database."""
    from sqlalchemy import update
    from app.core.database import AsyncSessionLocal
    from app.models.database import Case

    try:
        async with AsyncSessionLocal() as session:
            stmt = (
                update(Case)
                .where(Case.case_id == case_id)
                .values(status=status, error_message=error)
            )
            await session.execute(stmt)
            await session.commit()
    except Exception as e:
        logger.error("Failed to update case %s status: %s", case_id, e)
