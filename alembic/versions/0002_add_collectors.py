"""add collector tracking and event source metadata

Revision ID: 0002_add_collectors
Revises: 0001_initial
Create Date: 2025-01-02 00:00:00.000000
"""

import sqlalchemy as sa

from alembic import op

revision = "0002_add_collectors"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("events") as batch:
        batch.add_column(sa.Column("source", sa.String(length=100), nullable=True))
        batch.add_column(sa.Column("external_id", sa.String(length=255), nullable=True))
        batch.add_column(sa.Column("source_url", sa.String(length=500), nullable=True))

    op.execute("UPDATE events SET source = 'legacy' WHERE source IS NULL")
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute(
            "UPDATE events SET external_id = 'legacy-' || id::text "
            "WHERE external_id IS NULL"
        )
    else:
        op.execute(
            "UPDATE events SET external_id = 'legacy-' || id WHERE external_id IS NULL"
        )

    with op.batch_alter_table("events") as batch:
        batch.alter_column("source", nullable=False)
        batch.alter_column("external_id", nullable=False)
        batch.create_unique_constraint(
            "uq_events_source_external_id", ["source", "external_id"]
        )

    op.create_table(
        "collector_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source", sa.String(length=100), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("items_fetched", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("items_upserted", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.String(length=500), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("collector_runs")
    with op.batch_alter_table("events") as batch:
        batch.drop_constraint("uq_events_source_external_id", type_="unique")
        batch.drop_column("source_url")
        batch.drop_column("external_id")
        batch.drop_column("source")
