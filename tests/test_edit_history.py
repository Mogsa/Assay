import pytest
from httpx import AsyncClient


async def _create_question(client: AsyncClient, headers: dict) -> str:
    resp = await client.post(
        "/api/v1/questions",
        json={"title": "Original", "body": "Original body"},
        headers=headers,
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def _create_answer(client: AsyncClient, question_id: str, headers: dict) -> str:
    resp = await client.post(
        f"/api/v1/questions/{question_id}/answers",
        json={"body": "Original answer"},
        headers=headers,
    )
    assert resp.status_code == 201
    return resp.json()["id"]


async def test_edit_question_title(client: AsyncClient, agent_headers: dict):
    question_id = await _create_question(client, agent_headers)

    resp = await client.put(
        f"/api/v1/questions/{question_id}",
        json={"title": "Updated Title"},
        headers=agent_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Updated Title"
    assert data["body"] == "Original body"


async def test_edit_question_body(client: AsyncClient, agent_headers: dict):
    question_id = await _create_question(client, agent_headers)

    resp = await client.put(
        f"/api/v1/questions/{question_id}",
        json={"body": "Updated body"},
        headers=agent_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["title"] == "Original"
    assert data["body"] == "Updated body"


async def test_edit_question_unauthorized(
    client: AsyncClient, agent_headers: dict, second_agent_headers: dict
):
    question_id = await _create_question(client, agent_headers)

    resp = await client.put(
        f"/api/v1/questions/{question_id}",
        json={"title": "Hijacked"},
        headers=second_agent_headers,
    )
    assert resp.status_code == 403


async def test_edit_history_recorded(client: AsyncClient, agent_headers: dict):
    question_id = await _create_question(client, agent_headers)

    # Edit title
    await client.put(
        f"/api/v1/questions/{question_id}",
        json={"title": "New Title"},
        headers=agent_headers,
    )

    # Edit body
    await client.put(
        f"/api/v1/questions/{question_id}",
        json={"body": "New body"},
        headers=agent_headers,
    )

    resp = await client.get(
        f"/api/v1/questions/{question_id}/history",
        headers=agent_headers,
    )
    assert resp.status_code == 200
    entries = resp.json()
    assert len(entries) == 2

    title_entry = entries[0]
    assert title_entry["field_name"] == "title"
    assert title_entry["old_value"] == "Original"
    assert title_entry["new_value"] == "New Title"
    assert title_entry["target_type"] == "question"

    body_entry = entries[1]
    assert body_entry["field_name"] == "body"
    assert body_entry["old_value"] == "Original body"
    assert body_entry["new_value"] == "New body"


async def test_edit_answer(client: AsyncClient, agent_headers: dict):
    question_id = await _create_question(client, agent_headers)
    answer_id = await _create_answer(client, question_id, agent_headers)

    resp = await client.put(
        f"/api/v1/answers/{answer_id}",
        json={"body": "Updated answer"},
        headers=agent_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["body"] == "Updated answer"


async def test_edit_answer_unauthorized(
    client: AsyncClient, agent_headers: dict, second_agent_headers: dict
):
    question_id = await _create_question(client, agent_headers)
    answer_id = await _create_answer(client, question_id, agent_headers)

    resp = await client.put(
        f"/api/v1/answers/{answer_id}",
        json={"body": "Hijacked answer"},
        headers=second_agent_headers,
    )
    assert resp.status_code == 403
