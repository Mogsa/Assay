"""fix: add server_default to community_members.role

Revision ID: 813bf3e73b63
Revises: e5dd54458687
Create Date: 2026-03-03 20:09:53.916765

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '813bf3e73b63'
down_revision: Union[str, Sequence[str], None] = 'e5dd54458687'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add server_default to community_members.role."""
    op.alter_column(
        "community_members",
        "role",
        server_default=sa.text("'subscriber'"),
    )


def downgrade() -> None:
    """Remove server_default from community_members.role."""
    op.alter_column(
        "community_members",
        "role",
        server_default=None,
    )
