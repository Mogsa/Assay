"""add question_passes table

Revision ID: b4a2c1e7f390
Revises: 0da39e524442
Create Date: 2026-03-15
"""

from alembic import op
import sqlalchemy as sa

revision: str = "b4a2c1e7f390"
down_revision: str = "0da39e524442"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "question_passes",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("agent_id", sa.Uuid(), nullable=False),
        sa.Column("question_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["agent_id"], ["agents.id"]),
        sa.ForeignKeyConstraint(["question_id"], ["questions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("agent_id", "question_id", name="uq_question_passes_agent_question"),
    )


def downgrade() -> None:
    op.drop_table("question_passes")
