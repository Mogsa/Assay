import asyncio
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from assay.database import Base, get_db
from assay.main import app
from assay.models import *  # noqa: F401, F403

TEST_DATABASE_URL = "postgresql+asyncpg://assay:assay@localhost:5432/assay_test"
ALEMBIC_INI_PATH = Path(__file__).resolve().parents[1] / "alembic.ini"


def _make_alembic_config(database_url: str) -> Config:
    config = Config(str(ALEMBIC_INI_PATH))
    config.set_main_option("sqlalchemy.url", database_url)
    return config


async def _reset_public_schema(database_url: str) -> None:
    engine = create_async_engine(database_url)
    try:
        async with engine.begin() as conn:
            await conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
            await conn.execute(text("CREATE SCHEMA public"))
    finally:
        await engine.dispose()


@pytest.fixture(scope="session")
def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    yield engine


@pytest.fixture(scope="session", autouse=True)
def setup_database(test_engine):
    """Recreate the test schema from Alembic migrations once per session."""
    asyncio.run(_reset_public_schema(TEST_DATABASE_URL))
    command.upgrade(_make_alembic_config(TEST_DATABASE_URL), "head")
    yield
    asyncio.run(test_engine.dispose())


@pytest.fixture
async def session_factory(test_engine):
    """Create request-scoped sessions against the test database."""
    return async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture
async def client(session_factory) -> AsyncGenerator[AsyncClient, None]:
    """HTTP test client with request-scoped database sessions."""

    async def override_get_db():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
async def clean_database(test_engine):
    """Keep tests isolated even when handlers commit their own transactions."""
    yield
    async with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(text(f'TRUNCATE TABLE "{table.name}" CASCADE'))


@pytest.fixture
async def agent_headers(client: AsyncClient) -> dict[str, str]:
    """Register an agent and return auth headers."""
    resp = await client.post(
        "/api/v1/agents/register",
        json={
            "display_name": "TestAgent",
            "agent_type": "test-agent",
        },
    )
    return {"Authorization": f"Bearer {resp.json()['api_key']}"}


@pytest.fixture
async def second_agent_headers(client: AsyncClient) -> dict[str, str]:
    """Register a second agent for multi-agent tests."""
    resp = await client.post(
        "/api/v1/agents/register",
        json={
            "display_name": "SecondAgent",
            "agent_type": "test-agent-2",
        },
    )
    return {"Authorization": f"Bearer {resp.json()['api_key']}"}


@pytest.fixture
async def third_agent_headers(client: AsyncClient) -> dict[str, str]:
    """Register a third agent for permission tests."""
    resp = await client.post(
        "/api/v1/agents/register",
        json={
            "display_name": "ThirdAgent",
            "agent_type": "test-agent-3",
        },
    )
    return {"Authorization": f"Bearer {resp.json()['api_key']}"}
