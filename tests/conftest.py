from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from assay.database import Base, get_db
from assay.main import app
from assay.models import *  # noqa: F401, F403

TEST_DATABASE_URL = "postgresql+asyncpg://assay:assay@localhost:5432/assay_test"


@pytest.fixture(scope="session")
def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    yield engine


@pytest.fixture(scope="session", autouse=True)
async def setup_database(test_engine):
    """Create all tables in test database once per session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    await test_engine.dispose()


@pytest.fixture
async def db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Fresh database session per test — rolls back transaction after."""
    conn = await test_engine.connect()
    txn = await conn.begin()
    session = AsyncSession(bind=conn, expire_on_commit=False)

    yield session

    await session.close()
    await txn.rollback()
    await conn.close()


@pytest.fixture
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """HTTP test client with database dependency override."""

    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


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
