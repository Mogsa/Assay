"""Tests for the /api/v1/analytics/arcs endpoint."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_arcs_empty(client: AsyncClient) -> None:
    """Empty DB returns empty arcs list."""
    resp = await client.get("/api/v1/analytics/arcs")
    assert resp.status_code == 200
    data = resp.json()
    assert data["arcs"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_arcs_single_thread(
    client: AsyncClient,
    agent_headers: dict[str, str],
) -> None:
    """A question with an extends link forms a single arc."""
    q1 = await client.post(
        "/api/v1/questions",
        json={"title": "Root question", "body": "Root body"},
        headers=agent_headers,
    )
    assert q1.status_code == 201
    q1_id = q1.json()["id"]

    q2 = await client.post(
        "/api/v1/questions",
        json={"title": "Child question", "body": "Extends root"},
        headers=agent_headers,
    )
    assert q2.status_code == 201
    q2_id = q2.json()["id"]

    link_resp = await client.post(
        "/api/v1/links",
        json={
            "source_type": "question",
            "source_id": q2_id,
            "target_type": "question",
            "target_id": q1_id,
            "link_type": "extends",
            "reason": "builds on root",
        },
        headers=agent_headers,
    )
    assert link_resp.status_code == 201

    resp = await client.get("/api/v1/analytics/arcs")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1

    arc = data["arcs"][0]
    assert arc["root_question_id"] == q1_id
    assert arc["breadth"] == 2
    assert arc["depth"] >= 1
    assert arc["extends_count"] == 1


@pytest.mark.asyncio
async def test_arcs_with_contradicts(
    client: AsyncClient,
    agent_headers: dict[str, str],
    second_agent_headers: dict[str, str],
) -> None:
    """Contradicts links mark an arc as contested and boost engagement."""
    q1 = await client.post(
        "/api/v1/questions",
        json={"title": "Claim A", "body": "Position A"},
        headers=agent_headers,
    )
    q1_id = q1.json()["id"]

    q2 = await client.post(
        "/api/v1/questions",
        json={"title": "Claim B", "body": "Position B"},
        headers=second_agent_headers,
    )
    q2_id = q2.json()["id"]

    await client.post(
        "/api/v1/links",
        json={
            "source_type": "question",
            "source_id": q2_id,
            "target_type": "question",
            "target_id": q1_id,
            "link_type": "contradicts",
            "reason": "B contradicts A because...",
        },
        headers=second_agent_headers,
    )

    resp = await client.get("/api/v1/analytics/arcs")
    data = resp.json()
    arc = data["arcs"][0]
    assert arc["contradicts_count"] == 1
    assert arc["lifecycle"] == "contested"
