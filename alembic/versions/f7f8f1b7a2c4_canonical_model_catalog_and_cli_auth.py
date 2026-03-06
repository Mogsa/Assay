"""canonical_model_catalog_and_cli_auth

Revision ID: f7f8f1b7a2c4
Revises: 9d09f0b1a9a6
Create Date: 2026-03-06 16:20:00.000000

"""

from collections.abc import Sequence
import re
from typing import Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f7f8f1b7a2c4"
down_revision: Union[str, None] = "9d09f0b1a9a6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


CANONICAL_MODELS = [
    {
        "slug": "anthropic/claude-opus-4",
        "provider": "anthropic",
        "family_slug": "anthropic/claude-opus",
        "display_name": "Claude Opus 4",
        "version_label": "4",
        "is_active": True,
        "is_canonical": True,
        "supports_cli": True,
        "supports_api": False,
    },
    {
        "slug": "anthropic/claude-sonnet-4",
        "provider": "anthropic",
        "family_slug": "anthropic/claude-sonnet",
        "display_name": "Claude Sonnet 4",
        "version_label": "4",
        "is_active": True,
        "is_canonical": True,
        "supports_cli": True,
        "supports_api": False,
    },
    {
        "slug": "openai/gpt-4o",
        "provider": "openai",
        "family_slug": "openai/gpt-4o",
        "display_name": "GPT-4o",
        "version_label": "4o",
        "is_active": True,
        "is_canonical": True,
        "supports_cli": True,
        "supports_api": True,
    },
    {
        "slug": "openai/gpt-5",
        "provider": "openai",
        "family_slug": "openai/gpt",
        "display_name": "GPT-5",
        "version_label": "5",
        "is_active": True,
        "is_canonical": True,
        "supports_cli": True,
        "supports_api": True,
    },
    {
        "slug": "google/gemini-2.5-pro",
        "provider": "google",
        "family_slug": "google/gemini-pro",
        "display_name": "Gemini 2.5 Pro",
        "version_label": "2.5-pro",
        "is_active": True,
        "is_canonical": True,
        "supports_cli": True,
        "supports_api": False,
    },
    {
        "slug": "qwen/qwen3-coder",
        "provider": "qwen",
        "family_slug": "qwen/qwen3",
        "display_name": "Qwen3 Coder",
        "version_label": "3-coder",
        "is_active": True,
        "is_canonical": True,
        "supports_cli": True,
        "supports_api": False,
    },
]

RUNTIMES = [
    {
        "slug": "claude-cli",
        "display_name": "Claude CLI",
        "transport": "cli",
        "auth_mode": "delegated_cli",
        "is_active": True,
    },
    {
        "slug": "gemini-cli",
        "display_name": "Gemini CLI",
        "transport": "cli",
        "auth_mode": "delegated_cli",
        "is_active": True,
    },
    {
        "slug": "codex-cli",
        "display_name": "Codex CLI",
        "transport": "cli",
        "auth_mode": "delegated_cli",
        "is_active": True,
    },
    {
        "slug": "local-command",
        "display_name": "Local Command",
        "transport": "cli",
        "auth_mode": "delegated_cli",
        "is_active": True,
    },
    {
        "slug": "openai-api",
        "display_name": "OpenAI API",
        "transport": "api",
        "auth_mode": "local_env_api",
        "is_active": True,
    },
]

MODEL_RUNTIME_SUPPORT = [
    ("anthropic/claude-opus-4", "claude-cli"),
    ("anthropic/claude-opus-4", "local-command"),
    ("anthropic/claude-sonnet-4", "claude-cli"),
    ("anthropic/claude-sonnet-4", "local-command"),
    ("openai/gpt-4o", "codex-cli"),
    ("openai/gpt-4o", "local-command"),
    ("openai/gpt-4o", "openai-api"),
    ("openai/gpt-5", "codex-cli"),
    ("openai/gpt-5", "local-command"),
    ("openai/gpt-5", "openai-api"),
    ("google/gemini-2.5-pro", "gemini-cli"),
    ("google/gemini-2.5-pro", "local-command"),
    ("qwen/qwen3-coder", "local-command"),
]

LEGACY_ALIASES = {
    "claude-opus": "anthropic/claude-opus-4",
    "claude-opus-4": "anthropic/claude-opus-4",
    "claude-sonnet": "anthropic/claude-sonnet-4",
    "claude-sonnet-4": "anthropic/claude-sonnet-4",
    "gpt-4o": "openai/gpt-4o",
    "gpt-5": "openai/gpt-5",
    "gemini-2.5-pro": "google/gemini-2.5-pro",
    "gemini-pro": "google/gemini-2.5-pro",
    "qwen3-coder": "qwen/qwen3-coder",
    "qwen-coder": "qwen/qwen3-coder",
    "qwen/qwen3-coder": "qwen/qwen3-coder",
}


def _sanitize(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "legacy-unknown"


def _infer_runtime(model_slug: str | None, agent_type: str) -> str:
    if model_slug in {"anthropic/claude-opus-4", "anthropic/claude-sonnet-4"}:
        return "claude-cli"
    if model_slug == "google/gemini-2.5-pro":
        return "gemini-cli"
    if model_slug in {"openai/gpt-4o", "openai/gpt-5"}:
        return "openai-api"
    if model_slug == "qwen/qwen3-coder":
        return "local-command"

    normalized = agent_type.strip().lower()
    if "claude" in normalized:
        return "claude-cli"
    if "gemini" in normalized:
        return "gemini-cli"
    if "gpt" in normalized or "openai" in normalized:
        return "openai-api"
    if "codex" in normalized:
        return "codex-cli"
    return "local-command"


def upgrade() -> None:
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
        sa.ForeignKeyConstraint(["model_slug"], ["model_catalog.slug"]),
        sa.ForeignKeyConstraint(["runtime_slug"], ["runtime_catalog.slug"]),
        sa.PrimaryKeyConstraint("model_slug", "runtime_slug"),
    )
    op.add_column(
        "agents",
        sa.Column("kind", sa.String(length=16), nullable=True, server_default="agent"),
    )
    op.add_column("agents", sa.Column("model_slug", sa.String(length=128), nullable=True))
    op.add_column("agents", sa.Column("runtime_kind", sa.String(length=64), nullable=True))
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
    op.create_index("idx_agents_kind", "agents", ["kind"])
    op.create_index("idx_agents_model_slug", "agents", ["model_slug"])
    op.create_index("idx_agents_runtime_kind", "agents", ["runtime_kind"])
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

    connection = op.get_bind()
    model_table = sa.table(
        "model_catalog",
        sa.column("slug", sa.String),
        sa.column("provider", sa.String),
        sa.column("family_slug", sa.String),
        sa.column("display_name", sa.String),
        sa.column("version_label", sa.String),
        sa.column("is_active", sa.Boolean),
        sa.column("is_canonical", sa.Boolean),
        sa.column("supports_cli", sa.Boolean),
        sa.column("supports_api", sa.Boolean),
    )
    runtime_table = sa.table(
        "runtime_catalog",
        sa.column("slug", sa.String),
        sa.column("display_name", sa.String),
        sa.column("transport", sa.String),
        sa.column("auth_mode", sa.String),
        sa.column("is_active", sa.Boolean),
    )
    support_table = sa.table(
        "model_runtime_support",
        sa.column("model_slug", sa.String),
        sa.column("runtime_slug", sa.String),
    )

    op.bulk_insert(model_table, CANONICAL_MODELS)
    op.bulk_insert(runtime_table, RUNTIMES)
    op.bulk_insert(
        support_table,
        [{"model_slug": model_slug, "runtime_slug": runtime_slug} for model_slug, runtime_slug in MODEL_RUNTIME_SUPPORT],
    )

    display_names = {row["slug"]: row["display_name"] for row in CANONICAL_MODELS}
    existing_types = [
        row[0]
        for row in connection.execute(
            sa.text("SELECT DISTINCT agent_type FROM agents WHERE agent_type IS NOT NULL")
        )
    ]
    legacy_rows = []
    legacy_support_rows = []
    seen_legacy_slugs = set()

    connection.execute(
        sa.text(
            "UPDATE agents SET kind = 'human', model_slug = NULL, runtime_kind = NULL "
            "WHERE lower(agent_type) = 'human'"
        )
    )

    for agent_type in existing_types:
        normalized = agent_type.strip().lower()
        if normalized == "human":
            continue

        canonical_slug = LEGACY_ALIASES.get(normalized)
        runtime_kind = _infer_runtime(canonical_slug, agent_type)
        resolved_model_slug = canonical_slug
        if resolved_model_slug is None:
            resolved_model_slug = f"legacy/{_sanitize(agent_type)}"
            if resolved_model_slug not in seen_legacy_slugs:
                seen_legacy_slugs.add(resolved_model_slug)
                legacy_rows.append(
                    {
                        "slug": resolved_model_slug,
                        "provider": "legacy",
                        "family_slug": "legacy/custom",
                        "display_name": agent_type,
                        "version_label": "legacy",
                        "is_active": True,
                        "is_canonical": False,
                        "supports_cli": True,
                        "supports_api": False,
                    }
                )
                legacy_support_rows.append(
                    {
                        "model_slug": resolved_model_slug,
                        "runtime_slug": "local-command",
                    }
                )
            runtime_kind = "local-command"

        connection.execute(
            sa.text(
                "UPDATE agents SET kind = 'agent', model_slug = :model_slug, runtime_kind = :runtime_kind "
                "WHERE agent_type = :agent_type"
            ),
            {
                "model_slug": resolved_model_slug,
                "runtime_kind": runtime_kind,
                "agent_type": agent_type,
            },
        )

        if canonical_slug is not None:
            connection.execute(
                sa.text(
                    "UPDATE agents SET agent_type = :display_name WHERE agent_type = :agent_type"
                ),
                {"display_name": display_names[canonical_slug], "agent_type": agent_type},
            )

    if legacy_rows:
        op.bulk_insert(model_table, legacy_rows)
    if legacy_support_rows:
        op.bulk_insert(support_table, legacy_support_rows)

    connection.execute(
        sa.text(
            "UPDATE agents SET kind = 'agent' WHERE kind IS NULL AND lower(coalesce(agent_type, '')) <> 'human'"
        )
    )
    op.alter_column("agents", "kind", nullable=False, server_default="agent")


def downgrade() -> None:
    op.drop_index("idx_cli_device_authorizations_status", table_name="cli_device_authorizations")
    op.drop_index("idx_cli_device_authorizations_expiry", table_name="cli_device_authorizations")
    op.drop_table("cli_device_authorizations")
    op.drop_index("idx_agent_auth_tokens_expiry", table_name="agent_auth_tokens")
    op.drop_index("idx_agent_auth_tokens_agent", table_name="agent_auth_tokens")
    op.drop_table("agent_auth_tokens")
    op.drop_index("idx_agents_runtime_kind", table_name="agents")
    op.drop_index("idx_agents_model_slug", table_name="agents")
    op.drop_index("idx_agents_kind", table_name="agents")
    op.drop_constraint("fk_agents_runtime_kind", "agents", type_="foreignkey")
    op.drop_constraint("fk_agents_model_slug", "agents", type_="foreignkey")
    op.drop_column("agents", "runtime_kind")
    op.drop_column("agents", "model_slug")
    op.drop_column("agents", "kind")
    op.drop_table("model_runtime_support")
    op.drop_table("runtime_catalog")
    op.drop_table("model_catalog")
