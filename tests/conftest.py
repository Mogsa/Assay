from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

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
        # Drop SQL functions that drop_all won't handle
        await conn.execute(text("DROP INDEX IF EXISTS idx_questions_search"))
        await conn.execute(text("DROP INDEX IF EXISTS idx_questions_hot"))
        await conn.execute(text("DROP INDEX IF EXISTS idx_questions_open"))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.execute(text("DROP FUNCTION IF EXISTS hot_score(INT, INT, TIMESTAMP)"))
        await conn.execute(text("DROP FUNCTION IF EXISTS wilson_lower(INT, INT)"))

        # Create tables
        await conn.run_sync(Base.metadata.create_all)

        # Create SQL functions (not handled by create_all)
        await conn.execute(text("""
            CREATE OR REPLACE FUNCTION wilson_lower(up INT, down INT)
            RETURNS FLOAT LANGUAGE SQL IMMUTABLE STRICT AS $$
                SELECT CASE WHEN (up + down) = 0 THEN 0.0
                ELSE (
                    (up::float / (up + down)) + 1.9208 / (up + down)
                    - 1.96 * sqrt(
                        ((up::float / (up + down)) * (1.0 - (up::float / (up + down)))
                        + 0.9604 / (up + down)) / (up + down)
                    )
                ) / (1.0 + 3.8416 / (up + down))
                END
            $$;
        """))
        await conn.execute(text("""
            CREATE OR REPLACE FUNCTION hot_score(ups INT, downs INT, created TIMESTAMP)
            RETURNS FLOAT LANGUAGE SQL IMMUTABLE STRICT AS $$
                SELECT SIGN(ups - downs)
                    * LOG(GREATEST(ABS(ups - downs), 1))
                    + EXTRACT(EPOCH FROM created - '2025-01-01'::timestamp) / 45000.0
            $$;
        """))

        # Add generated search_vector column to questions
        await conn.execute(text("""
            ALTER TABLE questions ADD COLUMN IF NOT EXISTS search_vector tsvector
            GENERATED ALWAYS AS (
                setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
                setweight(to_tsvector('english', coalesce(body, '')), 'B')
            ) STORED;
        """))
        await conn.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_questions_search "
            "ON questions USING GIN (search_vector);"
        ))
    yield
    await test_engine.dispose()


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
