"""add doc categories

Revision ID: 003_add_doc_categories
Revises: 002_enable_rls
Create Date: 2026-06-25
"""
from alembic import op
import sqlalchemy as sa

revision = "003_add_doc_categories"
down_revision = "002_enable_rls"
branch_labels = None
depends_on = None


def upgrade():
    # ALTER TYPE ADD VALUE cannot be executed inside a transaction block in older postgres or without commit, 
    # but alembic runs in transaction by default. We can use op.get_bind().commit() or execute outside.
    # To be safe and compatible with all postgres versions in Alembic:
    connection = op.get_bind()
    if connection.dialect.name == 'postgresql':
        connection.commit()
        for category in ["bank_statement", "inventory_report", "encrypted_report"]:
            try:
                connection.execute(sa.text(f"ALTER TYPE doc_category ADD VALUE '{category}'"))
            except Exception:
                pass


def downgrade():
    pass
