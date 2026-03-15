"""add question_reads table

Revision ID: de440105dc45
Revises: 0da39e524442
Create Date: 2026-03-15 11:55:10.457720

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'de440105dc45'
down_revision: Union[str, Sequence[str], None] = '0da39e524442'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('question_reads',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('agent_id', sa.Uuid(), nullable=False),
    sa.Column('question_id', sa.Uuid(), nullable=False),
    sa.Column('read_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ),
    sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('agent_id', 'question_id', name='uq_question_reads_agent_question')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('question_reads')
