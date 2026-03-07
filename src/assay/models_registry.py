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
    "anthropic/claude-opus-4": ModelDefinition(
        slug="anthropic/claude-opus-4",
        display_name="Claude Opus 4",
        provider="anthropic",
    ),
    "anthropic/claude-sonnet-4": ModelDefinition(
        slug="anthropic/claude-sonnet-4",
        display_name="Claude Sonnet 4",
        provider="anthropic",
    ),
    "anthropic/claude-haiku-4": ModelDefinition(
        slug="anthropic/claude-haiku-4",
        display_name="Claude Haiku 4",
        provider="anthropic",
    ),
    # OpenAI
    "openai/gpt-4o": ModelDefinition(
        slug="openai/gpt-4o",
        display_name="GPT-4o",
        provider="openai",
    ),
    "openai/gpt-5": ModelDefinition(
        slug="openai/gpt-5",
        display_name="GPT-5",
        provider="openai",
    ),
    "openai/o3": ModelDefinition(
        slug="openai/o3",
        display_name="o3",
        provider="openai",
    ),
    "openai/o4-mini": ModelDefinition(
        slug="openai/o4-mini",
        display_name="o4-mini",
        provider="openai",
    ),
    # Google
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
    "qwen/qwen3-coder": ModelDefinition(
        slug="qwen/qwen3-coder",
        display_name="Qwen3 Coder",
        provider="qwen",
    ),
    # DeepSeek
    "deepseek/deepseek-r1": ModelDefinition(
        slug="deepseek/deepseek-r1",
        display_name="DeepSeek R1",
        provider="deepseek",
    ),
    # Meta
    "meta/llama-4-maverick": ModelDefinition(
        slug="meta/llama-4-maverick",
        display_name="Llama 4 Maverick",
        provider="meta",
    ),
}

RUNTIME_REGISTRY: dict[str, RuntimeDefinition] = {
    "claude-cli": RuntimeDefinition(slug="claude-cli", display_name="Claude Code"),
    "codex-cli": RuntimeDefinition(slug="codex-cli", display_name="Codex CLI"),
    "gemini-cli": RuntimeDefinition(slug="gemini-cli", display_name="Gemini CLI"),
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
