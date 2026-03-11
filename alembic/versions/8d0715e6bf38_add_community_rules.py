"""add community rules

Revision ID: 8d0715e6bf38
Revises: 3c7d9e1a2b4f
Create Date: 2026-03-11 14:57:14.090796

"""

from alembic import op
import sqlalchemy as sa

revision: str = "8d0715e6bf38"
down_revision: str = "3c7d9e1a2b4f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("communities", sa.Column("rules", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("communities", "rules")
