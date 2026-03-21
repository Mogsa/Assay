"""v2 restructure: drop votes, modify links, new sql functions

Revision ID: d21dfc8d96c0
Revises: b3c4d5e6f7a8
Create Date: 2026-03-21 14:57:44.119654

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd21dfc8d96c0'
down_revision: Union[str, Sequence[str], None] = 'b3c4d5e6f7a8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 0. Drop functional indexes that depend on vote columns/functions
    op.execute("DROP INDEX IF EXISTS idx_questions_hot")
    op.execute("DROP INDEX IF EXISTS idx_questions_open")

    # 1. Drop votes table
    op.drop_table("votes")

    # 2. Remove vote columns from content tables
    op.drop_column("questions", "upvotes")
    op.drop_column("questions", "downvotes")
    op.drop_column("questions", "score")
    op.drop_column("answers", "upvotes")
    op.drop_column("answers", "downvotes")
    op.drop_column("answers", "score")
    op.drop_column("comments", "upvotes")
    op.drop_column("comments", "downvotes")
    op.drop_column("comments", "score")

    # 3. Drop old SQL functions
    op.execute("DROP FUNCTION IF EXISTS wilson_lower(INT, INT)")
    op.execute("DROP FUNCTION IF EXISTS hot_score(INT, INT, TIMESTAMPTZ)")

    # 4. Add reason column to links
    op.add_column("links", sa.Column("reason", sa.Text(), nullable=True))

    # 5. Update link unique constraint: add created_by
    op.execute("""
        DO $$
        DECLARE cname TEXT;
        BEGIN
            SELECT constraint_name INTO cname
            FROM information_schema.table_constraints
            WHERE table_name = 'links' AND constraint_type = 'UNIQUE'
            LIMIT 1;
            IF cname IS NOT NULL THEN
                EXECUTE 'ALTER TABLE links DROP CONSTRAINT ' || cname;
            END IF;
        END $$;
    """)
    op.create_unique_constraint(
        "uq_links_source_target_type_creator",
        "links",
        ["source_type", "source_id", "target_type", "target_id", "link_type", "created_by"],
    )

    # 6. Convert old link types
    op.execute("UPDATE links SET link_type = 'extends' WHERE link_type = 'solves'")
    op.execute("UPDATE links SET link_type = 'references' WHERE link_type = 'repost'")

    # 7. Add CHECK constraint for link types
    op.create_check_constraint(
        "ck_links_link_type",
        "links",
        "link_type IN ('references', 'extends', 'contradicts')",
    )

    # 8. Create new SQL functions
    op.execute("""
        CREATE OR REPLACE FUNCTION frontier_score_fn(r FLOAT, n FLOAT, g FLOAT)
        RETURNS FLOAT LANGUAGE SQL IMMUTABLE STRICT AS $$
            SELECT sqrt(power(r-1,2) + power(n-1,2) + power(g-1,2))
                 - sqrt(power(5-r,2) + power(5-n,2) + power(5-g,2))
        $$
    """)

    op.execute("""
        CREATE OR REPLACE FUNCTION hot_frontier(score FLOAT, created TIMESTAMPTZ)
        RETURNS FLOAT LANGUAGE SQL IMMUTABLE STRICT AS $$
            SELECT COALESCE(score, 0.0)
                + EXTRACT(EPOCH FROM created - '2025-01-01T00:00:00+00'::timestamptz) / 45000.0
        $$
    """)

    # 9. Create replacement index for hot sort
    op.execute("""
        CREATE INDEX idx_questions_hot_frontier
        ON questions (hot_frontier(frontier_score, last_activity_at) DESC, id DESC)
    """)


def downgrade() -> None:
    """Downgrade not supported — v2 is a one-way migration."""
    raise NotImplementedError("v2 restructure cannot be reversed automatically")
