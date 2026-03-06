"""add agent runtime metadata

Revision ID: 4b7d2e8a2f31
Revises: 9d09f0b1a9a6
Create Date: 2026-03-06 18:10:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4b7d2e8a2f31"
down_revision = "9d09f0b1a9a6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("agents", sa.Column("description", sa.String(length=512), nullable=True))
    op.add_column("agents", sa.Column("provider", sa.String(length=64), nullable=True))
    op.add_column("agents", sa.Column("model_name", sa.String(length=128), nullable=True))
    op.add_column("agents", sa.Column("runtime_kind", sa.String(length=64), nullable=True))


def downgrade() -> None:
    op.drop_column("agents", "runtime_kind")
    op.drop_column("agents", "model_name")
    op.drop_column("agents", "provider")
    op.drop_column("agents", "description")
