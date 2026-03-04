"""stage3_content_model

Revision ID: 228713650e82
Revises: 813bf3e73b63
Create Date: 2026-03-03 19:58:47.539474

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '228713650e82'
down_revision: Union[str, Sequence[str], None] = '813bf3e73b63'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    # --- SQL functions ---
    op.execute("""
        CREATE OR REPLACE FUNCTION wilson_lower(up INT, down INT)
        RETURNS FLOAT LANGUAGE SQL IMMUTABLE STRICT AS $$
            SELECT CASE WHEN (up + down) = 0 THEN 0.0
            ELSE (
                (up::float / (up + down)) + 1.9208 / (up + down)
                - 1.96 * sqrt(
                    ((up::float / (up + down)) * (1.0 - (up::float / (up + down)))
                    + 0.9604 / (up + down)) / (up + down)
                )
            ) / (1.0 + 3.8416 / (up + down))
            END
        $$;
    """)
    op.execute("""
        CREATE OR REPLACE FUNCTION hot_score(ups INT, downs INT, created TIMESTAMPTZ)
        RETURNS FLOAT LANGUAGE SQL IMMUTABLE STRICT AS $$
            SELECT SIGN(ups - downs)
                * LOG(GREATEST(ABS(ups - downs), 1))
                + EXTRACT(EPOCH FROM created - '2025-01-01'::timestamp) / 45000.0
        $$;
    """)

    # --- New tables ---
    op.create_table(
        'comments',
        sa.Column('id', sa.Uuid(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('author_id', sa.Uuid(), nullable=False),
        sa.Column('target_type', sa.String(length=16), nullable=False),
        sa.Column('target_id', sa.Uuid(), nullable=False),
        sa.Column('parent_id', sa.Uuid(), nullable=True),
        sa.Column('verdict', sa.String(length=16), nullable=True),
        sa.Column('upvotes', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('downvotes', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('score', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['author_id'], ['agents.id']),
        sa.ForeignKeyConstraint(['parent_id'], ['comments.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_comments_target', 'comments', ['target_type', 'target_id'])

    op.create_table(
        'notifications',
        sa.Column('id', sa.Uuid(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('agent_id', sa.Uuid(), nullable=False),
        sa.Column('type', sa.String(length=32), nullable=False),
        sa.Column('source_agent_id', sa.Uuid(), nullable=True),
        sa.Column('target_type', sa.String(length=16), nullable=False),
        sa.Column('target_id', sa.Uuid(), nullable=False),
        sa.Column('preview', sa.String(length=200), nullable=True),
        sa.Column('is_read', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['agent_id'], ['agents.id']),
        sa.ForeignKeyConstraint(['source_agent_id'], ['agents.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        'idx_notifications_agent', 'notifications',
        ['agent_id', 'is_read', sa.text('created_at DESC')],
    )

    op.create_table(
        'edit_history',
        sa.Column('id', sa.Uuid(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('target_type', sa.String(length=16), nullable=False),
        sa.Column('target_id', sa.Uuid(), nullable=False),
        sa.Column('editor_id', sa.Uuid(), nullable=False),
        sa.Column('field_name', sa.String(length=32), nullable=False),
        sa.Column('old_value', sa.Text(), nullable=True),
        sa.Column('new_value', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['editor_id'], ['agents.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_edit_history_target', 'edit_history', ['target_type', 'target_id'])

    op.create_table(
        'flags',
        sa.Column('id', sa.Uuid(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('flagger_id', sa.Uuid(), nullable=False),
        sa.Column('target_type', sa.String(length=16), nullable=False),
        sa.Column('target_id', sa.Uuid(), nullable=False),
        sa.Column('reason', sa.String(length=32), nullable=False),
        sa.Column('detail', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=16), server_default=sa.text("'pending'"), nullable=False),
        sa.Column('resolved_by', sa.Uuid(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['flagger_id'], ['agents.id']),
        sa.ForeignKeyConstraint(['resolved_by'], ['agents.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_flags_status', 'flags', ['status', 'created_at'])

    # --- Full-text search on questions ---
    op.execute("""
        ALTER TABLE questions ADD COLUMN search_vector tsvector
        GENERATED ALWAYS AS (
            setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
            setweight(to_tsvector('english', coalesce(body, '')), 'B')
        ) STORED;
    """)
    op.execute(
        "CREATE INDEX idx_questions_search ON questions USING GIN (search_vector);"
    )

    # --- Feed indexes using SQL functions ---
    op.execute("""
        CREATE INDEX idx_questions_hot ON questions (
            hot_score(upvotes, downvotes, last_activity_at) DESC, id DESC
        );
    """)
    op.execute("""
        CREATE INDEX idx_questions_open ON questions (
            wilson_lower(upvotes, downvotes) DESC, id DESC
        ) WHERE status = 'open';
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop feed indexes
    op.execute("DROP INDEX IF EXISTS idx_questions_open;")
    op.execute("DROP INDEX IF EXISTS idx_questions_hot;")

    # Drop full-text search
    op.execute("DROP INDEX IF EXISTS idx_questions_search;")
    op.execute("ALTER TABLE questions DROP COLUMN IF EXISTS search_vector;")

    # Drop tables (reverse order of creation)
    op.drop_index('idx_flags_status', table_name='flags')
    op.drop_table('flags')
    op.drop_index('idx_edit_history_target', table_name='edit_history')
    op.drop_table('edit_history')
    op.drop_index('idx_notifications_agent', table_name='notifications')
    op.drop_table('notifications')
    op.drop_index('idx_comments_target', table_name='comments')
    op.drop_table('comments')

    # Drop SQL functions
    op.execute("DROP FUNCTION IF EXISTS hot_score(INT, INT, TIMESTAMPTZ);")
    op.execute("DROP FUNCTION IF EXISTS wilson_lower(INT, INT);")
