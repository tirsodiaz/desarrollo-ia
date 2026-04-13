"""initial schema

Revision ID: 20260320_000001
Revises:
Create Date: 2026-03-20 00:00:01
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20260320_000001"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "processing_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("correlation_id", sa.String(length=64), nullable=False),
        sa.Column("case_id", sa.String(length=128), nullable=False),
        sa.Column("source_file", sa.String(length=512), nullable=False),
        sa.Column("detected_at", sa.DateTime(), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("action", sa.String(length=64), nullable=True),
        sa.Column("output_file", sa.String(length=512), nullable=True),
        sa.Column("error_details", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("correlation_id"),
    )
    op.create_index(
        op.f("ix_processing_records_case_id"),
        "processing_records",
        ["case_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_processing_records_correlation_id"),
        "processing_records",
        ["correlation_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_processing_records_correlation_id"), table_name="processing_records")
    op.drop_index(op.f("ix_processing_records_case_id"), table_name="processing_records")
    op.drop_table("processing_records")
