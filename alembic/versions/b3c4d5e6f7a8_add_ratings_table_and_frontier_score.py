"""add ratings table and frontier_score columns

Revision ID: b3c4d5e6f7a8
Revises: d2aed9fc3f02
Create Date: 2026-03-19 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b3c4d5e6f7a8'
down_revision: Union[str, Sequence[str], None] = 'd2aed9fc3f02'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('ratings',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('rater_id', sa.Uuid(), nullable=False),
        sa.Column('target_type', sa.String(16), nullable=False),
        sa.Column('target_id', sa.Uuid(), nullable=False),
        sa.Column('rigour', sa.SmallInteger(), nullable=False),
        sa.Column('novelty', sa.SmallInteger(), nullable=False),
        sa.Column('generativity', sa.SmallInteger(), nullable=False),
        sa.Column('reasoning', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('rater_id', 'target_type', 'target_id'),
    )
    op.create_index('idx_ratings_target', 'ratings', ['target_type', 'target_id'])
    op.create_index(op.f('ix_ratings_rater_id'), 'ratings', ['rater_id'])

    op.add_column('questions', sa.Column('frontier_score', sa.Float(), server_default='0.0', nullable=False))
    op.add_column('answers', sa.Column('frontier_score', sa.Float(), server_default='0.0', nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('answers', 'frontier_score')
    op.drop_column('questions', 'frontier_score')
    op.drop_index(op.f('ix_ratings_rater_id'), table_name='ratings')
    op.drop_index('idx_ratings_target', table_name='ratings')
    op.drop_table('ratings')
