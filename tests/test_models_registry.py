from assay.models_registry import MODEL_REGISTRY, RUNTIME_REGISTRY, get_model_definition, get_runtime_definition


def test_known_model_slugs_are_registered():
    assert "anthropic/claude-opus-4-6" in MODEL_REGISTRY
    assert "openai/gpt-5" in MODEL_REGISTRY


def test_known_runtime_slugs_are_registered():
    assert "claude-cli" in RUNTIME_REGISTRY
    assert "codex-cli" in RUNTIME_REGISTRY
    assert "gemini-cli" in RUNTIME_REGISTRY
    assert "open-code" in RUNTIME_REGISTRY
    assert "openai-api" in RUNTIME_REGISTRY
    assert "local-command" in RUNTIME_REGISTRY


def test_lookup_returns_display_names():
    assert get_model_definition("anthropic/claude-opus-4-6").display_name == "Claude Opus 4.6"
    assert get_runtime_definition("claude-cli").display_name == "Claude Code"


def test_unknown_registry_entries_return_none():
    assert get_model_definition("unknown/model") is None
    assert get_runtime_definition("unknown-runtime") is None


def test_qwen_3_5_9b_in_registry():
    model = get_model_definition("qwen/qwen3.5-9b")
    assert model is not None
    assert model.display_name == "Qwen 3.5 9B"
    assert model.provider == "qwen"
