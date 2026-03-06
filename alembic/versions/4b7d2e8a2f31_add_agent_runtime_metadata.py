"""add agent runtime metadata

Revision ID: 4b7d2e8a2f31
Revises: 8d95f1e1fbb7
Create Date: 2026-03-06 18:10:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision = "4b7d2e8a2f31"
down_revision = "8d95f1e1fbb7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("agents")}

    if "claim_token_hash" not in columns:
        op.add_column("agents", sa.Column("claim_token_hash", sa.String(length=64), nullable=True))
    if "claim_token_expires_at" not in columns:
        op.add_column("agents", sa.Column("claim_token_expires_at", sa.DateTime(timezone=True), nullable=True))
    if "claim_status" not in columns:
        op.add_column(
            "agents",
            sa.Column("claim_status", sa.String(length=16), nullable=False, server_default="claimed"),
        )
        op.execute(
            """
            UPDATE agents
            SET claim_status = CASE
              WHEN agent_type = 'human' OR owner_id IS NOT NULL THEN 'claimed'
              ELSE 'unclaimed'
            END
            """
        )
        op.alter_column("agents", "claim_status", server_default=None)

    if "description" not in columns:
        op.add_column("agents", sa.Column("description", sa.String(length=512), nullable=True))
    if "provider" not in columns:
        op.add_column("agents", sa.Column("provider", sa.String(length=64), nullable=True))
    if "model_name" not in columns:
        op.add_column("agents", sa.Column("model_name", sa.String(length=128), nullable=True))
    if "runtime_kind" not in columns:
        op.add_column("agents", sa.Column("runtime_kind", sa.String(length=64), nullable=True))

    op.execute(
        """
        UPDATE agents
        SET model_name = COALESCE(model_name, NULLIF(agent_type, '')),
            provider = COALESCE(provider, CASE WHEN agent_type = 'human' THEN NULL ELSE 'other' END),
            runtime_kind = COALESCE(runtime_kind, CASE WHEN agent_type = 'human' THEN NULL ELSE 'unknown' END)
        """
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("agents")}
    if "runtime_kind" in columns:
        op.drop_column("agents", "runtime_kind")
    if "model_name" in columns:
        op.drop_column("agents", "model_name")
    if "provider" in columns:
        op.drop_column("agents", "provider")
    if "description" in columns:
        op.drop_column("agents", "description")
    if "claim_status" in columns:
        op.drop_column("agents", "claim_status")
    if "claim_token_expires_at" in columns:
        op.drop_column("agents", "claim_token_expires_at")
    if "claim_token_hash" in columns:
        op.drop_column("agents", "claim_token_hash")
