import json
import os
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


def assay_home() -> Path:
    env_home = os.environ.get("ASSAY_HOME")
    if env_home:
        return Path(env_home).expanduser()
    return Path.home() / ".assay"


def profiles_path() -> Path:
    return assay_home() / "profiles.json"


def skill_cache_dir() -> Path:
    return assay_home() / "skill-cache"


class LocalAgentProfile(BaseModel):
    agent_id: uuid.UUID
    display_name: str
    model_slug: str
    runtime_kind: str
    base_url: str
    access_token: str
    refresh_token: str
    access_token_expires_at: datetime | None = None
    timeout_mode: Literal["normal", "deep"] = "normal"
    prompt_timeout_seconds: int | None = None
    command: str | None = None
    args: list[str] = []
    workdir: str | None = None
    env_keys: list[str] = []
    poll_interval_seconds: int = Field(default=120, ge=10)

    def looks_expired(self, *, skew_seconds: int = 30) -> bool:
        if self.access_token_expires_at is None:
            return False
        return self.access_token_expires_at <= datetime.now(UTC) + timedelta(seconds=skew_seconds)


class LocalProfileStore(BaseModel):
    profiles: list[LocalAgentProfile] = []

    def upsert(self, profile: LocalAgentProfile) -> None:
        for index, existing in enumerate(self.profiles):
            if existing.agent_id == profile.agent_id:
                self.profiles[index] = profile
                return
        self.profiles.append(profile)

    def remove(self, identifier: str) -> LocalAgentProfile:
        resolved = self.resolve(identifier)
        self.profiles = [profile for profile in self.profiles if profile.agent_id != resolved.agent_id]
        return resolved

    def resolve(self, identifier: str | None = None) -> LocalAgentProfile:
        if identifier is None:
            if len(self.profiles) == 1:
                return self.profiles[0]
            raise ValueError("Multiple connected agents found. Pass --agent with an id or display name.")

        for profile in self.profiles:
            if str(profile.agent_id) == identifier or profile.display_name == identifier:
                return profile

        raise ValueError(f"No connected agent matches '{identifier}'")


def load_profiles() -> LocalProfileStore:
    path = profiles_path()
    if not path.exists():
        return LocalProfileStore()
    return LocalProfileStore.model_validate_json(path.read_text())


def save_profiles(store: LocalProfileStore) -> None:
    path = profiles_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store.model_dump(mode="json"), indent=2) + "\n")
