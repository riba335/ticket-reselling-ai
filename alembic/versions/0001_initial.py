"""initial

Revision ID: 0001_initial
Revises:
Create Date: 2025-01-01 00:00:00.000000
"""
import sqlalchemy as sa

from alembic import op

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("venue", sa.String(length=255), nullable=False),
        sa.Column("event_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "listings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("event_id", sa.Integer(), sa.ForeignKey("events.id"), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_table(
        "price_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "listing_id", sa.Integer(), sa.ForeignKey("listings.id"), nullable=False
        ),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("snapped_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("price_snapshots")
    op.drop_table("listings")
    op.drop_table("events")
