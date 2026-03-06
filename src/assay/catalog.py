import re

ANTHROPIC_CLI_WARNING = (
    "Anthropic consumer Claude and Claude Code subscriptions may not permit every "
    "third-party automation or product use case. Confirm your provider terms before use."
)
CUSTOM_MODEL_WARNING = (
    "Custom models are allowed, but they are excluded from canonical model averages "
    "and agent-type leaderboards."
)


DEFAULT_RUNTIME_BY_MODEL: dict[str, str] = {
    "anthropic/claude-opus-4": "claude-cli",
    "anthropic/claude-sonnet-4": "claude-cli",
    "openai/gpt-4o": "openai-api",
    "openai/gpt-5": "openai-api",
    "google/gemini-2.5-pro": "gemini-cli",
    "qwen/qwen3-coder": "local-command",
}


LEGACY_MODEL_ALIASES: dict[str, str] = {
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


def sanitize_legacy_model_slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "legacy-unknown"


def sanitize_catalog_slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "unknown"


def custom_model_slug(provider: str, model_name: str) -> str:
    return f"custom/{sanitize_catalog_slug(provider)}/{sanitize_catalog_slug(model_name)}"


def legacy_model_slug(value: str) -> str:
    return f"legacy/{sanitize_legacy_model_slug(value)}"


def normalize_agent_type(value: str) -> str:
    return value.strip().lower()


def resolve_legacy_alias(agent_type: str) -> str | None:
    return LEGACY_MODEL_ALIASES.get(normalize_agent_type(agent_type))


def infer_runtime_kind(*, model_slug: str | None = None, agent_type: str | None = None) -> str:
    if model_slug and model_slug in DEFAULT_RUNTIME_BY_MODEL:
        return DEFAULT_RUNTIME_BY_MODEL[model_slug]

    alias = resolve_legacy_alias(agent_type or "")
    if alias and alias in DEFAULT_RUNTIME_BY_MODEL:
        return DEFAULT_RUNTIME_BY_MODEL[alias]

    normalized = normalize_agent_type(agent_type or "")
    if "claude" in normalized:
        return "claude-cli"
    if "gemini" in normalized:
        return "gemini-cli"
    if "gpt" in normalized or "openai" in normalized:
        return "openai-api"
    if "codex" in normalized:
        return "codex-cli"
    return "local-command"
