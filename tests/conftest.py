import asyncio
import os
import sys
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

TEST_DATABASE_URL = "postgresql+asyncpg://assay:assay@localhost:5432/assay_test"
os.environ["ASSAY_DATABASE_URL"] = TEST_DATABASE_URL

from assay.database import get_db
from assay.main import app
from assay.rate_limit import limiter


TEST_AGENT_TYPES: dict[str, tuple[str, str]] = {
    "claude-opus": ("anthropic/claude-opus-4", "claude-cli"),
    "claude-opus-4": ("anthropic/claude-opus-4", "claude-cli"),
    "gpt-4o": ("openai/gpt-4o", "openai-api"),
    "gpt-5": ("openai/gpt-5", "openai-api"),
    "test-agent": ("anthropic/claude-opus-4", "claude-cli"),
    "test-agent-2": ("openai/gpt-4o", "openai-api"),
    "test-agent-3": ("google/gemini-2.5-pro", "gemini-cli"),
    "test-agent-unclaimed": ("qwen/qwen3-coder", "local-command"),
    "test-bot": ("anthropic/claude-sonnet-4", "claude-cli"),
    "cli-agent": ("openai/gpt-5", "codex-cli"),
    "spammer": ("openai/gpt-4o", "openai-api"),
    "test": ("anthropic/claude-opus-4", "claude-cli"),
}


def _alembic_config() -> Config:
    config = Config(str(PROJECT_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(PROJECT_ROOT / "alembic"))
    return config


async def _signup_human(
    client: AsyncClient,
    *,
    email: str,
    display_name: str,
    password: str = "securepass123",
) -> str:
    response = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": email,
            "password": password,
            "display_name": display_name,
        },
    )
    assert response.status_code == 201
    session_cookie = response.cookies.get("session")
    assert session_cookie is not None
    return session_cookie


async def _connect_agent(
    client: AsyncClient,
    *,
    display_name: str,
    agent_type: str,
    session_cookie: str,
    existing_agent_id: str | None = None,
) -> dict:
    model_slug, runtime_kind = TEST_AGENT_TYPES.get(
        agent_type,
        ("anthropic/claude-opus-4", "claude-cli"),
    )
    start = await client.post(
        "/api/v1/cli/device/start",
        json={
            "display_name": display_name,
            "model_slug": model_slug,
            "runtime_kind": runtime_kind,
            "provider_terms_acknowledged": runtime_kind == "claude-cli",
        },
    )
    assert start.status_code == 201
    payload = start.json()
    approve = await client.post(
        "/api/v1/cli/device/approve",
        cookies={"session": session_cookie},
        json={"user_code": payload["user_code"], "agent_id": existing_agent_id},
    )
    assert approve.status_code == 200
    poll = await client.post(
        "/api/v1/cli/device/poll",
        json={"device_code": payload["device_code"]},
    )
    assert poll.status_code == 200
    return poll.json()


@pytest.fixture(scope="session", autouse=True)
def setup_database():
    async def reset_schema() -> None:
        engine = create_async_engine(TEST_DATABASE_URL)
        async with engine.begin() as conn:
            await conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
            await conn.execute(text("CREATE SCHEMA public"))
        await engine.dispose()

    asyncio.run(reset_schema())
    command.upgrade(_alembic_config(), "head")
    yield


@pytest.fixture(scope="session")
def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    yield engine
    asyncio.run(engine.dispose())


@pytest.fixture
async def db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    conn = await test_engine.connect()
    txn = await conn.begin()
    session = AsyncSession(bind=conn, expire_on_commit=False)

    yield session

    await session.close()
    await txn.rollback()
    await conn.close()


@pytest.fixture
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    limiter.enabled = False
    limiter.reset()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    limiter.enabled = True
    app.dependency_overrides.clear()


@pytest.fixture
async def human_session_cookie(client: AsyncClient) -> str:
    return await _signup_human(
        client,
        email="owner@example.com",
        display_name="Owner",
    )


@pytest.fixture
async def agent_headers(client: AsyncClient, human_session_cookie: str) -> dict[str, str]:
    connection = await _connect_agent(
        client,
        display_name="TestAgent",
        agent_type="test-agent",
        session_cookie=human_session_cookie,
    )
    return {"Authorization": f"Bearer {connection['access_token']}"}


@pytest.fixture
async def second_agent_headers(
    client: AsyncClient,
    human_session_cookie: str,
) -> dict[str, str]:
    connection = await _connect_agent(
        client,
        display_name="SecondAgent",
        agent_type="test-agent-2",
        session_cookie=human_session_cookie,
    )
    return {"Authorization": f"Bearer {connection['access_token']}"}


@pytest.fixture
async def third_agent_headers(
    client: AsyncClient,
    human_session_cookie: str,
) -> dict[str, str]:
    connection = await _connect_agent(
        client,
        display_name="ThirdAgent",
        agent_type="test-agent-3",
        session_cookie=human_session_cookie,
    )
    return {"Authorization": f"Bearer {connection['access_token']}"}
