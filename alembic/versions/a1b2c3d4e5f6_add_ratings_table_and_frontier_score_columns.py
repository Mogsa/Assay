"""add ratings table and frontier_score columns

Revision ID: a1b2c3d4e5f6
Revises: 0da39e524442
Create Date: 2026-03-19 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: str = "0da39e524442"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ratings",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("rater_id", sa.Uuid(), nullable=False),
        sa.Column("target_type", sa.String(length=16), nullable=False),
        sa.Column("target_id", sa.Uuid(), nullable=False),
        sa.Column("rigour", sa.SmallInteger(), nullable=False),
        sa.Column("novelty", sa.SmallInteger(), nullable=False),
        sa.Column("generativity", sa.SmallInteger(), nullable=False),
        sa.Column("reasoning", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("rater_id", "target_type", "target_id"),
    )
    op.create_index("idx_ratings_target", "ratings", ["target_type", "target_id"])
    op.create_index(op.f("ix_ratings_rater_id"), "ratings", ["rater_id"])

    op.add_column(
        "questions",
        sa.Column("frontier_score", sa.Float(), server_default="0.0", nullable=False),
    )
    op.add_column(
        "answers",
        sa.Column("frontier_score", sa.Float(), server_default="0.0", nullable=False),
    )


def downgrade() -> None:
    op.drop_column("answers", "frontier_score")
    op.drop_column("questions", "frontier_score")
    op.drop_index(op.f("ix_ratings_rater_id"), table_name="ratings")
    op.drop_index("idx_ratings_target", table_name="ratings")
    op.drop_table("ratings")
