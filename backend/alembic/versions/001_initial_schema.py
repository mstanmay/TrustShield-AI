"""Initial schema — Case, Verdict, Complaint, User, AlertSubscription, SEBICircular, KnownScamPattern.

Revision ID: 001
Create Date: 2024-01-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("username", sa.String(50), unique=True, nullable=False),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "cases",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("case_id", sa.String(36), unique=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("input_type", sa.String(50), nullable=False),
        sa.Column("original_filename", sa.String(500)),
        sa.Column("artifact_path", sa.String(1000)),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("source_ip", sa.String(45)),
        sa.Column("geo_region", sa.String(100)),
        sa.Column("deepfake_result", postgresql.JSONB),
        sa.Column("voice_result", postgresql.JSONB),
        sa.Column("document_result", postgresql.JSONB),
        sa.Column("phishing_result", postgresql.JSONB),
        sa.Column("risk_assessment_result", postgresql.JSONB),
        sa.Column("execution_trace", postgresql.JSONB),
        sa.Column("applicable_agents", postgresql.JSONB),
        sa.Column("error_message", sa.Text),
        sa.Column("uploaded_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("processing_started_at", sa.DateTime),
        sa.Column("completed_at", sa.DateTime),
    )
    op.create_index("idx_cases_status", "cases", ["status"])
    op.create_index("idx_cases_input_type", "cases", ["input_type"])
    op.create_index("idx_cases_uploaded_at", "cases", ["uploaded_at"])
    op.create_index("idx_cases_case_id", "cases", ["case_id"])

    op.create_table(
        "verdicts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("case_id", sa.String(36), sa.ForeignKey("cases.case_id"), unique=True, nullable=False),
        sa.Column("classification", sa.String(20), nullable=False),
        sa.Column("risk_score", sa.Float, nullable=False),
        sa.Column("threat_severity", sa.String(20), nullable=False),
        sa.Column("explanation", sa.Text),
        sa.Column("evidence_breakdown", postgresql.JSONB),
        sa.Column("reasoning_chain", postgresql.JSONB),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index("idx_verdicts_classification", "verdicts", ["classification"])
    op.create_index("idx_verdicts_risk_score", "verdicts", ["risk_score"])

    op.create_table(
        "complaints",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("case_id", sa.String(36), sa.ForeignKey("cases.case_id"), unique=True, nullable=False),
        sa.Column("status", sa.String(30), nullable=False, server_default="DRAFT_READY"),
        sa.Column("complainant_name", sa.String(255)),
        sa.Column("subject", sa.String(500)),
        sa.Column("complaint_body", sa.Text),
        sa.Column("evidence_summary", postgresql.JSONB),
        sa.Column("involved_urls", postgresql.JSONB),
        sa.Column("involved_domains", postgresql.JSONB),
        sa.Column("involved_phone_numbers", postgresql.JSONB),
        sa.Column("verdict_summary", sa.Text),
        sa.Column("pdf_path", sa.String(1000)),
        sa.Column("draft_json", postgresql.JSONB),
        sa.Column("generated_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("confirmed_at", sa.DateTime),
    )

    op.create_table(
        "alert_subscriptions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("subscription_type", sa.String(20), nullable=False),
        sa.Column("webhook_url", sa.String(1000)),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "sebi_circulars",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("circular_number", sa.String(100), unique=True, nullable=False),
        sa.Column("title", sa.String(500)),
        sa.Column("issued_date", sa.DateTime),
        sa.Column("content_text", sa.Text),
        sa.Column("signatory", sa.String(255)),
        sa.Column("department", sa.String(255)),
        sa.Column("content_hash", sa.String(64)),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "known_scam_patterns",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("pattern_type", sa.String(50), nullable=False),
        sa.Column("pattern_value", sa.Text, nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("severity", sa.String(20), server_default="medium"),
        sa.Column("reported_count", sa.Integer, server_default="1"),
        sa.Column("first_seen", sa.DateTime, server_default=sa.func.now()),
        sa.Column("last_seen", sa.DateTime, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("known_scam_patterns")
    op.drop_table("sebi_circulars")
    op.drop_table("alert_subscriptions")
    op.drop_table("complaints")
    op.drop_table("verdicts")
    op.drop_table("cases")
    op.drop_table("users")
    op.execute("DROP EXTENSION IF EXISTS vector")
