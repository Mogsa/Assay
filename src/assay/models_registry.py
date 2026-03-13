from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True)
class ModelDefinition:
    slug: str
    display_name: str
    provider: str


@dataclass(frozen=True)
class RuntimeDefinition:
    slug: str
    display_name: str


MODEL_REGISTRY: dict[str, ModelDefinition] = {
    # Anthropic
    "anthropic/claude-opus-4-6": ModelDefinition(
        slug="anthropic/claude-opus-4-6",
        display_name="Claude Opus 4.6",
        provider="anthropic",
    ),
    "anthropic/claude-sonnet-4-6": ModelDefinition(
        slug="anthropic/claude-sonnet-4-6",
        display_name="Claude Sonnet 4.6",
        provider="anthropic",
    ),
    "anthropic/claude-haiku-4-5": ModelDefinition(
        slug="anthropic/claude-haiku-4-5",
        display_name="Claude Haiku 4.5",
        provider="anthropic",
    ),
    # OpenAI
    "openai/gpt-5.4": ModelDefinition(
        slug="openai/gpt-5.4",
        display_name="GPT-5.4",
        provider="openai",
    ),
    "openai/gpt-5.3": ModelDefinition(
        slug="openai/gpt-5.3",
        display_name="GPT-5.3",
        provider="openai",
    ),
    "openai/gpt-5": ModelDefinition(
        slug="openai/gpt-5",
        display_name="GPT-5",
        provider="openai",
    ),
    "openai/gpt-5-mini": ModelDefinition(
        slug="openai/gpt-5-mini",
        display_name="GPT-5 Mini",
        provider="openai",
    ),
    # Google
    "google/gemini-3-pro-preview": ModelDefinition(
        slug="google/gemini-3-pro-preview",
        display_name="Gemini 3 Pro (Preview)",
        provider="google",
    ),
    "google/gemini-3-flash-preview": ModelDefinition(
        slug="google/gemini-3-flash-preview",
        display_name="Gemini 3 Flash (Preview)",
        provider="google",
    ),
    "google/gemini-2.5-pro": ModelDefinition(
        slug="google/gemini-2.5-pro",
        display_name="Gemini 2.5 Pro",
        provider="google",
    ),
    "google/gemini-2.5-flash": ModelDefinition(
        slug="google/gemini-2.5-flash",
        display_name="Gemini 2.5 Flash",
        provider="google",
    ),
    # Qwen
    "qwen/qwen3-coder-plus": ModelDefinition(
        slug="qwen/qwen3-coder-plus",
        display_name="Qwen3 Coder Plus",
        provider="qwen",
    ),
    "qwen/qwen3.5-9b": ModelDefinition(
        slug="qwen/qwen3.5-9b",
        display_name="Qwen 3.5 9B",
        provider="qwen",
    ),
    # MiniMax
    "minimax/minimax-m2.5": ModelDefinition(
        slug="minimax/minimax-m2.5",
        display_name="MiniMax M2.5",
        provider="minimax",
    ),
}

RUNTIME_REGISTRY: dict[str, RuntimeDefinition] = {
    "claude-cli": RuntimeDefinition(slug="claude-cli", display_name="Claude Code"),
    "codex-cli": RuntimeDefinition(slug="codex-cli", display_name="Codex CLI"),
    "gemini-cli": RuntimeDefinition(slug="gemini-cli", display_name="Gemini CLI"),
    "qwen-code": RuntimeDefinition(slug="qwen-code", display_name="Qwen Code"),
    "open-code": RuntimeDefinition(slug="open-code", display_name="OpenCode"),
    "openai-api": RuntimeDefinition(slug="openai-api", display_name="OpenAI API"),
    "local-command": RuntimeDefinition(slug="local-command", display_name="Local Command"),
}


def get_model_definition(model_slug: str | None) -> ModelDefinition | None:
    if model_slug is None:
        return None
    return MODEL_REGISTRY.get(model_slug)


def get_runtime_definition(runtime_slug: str | None) -> RuntimeDefinition | None:
    if runtime_slug is None:
        return None
    return RUNTIME_REGISTRY.get(runtime_slug)


def iter_model_definitions() -> Iterable[ModelDefinition]:
    return MODEL_REGISTRY.values()


def iter_runtime_definitions() -> Iterable[RuntimeDefinition]:
    return RUNTIME_REGISTRY.values()
