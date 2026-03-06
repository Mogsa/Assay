from sqlalchemy import text


async def test_database_is_upgraded_to_current_head(client, db):
    version = await db.execute(text("SELECT version_num FROM alembic_version"))
    assert version.scalar_one() == "8d95f1e1fbb7"

    signup_resp = await client.post(
        "/api/v1/auth/signup",
        json={
            "email": "migration-check@example.com",
            "password": "securepass123",
            "display_name": "MigrationCheck",
        },
    )
    session_cookie = signup_resp.cookies.get("session")

    start_resp = await client.post(
        "/api/v1/cli/device/start",
        json={
            "display_name": "MigratedAgent",
            "model_slug": "anthropic/claude-opus-4",
            "runtime_kind": "claude-cli",
            "provider_terms_acknowledged": True,
        },
    )
    assert start_resp.status_code == 201
    approve_resp = await client.post(
        "/api/v1/cli/device/approve",
        cookies={"session": session_cookie},
        json={"user_code": start_resp.json()["user_code"]},
    )
    assert approve_resp.status_code == 200
    poll_resp = await client.post(
        "/api/v1/cli/device/poll",
        json={"device_code": start_resp.json()["device_code"]},
    )
    assert poll_resp.status_code == 200
