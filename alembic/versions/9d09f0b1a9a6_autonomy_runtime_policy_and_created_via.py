"""autonomy_runtime_policy_and_created_via

Revision ID: 9d09f0b1a9a6
Revises: 5f18e0a4b9b3
Create Date: 2026-03-06 12:20:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9d09f0b1a9a6"
down_revision: Union[str, None] = "5f18e0a4b9b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "questions",
        sa.Column("created_via", sa.String(length=16), nullable=False, server_default="manual"),
    )
    op.add_column(
        "answers",
        sa.Column("created_via", sa.String(length=16), nullable=False, server_default="manual"),
    )
    op.add_column(
        "comments",
        sa.Column("created_via", sa.String(length=16), nullable=False, server_default="manual"),
    )

    op.create_table(
        "agent_runtime_policies",
        sa.Column("agent_id", sa.Uuid(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("dry_run", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("max_actions_per_hour", sa.Integer(), nullable=False, server_default="6"),
        sa.Column("max_questions_per_day", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_answers_per_hour", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("max_reviews_per_hour", sa.Integer(), nullable=False, server_default="6"),
        sa.Column("allow_question_asking", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("allow_reposts", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "allowed_community_ids",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'::json"),
        ),
        sa.Column("global_only", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.ForeignKeyConstraint(["agent_id"], ["agents.id"]),
        sa.PrimaryKeyConstraint("agent_id"),
    )


def downgrade() -> None:
    op.drop_table("agent_runtime_policies")
    op.drop_column("comments", "created_via")
    op.drop_column("answers", "created_via")
    op.drop_column("questions", "created_via")
