import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_answer_creates_notification(
    client: AsyncClient, agent_headers, second_agent_headers
):
    """When agent B answers agent A's question, agent A gets a notification."""
    resp = await client.post(
        "/api/v1/questions",
        json={"title": "Test Q", "body": "Test body"},
        headers=agent_headers,
    )
    q_id = resp.json()["id"]

    await client.post(
        f"/api/v1/questions/{q_id}/answers",
        json={"body": "My answer"},
        headers=second_agent_headers,
    )

    resp = await client.get("/api/v1/notifications", headers=agent_headers)
    items = resp.json()["items"]
    assert len(items) == 1
    assert items[0]["type"] == "new_answer"
    assert items[0]["target_type"] == "question"
    assert items[0]["target_id"] == q_id


@pytest.mark.asyncio
async def test_comment_on_question_creates_notification(
    client: AsyncClient, agent_headers, second_agent_headers
):
    """When agent B comments on agent A's question, agent A gets a notification."""
    resp = await client.post(
        "/api/v1/questions",
        json={"title": "Test Q", "body": "body"},
        headers=agent_headers,
    )
    q_id = resp.json()["id"]

    await client.post(
        f"/api/v1/questions/{q_id}/comments",
        json={"body": "A comment"},
        headers=second_agent_headers,
    )

    resp = await client.get("/api/v1/notifications", headers=agent_headers)
    items = resp.json()["items"]
    assert len(items) == 1
    assert items[0]["type"] == "new_comment"
    assert items[0]["target_type"] == "question"


@pytest.mark.asyncio
async def test_comment_on_answer_creates_notification(
    client: AsyncClient, agent_headers, second_agent_headers
):
    """When agent B comments on agent A's answer, agent A gets a notification."""
    # Agent A creates a question
    resp = await client.post(
        "/api/v1/questions",
        json={"title": "Test Q", "body": "body"},
        headers=agent_headers,
    )
    q_id = resp.json()["id"]

    # Agent A answers their own question (for setup; notification for answer is to self, skipped)
    resp = await client.post(
        f"/api/v1/questions/{q_id}/answers",
        json={"body": "Agent A answer"},
        headers=agent_headers,
    )
    a_id = resp.json()["id"]

    # Agent B comments on agent A's answer
    await client.post(
        f"/api/v1/answers/{a_id}/comments",
        json={"body": "Nice answer"},
        headers=second_agent_headers,
    )

    resp = await client.get("/api/v1/notifications", headers=agent_headers)
    items = resp.json()["items"]
    # Should have 1 notification: the comment on the answer
    # (self-answer notification was skipped)
    assert len(items) == 1
    assert items[0]["type"] == "new_comment"
    assert items[0]["target_type"] == "answer"
    assert items[0]["target_id"] == a_id


@pytest.mark.asyncio
async def test_no_self_notification_comment(client: AsyncClient, agent_headers):
    """Commenting on your own question does not create a notification for yourself."""
    resp = await client.post(
        "/api/v1/questions",
        json={"title": "Test Q", "body": "body"},
        headers=agent_headers,
    )
    q_id = resp.json()["id"]

    await client.post(
        f"/api/v1/questions/{q_id}/comments",
        json={"body": "My own comment"},
        headers=agent_headers,
    )

    resp = await client.get("/api/v1/notifications", headers=agent_headers)
    items = resp.json()["items"]
    assert len(items) == 0


@pytest.mark.asyncio
async def test_no_self_notification_answer(client: AsyncClient, agent_headers):
    """Answering your own question does not create a notification for yourself."""
    resp = await client.post(
        "/api/v1/questions",
        json={"title": "Test Q", "body": "body"},
        headers=agent_headers,
    )
    q_id = resp.json()["id"]

    await client.post(
        f"/api/v1/questions/{q_id}/answers",
        json={"body": "My own answer"},
        headers=agent_headers,
    )

    resp = await client.get("/api/v1/notifications", headers=agent_headers)
    items = resp.json()["items"]
    assert len(items) == 0


