"""add cascade deletes and question_id index to question_reads

Revision ID: d2aed9fc3f02
Revises: de440105dc45
Create Date: 2026-03-15 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'd2aed9fc3f02'
down_revision: Union[str, Sequence[str], None] = 'de440105dc45'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add CASCADE on both FKs and an index on question_id."""
    # Drop existing FKs and recreate with ondelete CASCADE
    op.drop_constraint('question_reads_agent_id_fkey', 'question_reads', type_='foreignkey')
    op.drop_constraint('question_reads_question_id_fkey', 'question_reads', type_='foreignkey')
    op.create_foreign_key(
        'question_reads_agent_id_fkey', 'question_reads',
        'agents', ['agent_id'], ['id'], ondelete='CASCADE',
    )
    op.create_foreign_key(
        'question_reads_question_id_fkey', 'question_reads',
        'questions', ['question_id'], ['id'], ondelete='CASCADE',
    )
    # Add index on question_id for efficient lookups
    op.create_index('ix_question_reads_question_id', 'question_reads', ['question_id'])


def downgrade() -> None:
    """Remove index and revert FKs to no cascade."""
    op.drop_index('ix_question_reads_question_id', table_name='question_reads')
    op.drop_constraint('question_reads_agent_id_fkey', 'question_reads', type_='foreignkey')
    op.drop_constraint('question_reads_question_id_fkey', 'question_reads', type_='foreignkey')
    op.create_foreign_key(
        'question_reads_agent_id_fkey', 'question_reads',
        'agents', ['agent_id'], ['id'],
    )
    op.create_foreign_key(
        'question_reads_question_id_fkey', 'question_reads',
        'questions', ['question_id'], ['id'],
    )
