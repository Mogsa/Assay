"""cli_first_api_keys

Revision ID: 3c7d9e1a2b4f
Revises: 8d95f1e1fbb7
Create Date: 2026-03-07 12:00:00.000000

"""

from collections.abc import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3c7d9e1a2b4f"
down_revision: Union[str, None] = "8d95f1e1fbb7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("agents", sa.Column("last_active_at", sa.DateTime(timezone=True), nullable=True))

    op.drop_constraint("fk_agents_model_slug", "agents", type_="foreignkey")
    op.drop_constraint("fk_agents_runtime_kind", "agents", type_="foreignkey")

    op.drop_table("agent_auth_tokens")
    op.drop_table("cli_device_authorizations")
    op.drop_table("agent_runtime_policies")
    op.drop_table("model_runtime_support")
    op.drop_table("runtime_catalog")
    op.drop_table("model_catalog")


def downgrade() -> None:
    op.create_table(
        "model_catalog",
        sa.Column("slug", sa.String(length=128), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False),
        sa.Column("family_slug", sa.String(length=128), nullable=False),
        sa.Column("display_name", sa.String(length=128), nullable=False),
        sa.Column("version_label", sa.String(length=64), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_canonical", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("supports_cli", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("supports_api", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.PrimaryKeyConstraint("slug"),
    )
    op.create_table(
        "runtime_catalog",
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("display_name", sa.String(length=128), nullable=False),
        sa.Column("transport", sa.String(length=16), nullable=False),
        sa.Column("auth_mode", sa.String(length=32), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.PrimaryKeyConstraint("slug"),
    )
    op.create_table(
        "model_runtime_support",
        sa.Column("model_slug", sa.String(length=128), nullable=False),
        sa.Column("runtime_slug", sa.String(length=64), nullable=False),
        sa.Column("support_level", sa.String(length=16), nullable=False, server_default="supported"),
        sa.Column("terms_warning", sa.String(length=512), nullable=True),
        sa.ForeignKeyConstraint(["model_slug"], ["model_catalog.slug"]),
        sa.ForeignKeyConstraint(["runtime_slug"], ["runtime_catalog.slug"]),
        sa.PrimaryKeyConstraint("model_slug", "runtime_slug"),
    )
    op.create_table(
        "agent_auth_tokens",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("agent_id", sa.Uuid(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("token_kind", sa.String(length=16), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["agent_id"], ["agents.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index("idx_agent_auth_tokens_agent", "agent_auth_tokens", ["agent_id"])
    op.create_index("idx_agent_auth_tokens_expiry", "agent_auth_tokens", ["expires_at"])
    op.create_table(
        "cli_device_authorizations",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("device_code_hash", sa.String(length=64), nullable=False),
        sa.Column("user_code_hash", sa.String(length=64), nullable=False),
        sa.Column("display_name", sa.String(length=128), nullable=False),
        sa.Column("model_slug", sa.String(length=128), nullable=False),
        sa.Column("runtime_kind", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False, server_default="pending"),
        sa.Column("owner_id", sa.Uuid(), nullable=True),
        sa.Column("agent_id", sa.Uuid(), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("denied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["agent_id"], ["agents.id"]),
        sa.ForeignKeyConstraint(["model_slug"], ["model_catalog.slug"]),
        sa.ForeignKeyConstraint(["owner_id"], ["agents.id"]),
        sa.ForeignKeyConstraint(["runtime_kind"], ["runtime_catalog.slug"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("device_code_hash"),
        sa.UniqueConstraint("user_code_hash"),
    )
    op.create_index(
        "idx_cli_device_authorizations_expiry",
        "cli_device_authorizations",
        ["expires_at"],
    )
    op.create_index(
        "idx_cli_device_authorizations_status",
        "cli_device_authorizations",
        ["status"],
    )
    op.create_table(
        "agent_runtime_policies",
        sa.Column("agent_id", sa.Uuid(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("dry_run", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("max_actions_per_hour", sa.Integer(), nullable=False, server_default="6"),
        sa.Column("max_questions_per_day", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_answers_per_hour", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("max_reviews_per_hour", sa.Integer(), nullable=False, server_default="6"),
        sa.Column("allow_question_asking", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("allow_reposts", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "allowed_community_ids",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'::json"),
        ),
        sa.Column("global_only", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.ForeignKeyConstraint(["agent_id"], ["agents.id"]),
        sa.PrimaryKeyConstraint("agent_id"),
    )

    op.create_foreign_key(
        "fk_agents_model_slug",
        "agents",
        "model_catalog",
        ["model_slug"],
        ["slug"],
    )
    op.create_foreign_key(
        "fk_agents_runtime_kind",
        "agents",
        "runtime_catalog",
        ["runtime_kind"],
        ["slug"],
    )
    op.drop_column("agents", "last_active_at")
