"""add source_metadata to questions

Revision ID: 0da39e524442
Revises: 8d0715e6bf38
Create Date: 2026-03-11 16:42:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = "0da39e524442"
down_revision: str = "8d0715e6bf38"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("questions", sa.Column("source_metadata", JSONB, nullable=True))


def downgrade() -> None:
    op.drop_column("questions", "source_metadata")
