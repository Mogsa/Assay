"""compatibility bridge for previous experimental branch

Revision ID: 8d95f1e1fbb7
Revises: 9d09f0b1a9a6
Create Date: 2026-03-06 18:45:00.000000
"""

from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = "8d95f1e1fbb7"
down_revision: Union[str, Sequence[str], None] = "9d09f0b1a9a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """No-op compatibility revision.

    This branch existed in an earlier experimental line deployed on Linux.
    We keep the same revision id here so Alembic can upgrade from that live
    database state onto the rebuilt main-based branch without stamping.
    """


def downgrade() -> None:
    """No-op compatibility revision."""
