import argparse
import asyncio

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from assay.catalog import ANTHROPIC_CLI_WARNING
from assay.config import settings
from assay.models.model_catalog import ModelCatalog
from assay.models.model_runtime_support import ModelRuntimeSupport
from assay.models.runtime_catalog import RuntimeCatalog


MODELS = [
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

SUPPORT = [
    ("anthropic/claude-opus-4", "claude-cli", "warning", ANTHROPIC_CLI_WARNING),
    ("anthropic/claude-opus-4", "local-command", "supported", None),
    ("anthropic/claude-sonnet-4", "claude-cli", "warning", ANTHROPIC_CLI_WARNING),
    ("anthropic/claude-sonnet-4", "local-command", "supported", None),
    ("openai/gpt-4o", "codex-cli", "supported", None),
    ("openai/gpt-4o", "local-command", "supported", None),
    ("openai/gpt-4o", "openai-api", "supported", None),
    ("openai/gpt-5", "codex-cli", "supported", None),
    ("openai/gpt-5", "local-command", "supported", None),
    ("openai/gpt-5", "openai-api", "supported", None),
    ("google/gemini-2.5-pro", "gemini-cli", "supported", None),
    ("google/gemini-2.5-pro", "local-command", "supported", None),
    ("qwen/qwen3-coder", "local-command", "supported", None),
]


async def upsert_catalog(session: AsyncSession) -> None:
    for payload in MODELS:
        model = await session.get(ModelCatalog, payload["slug"])
        if model is None:
            session.add(ModelCatalog(**payload))
        else:
            for key, value in payload.items():
                setattr(model, key, value)

    for payload in RUNTIMES:
        runtime = await session.get(RuntimeCatalog, payload["slug"])
        if runtime is None:
            session.add(RuntimeCatalog(**payload))
        else:
            for key, value in payload.items():
                setattr(runtime, key, value)

    await session.flush()

    canonical_slugs = {payload["slug"] for payload in MODELS}
    await session.execute(
        delete(ModelRuntimeSupport).where(ModelRuntimeSupport.model_slug.in_(canonical_slugs))
    )
    await session.flush()

    for model_slug, runtime_slug, support_level, terms_warning in SUPPORT:
        session.add(
            ModelRuntimeSupport(
                model_slug=model_slug,
                runtime_slug=runtime_slug,
                support_level=support_level,
                terms_warning=terms_warning,
            )
        )

    await session.commit()


async def _run() -> None:
    engine = create_async_engine(settings.database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        await upsert_catalog(session)
    await engine.dispose()


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync the canonical Assay model catalog")
    parser.parse_args()
    asyncio.run(_run())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
