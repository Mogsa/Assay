from datetime import UTC, datetime
from uuid import uuid4

from assay.cli_state import LocalAgentProfile, load_profiles, save_profiles


def test_local_profile_store_round_trip(tmp_path, monkeypatch):
    monkeypatch.setenv("ASSAY_HOME", str(tmp_path))
    profile = LocalAgentProfile(
        agent_id=uuid4(),
        display_name="Local Agent",
        model_slug="openai/gpt-5",
        runtime_kind="codex-cli",
        base_url="http://localhost:8000",
        access_token="access",
        refresh_token="refresh",
        access_token_expires_at=datetime.now(UTC),
        command="codex",
        args=["-p", "{prompt}"],
    )

    store = load_profiles()
    store.upsert(profile)
    save_profiles(store)

    reloaded = load_profiles()
    resolved = reloaded.resolve("Local Agent")
    assert resolved.agent_id == profile.agent_id
    assert resolved.command == "codex"
