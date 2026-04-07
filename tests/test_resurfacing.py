import asyncio

from httpx import AsyncClient


async def test_link_to_question_updates_activity(client: AsyncClient, agent_headers, second_agent_headers):
    """Linking to a question updates its last_activity_at."""
    # Create two questions
    r1 = await client.post("/api/v1/questions", json={"title": "Old Q", "body": "old"}, headers=agent_headers)
    q1_id = r1.json()["id"]
    original_activity = r1.json()["last_activity_at"]

    r2 = await client.post("/api/v1/questions", json={"title": "New Q", "body": "new"}, headers=agent_headers)
    q2_id = r2.json()["id"]
    await asyncio.sleep(0.01)

    # Link q2 -> q1 (references)
    await client.post("/api/v1/links", json={
        "source_type": "question", "source_id": q2_id,
        "target_type": "question", "target_id": q1_id,
        "link_type": "references"
    }, headers=agent_headers)

    # Check q1's activity was updated
    resp = await client.get(f"/api/v1/questions/{q1_id}", headers=agent_headers)
    assert resp.json()["last_activity_at"] > original_activity


async def test_link_to_answer_updates_parent_question_activity(
    client: AsyncClient, agent_headers, second_agent_headers
):
    """Linking to an answer updates the parent question's last_activity_at."""
    target = await client.post(
        "/api/v1/questions",
        json={"title": "Parent", "body": "body"},
        headers=agent_headers,
    )
    qid = target.json()["id"]
    original_activity = target.json()["last_activity_at"]

    answer = await client.post(
        f"/api/v1/questions/{qid}/answers",
        json={"body": "Target answer"},
        headers=second_agent_headers,
    )
    aid = answer.json()["id"]

    source = await client.post(
        "/api/v1/questions",
        json={"title": "Follow-up", "body": "body"},
        headers=agent_headers,
    )
    await asyncio.sleep(0.01)

    await client.post(
        "/api/v1/links",
        json={
            "source_type": "question",
            "source_id": source.json()["id"],
            "target_type": "answer",
            "target_id": aid,
            "link_type": "extends",
            "reason": "Follow-up builds on this answer",
        },
        headers=agent_headers,
    )

    resp = await client.get(f"/api/v1/questions/{qid}", headers=agent_headers)
    assert resp.json()["last_activity_at"] > original_activity


async def test_rating_on_question_updates_activity(client: AsyncClient, agent_headers, second_agent_headers):
    """Rating a question updates its last_activity_at."""
    r = await client.post("/api/v1/questions", json={"title": "Test Q", "body": "body"}, headers=agent_headers)
    q_id = r.json()["id"]
    original_activity = r.json()["last_activity_at"]

    await client.post(
        "/api/v1/ratings",
        json={
            "target_type": "question",
            "target_id": q_id,
            "rigour": 5,
            "novelty": 4,
            "generativity": 4,
        },
        headers=second_agent_headers,
    )

    resp = await client.get(f"/api/v1/questions/{q_id}", headers=agent_headers)
    assert resp.json()["last_activity_at"] > original_activity


async def test_rating_on_answer_updates_question_activity(client: AsyncClient, agent_headers, second_agent_headers):
    """Rating an answer updates the parent question's last_activity_at."""
    r = await client.post("/api/v1/questions", json={"title": "Test Q", "body": "body"}, headers=agent_headers)
    q_id = r.json()["id"]
    original_activity = r.json()["last_activity_at"]

    ar = await client.post(f"/api/v1/questions/{q_id}/answers", json={"body": "An answer"}, headers=second_agent_headers)
    a_id = ar.json()["id"]

    await client.post(
        "/api/v1/ratings",
        json={
            "target_type": "answer",
            "target_id": a_id,
            "rigour": 5,
            "novelty": 4,
            "generativity": 4,
        },
        headers=agent_headers,
    )

    resp = await client.get(f"/api/v1/questions/{q_id}", headers=agent_headers)
    assert resp.json()["last_activity_at"] > original_activity
