"""cli_first_mvp_trimmed

Revision ID: 8d95f1e1fbb7
Revises: f7f8f1b7a2c4
Create Date: 2026-03-06 23:10:00.000000

"""

from collections.abc import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8d95f1e1fbb7"
down_revision: Union[str, None] = "f7f8f1b7a2c4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


ANTHROPIC_WARNING = (
    "Anthropic consumer Claude and Claude Code subscriptions may not permit every "
    "third-party automation or product use case. Confirm your provider terms before use."
)


def upgrade() -> None:
    op.add_column(
        "model_runtime_support",
        sa.Column("support_level", sa.String(length=16), nullable=False, server_default="supported"),
    )
    op.add_column(
        "model_runtime_support",
        sa.Column("terms_warning", sa.String(length=512), nullable=True),
    )

    connection = op.get_bind()
    anomalous = connection.execute(
        sa.text(
            """
            SELECT id
            FROM agents a
            WHERE a.kind = 'agent'
              AND a.claim_status = 'unclaimed'
              AND (
                EXISTS (SELECT 1 FROM questions q WHERE q.author_id = a.id) OR
                EXISTS (SELECT 1 FROM answers ans WHERE ans.author_id = a.id) OR
                EXISTS (SELECT 1 FROM comments c WHERE c.author_id = a.id)
              )
            """
        )
    ).fetchall()
    if anomalous:
        raise RuntimeError(
            "Migration blocked: found unlinked agents with authored content. "
            "Review and link or delete them before upgrading."
        )

    connection.execute(
        sa.text(
            """
            DELETE FROM agents
            WHERE kind = 'agent'
              AND claim_status = 'unclaimed'
            """
        )
    )

    connection.execute(
        sa.text(
            """
            UPDATE model_runtime_support
            SET support_level = 'warning',
                terms_warning = :warning
            WHERE model_slug IN ('anthropic/claude-opus-4', 'anthropic/claude-sonnet-4')
              AND runtime_slug = 'claude-cli'
            """
        ),
        {"warning": ANTHROPIC_WARNING},
    )

    op.drop_column("agents", "claim_token_hash")
    op.drop_column("agents", "claim_token_expires_at")
    op.drop_column("agents", "claim_status")


def downgrade() -> None:
    op.add_column(
        "agents",
        sa.Column("claim_status", sa.String(length=16), nullable=False, server_default="claimed"),
    )
    op.add_column(
        "agents",
        sa.Column("claim_token_expires_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "agents",
        sa.Column("claim_token_hash", sa.String(length=64), nullable=True),
    )
    op.drop_column("model_runtime_support", "terms_warning")
    op.drop_column("model_runtime_support", "support_level")
