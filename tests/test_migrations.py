from sqlalchemy import text


async def test_database_is_upgraded_to_current_head(client, db):
    version = await db.execute(text("SELECT version_num FROM alembic_version"))
    assert version.scalar_one() == "f7f8f1b7a2c4"

    signup_resp = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "migration-check@example.com",
            "password": "securepass123",
            "display_name": "MigrationCheck",
        },
    )
    session_cookie = signup_resp.cookies.get("session")

    register_resp = await client.post(
        "/api/v1/agents/register",
        json={
            "display_name": "MigratedAgent",
            "model_slug": "anthropic/claude-opus-4",
            "runtime_kind": "claude-cli",
        },
    )
    claim_resp = await client.post(
        f"/api/v1/agents/claim/{register_resp.json()['claim_token']}",
        cookies={"session": session_cookie},
    )
    assert claim_resp.status_code == 200
