"""initial schema

Revision ID: 001_initial
Revises:
Create Date: 2026-06-25
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    company_tier = sa.Enum("essential", "advanced", "elite", name="company_tier")
    user_role = sa.Enum("owner", "gm", "manager", "auditor", "admin", "appowner", name="user_role")
    task_type = sa.Enum("daily", "weekly", "monthly", "adhoc", name="task_type")
    task_status = sa.Enum("pending", "in_progress", "completed", "overdue", name="task_status")
    file_type = sa.Enum("excel", "csv", "word", "image", "pdf", "encrypted_json", name="file_type")
    doc_category = sa.Enum("invoice", "contract", "report", "receipt", "other", name="doc_category")
    doc_status = sa.Enum("pending", "ocr_processing", "certified", name="doc_status")
    ocr_status = sa.Enum("not_started", "running", "done", "failed", name="ocr_status")
    ledger_action = sa.Enum("insert", "update", "delete", "reverse", name="ledger_action")
    analytics_output_type = sa.Enum("trust_index", "forecast", "summary", "other", name="analytics_output_type")
    waste_category = sa.Enum("financial", "operational", "human", "opportunity", name="waste_category")
    risk_severity = sa.Enum("low", "medium", "high", "critical", name="risk_severity")

    for e in [company_tier, user_role, task_type, task_status, file_type, doc_category,
              doc_status, ocr_status, ledger_action, analytics_output_type,
              waste_category, risk_severity]:
        e.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "companies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("sector", sa.String(120), nullable=False),
        sa.Column("tier", company_tier, nullable=False, server_default="essential"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "branches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("location", sa.String(255)),
    )

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("role", user_role, nullable=False),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("branches.id", ondelete="SET NULL")),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "audit_tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("auditor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("task_type", task_type, nullable=False),
        sa.Column("status", task_status, nullable=False, server_default="pending"),
        sa.Column("sla_deadline", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("demerit_points", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("file_path", sa.String(1024), nullable=False),
        sa.Column("original_filename", sa.String(512), nullable=False),
        sa.Column("file_type", file_type, nullable=False),
        sa.Column("doc_category", doc_category, nullable=False, server_default="other"),
        sa.Column("status", doc_status, nullable=False, server_default="pending"),
        sa.Column("uploaded_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("branches.id", ondelete="SET NULL")),
        sa.Column("ocr_status", ocr_status, nullable=False, server_default="not_started"),
        sa.Column("confidence_score", sa.Float),
        sa.Column("extracted_data", postgresql.JSONB),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "document_certifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("auditor_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("certified_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("corrections_made", postgresql.JSONB),
        sa.Column("is_valid", sa.Boolean, nullable=False, server_default=sa.text("true")),
    )

    op.create_table(
        "audit_ledger",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("table_name", sa.String(120), nullable=False),
        sa.Column("record_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action", ledger_action, nullable=False),
        sa.Column("old_value", postgresql.JSONB),
        sa.Column("new_value", postgresql.JSONB),
        sa.Column("reason", sa.Text),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("previous_hash", sa.Text),
        sa.Column("current_hash", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "analytics_outputs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("output_type", analytics_output_type, nullable=False),
        sa.Column("data", postgresql.JSONB, nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("generated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("trust_index", sa.Integer),
    )

    op.create_table(
        "waste_map_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category", waste_category, nullable=False),
        sa.Column("amount_iqd", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("department", sa.String(255)),
        sa.Column("description", sa.Text),
        sa.Column("status", sa.String(64), nullable=False, server_default="open"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "risk_alerts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("severity", risk_severity, nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("financial_impact", sa.Numeric(18, 2), nullable=False, server_default="0"),
        sa.Column("status", sa.String(64), nullable=False, server_default="open"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )


def downgrade():
    for t in ["risk_alerts", "waste_map_items", "analytics_outputs", "audit_ledger",
              "document_certifications", "documents", "audit_tasks", "users",
              "branches", "companies"]:
        op.drop_table(t)
    for n in ["risk_severity", "waste_category", "analytics_output_type", "ledger_action",
              "ocr_status", "doc_status", "doc_category", "file_type",
              "task_status", "task_type", "user_role", "company_tier"]:
        op.execute(f"DROP TYPE IF EXISTS {n}")