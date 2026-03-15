from sqlalchemy import text


async def test_database_is_upgraded_to_current_head(client, db):
    version = await db.execute(text("SELECT version_num FROM alembic_version"))
    assert version.scalar_one() == "d2aed9fc3f02"

    signup_resp = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "migration-check@example.com",
            "password": "securepass123",
            "display_name": "MigrationCheck",
        },
    )
    session_cookie = signup_resp.cookies.get("session")

    create_resp = await client.post(
        "/api/v1/agents",
        cookies={"session": session_cookie},
        json={
            "display_name": "MigratedAgent",
            "model_slug": "anthropic/claude-opus-4-6",
            "runtime_kind": "claude-cli",
        },
    )
    assert create_resp.status_code == 201
