"""phase2_phase3_schema_backfill

Revision ID: 4b4f6d22c7aa
Revises: d21dfc8d96c0
Create Date: 2026-04-07 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4b4f6d22c7aa"
down_revision: Union[str, Sequence[str], None] = "d21dfc8d96c0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "agents",
        sa.Column("trust_score", sa.Float(), nullable=False, server_default="1.0"),
    )
    op.add_column(
        "questions",
        sa.Column("disagreement_score", sa.Float(), nullable=False, server_default="0.0"),
    )
    op.add_column(
        "answers",
        sa.Column("is_synthesis", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.add_column(
        "answers",
        sa.Column("superseded", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    op.create_table(
        "activity_log",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("actor_id", sa.Uuid(), nullable=False),
        sa.Column("action", sa.String(length=32), nullable=False),
        sa.Column("target_type", sa.String(length=16), nullable=False),
        sa.Column("target_id", sa.Uuid(), nullable=False),
        sa.Column("summary", sa.String(length=200), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["actor_id"], ["agents.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_activity_log_created_at_desc", "activity_log", [sa.text("created_at DESC")])


def downgrade() -> None:
    op.drop_index("ix_activity_log_created_at_desc", table_name="activity_log")
    op.drop_table("activity_log")
    op.drop_column("answers", "superseded")
    op.drop_column("answers", "is_synthesis")
    op.drop_column("questions", "disagreement_score")
    op.drop_column("agents", "trust_score")
