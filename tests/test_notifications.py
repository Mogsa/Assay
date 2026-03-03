import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from assay.models.notification import Notification


@pytest.fixture
async def create_notification(session_factory: async_sessionmaker[AsyncSession]):
    """Insert a notification directly for testing."""

    async def _create(agent_id: uuid.UUID, **kwargs) -> Notification:
        async with session_factory() as session:
            notif = Notification(agent_id=agent_id, **kwargs)
            session.add(notif)
            await session.commit()
            await session.refresh(notif)
            return notif

    return _create


async def _register_agent(client: AsyncClient, name: str = "TestAgent") -> tuple[uuid.UUID, dict[str, str]]:
    """Register an agent, return (agent_id, headers)."""
    resp = await client.post(
        "/api/v1/agents/register",
        json={"display_name": name, "agent_type": "test-agent"},
    )
    data = resp.json()
    return uuid.UUID(data["agent_id"]), {"Authorization": f"Bearer {data['api_key']}"}


async def test_list_notifications(client: AsyncClient, create_notification):
    agent_id, headers = await _register_agent(client, "ListAgent")
    target_id = uuid.uuid4()

    await create_notification(
        agent_id,
        type="new_answer",
        target_type="question",
        target_id=target_id,
        preview="Someone answered your question",
    )
    await create_notification(
        agent_id,
        type="vote",
        target_type="answer",
        target_id=target_id,
        preview="Your answer got an upvote",
    )

    resp = await client.get("/api/v1/notifications", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["items"]) == 2
    assert body["has_more"] is False
    assert body["next_cursor"] is None
    # Most recent first
    assert body["items"][0]["type"] == "vote"
    assert body["items"][1]["type"] == "new_answer"


async def test_list_unread_only(client: AsyncClient, create_notification):
    agent_id, headers = await _register_agent(client, "UnreadAgent")
    target_id = uuid.uuid4()

    await create_notification(
        agent_id,
        type="new_answer",
        target_type="question",
        target_id=target_id,
        is_read=True,
    )
    await create_notification(
        agent_id,
        type="new_comment",
        target_type="question",
        target_id=target_id,
        is_read=False,
    )

    resp = await client.get(
        "/api/v1/notifications", headers=headers, params={"unread_only": "true"}
    )
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["type"] == "new_comment"
    assert body["items"][0]["is_read"] is False


async def test_mark_notification_read(client: AsyncClient, create_notification):
    agent_id, headers = await _register_agent(client, "ReadAgent")
    target_id = uuid.uuid4()

    notif = await create_notification(
        agent_id,
        type="verdict",
        target_type="answer",
        target_id=target_id,
    )

    resp = await client.put(
        f"/api/v1/notifications/{notif.id}/read", headers=headers
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["is_read"] is True
    assert body["id"] == str(notif.id)


async def test_mark_all_read(client: AsyncClient, create_notification):
    agent_id, headers = await _register_agent(client, "ReadAllAgent")
    target_id = uuid.uuid4()

    await create_notification(
        agent_id, type="new_answer", target_type="question", target_id=target_id,
    )
    await create_notification(
        agent_id, type="vote", target_type="answer", target_id=target_id,
    )
    await create_notification(
        agent_id, type="new_comment", target_type="question", target_id=target_id,
        is_read=True,
    )

    resp = await client.post("/api/v1/notifications/read-all", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["updated_count"] == 2

    # Verify all are read now
    resp2 = await client.get(
        "/api/v1/notifications", headers=headers, params={"unread_only": "true"}
    )
    assert len(resp2.json()["items"]) == 0


async def test_notifications_require_auth(client: AsyncClient):
    resp = await client.get("/api/v1/notifications")
    assert resp.status_code in (401, 403)

    resp2 = await client.put(f"/api/v1/notifications/{uuid.uuid4()}/read")
    assert resp2.status_code in (401, 403)

    resp3 = await client.post("/api/v1/notifications/read-all")
    assert resp3.status_code in (401, 403)


async def test_cannot_read_others_notification(client: AsyncClient, create_notification):
    agent_a_id, _ = await _register_agent(client, "AgentA")
    _, agent_b_headers = await _register_agent(client, "AgentB")
    target_id = uuid.uuid4()

    notif = await create_notification(
        agent_a_id,
        type="new_answer",
        target_type="question",
        target_id=target_id,
    )

    # Agent B tries to mark Agent A's notification as read
    resp = await client.put(
        f"/api/v1/notifications/{notif.id}/read", headers=agent_b_headers
    )
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Not your notification"
