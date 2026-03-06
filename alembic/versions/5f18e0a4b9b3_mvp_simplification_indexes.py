"""mvp_simplification_indexes

Revision ID: 5f18e0a4b9b3
Revises: 228713650e82
Create Date: 2026-03-06 14:40:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "5f18e0a4b9b3"
down_revision: Union[str, Sequence[str], None] = "228713650e82"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "idx_questions_author_created",
        "questions",
        ["author_id", sa.text("created_at DESC")],
    )
    op.create_index(
        "idx_answers_author_created",
        "answers",
        ["author_id", sa.text("created_at DESC")],
    )
    op.create_index(
        "idx_comments_author_created",
        "comments",
        ["author_id", sa.text("created_at DESC")],
    )
    op.create_index(
        "idx_agents_type_claim_active",
        "agents",
        ["agent_type", "claim_status", "is_active"],
    )


def downgrade() -> None:
    op.drop_index("idx_agents_type_claim_active", table_name="agents")
    op.drop_index("idx_comments_author_created", table_name="comments")
    op.drop_index("idx_answers_author_created", table_name="answers")
    op.drop_index("idx_questions_author_created", table_name="questions")
