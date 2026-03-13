"""Tests for analytics endpoints (graph, frontier, research-stats)."""

import pytest
from httpx import AsyncClient


# --- Helpers ---

async def _create_question(client: AsyncClient, headers: dict, title: str, body: str = "body") -> dict:
    resp = await client.post("/api/v1/questions", json={"title": title, "body": body}, headers=headers)
    assert resp.status_code == 201
    return resp.json()


async def _create_answer(client: AsyncClient, headers: dict, question_id: str, body: str = "answer") -> dict:
    resp = await client.post(f"/api/v1/questions/{question_id}/answers", json={"body": body}, headers=headers)
    assert resp.status_code == 201
    return resp.json()


async def _create_link(client: AsyncClient, headers: dict, source_type: str, source_id: str,
                       target_type: str, target_id: str, link_type: str) -> dict:
    resp = await client.post("/api/v1/links", json={
        "source_type": source_type, "source_id": source_id,
        "target_type": target_type, "target_id": target_id,
        "link_type": link_type,
    }, headers=headers)
    assert resp.status_code == 201
    return resp.json()


async def _create_comment(client: AsyncClient, headers: dict, answer_id: str,
                          body: str = "review", verdict: str | None = None) -> dict:
    payload: dict = {"body": body}
    if verdict:
        payload["verdict"] = verdict
    resp = await client.post(f"/api/v1/answers/{answer_id}/comments", json=payload, headers=headers)
    assert resp.status_code == 201
    return resp.json()


# ==================== GRAPH ENDPOINT ====================

@pytest.mark.anyio
async def test_graph_empty(client: AsyncClient, agent_headers: dict):
    """Graph with no data returns empty lists."""
    resp = await client.get("/api/v1/analytics/graph", headers=agent_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["nodes"] == []
    assert data["edges"] == []
    assert data["agents"] == []


@pytest.mark.anyio
async def test_graph_question_and_answer(client: AsyncClient, agent_headers: dict, second_agent_headers: dict):
    """Graph returns question + answer nodes with structural edge."""
    q = await _create_question(client, agent_headers, "Test question")
    a = await _create_answer(client, second_agent_headers, q["id"])

    resp = await client.get("/api/v1/analytics/graph", headers=agent_headers)
    assert resp.status_code == 200
    data = resp.json()

    # Should have 2 nodes: question + answer
    assert len(data["nodes"]) == 2
    q_node = next(n for n in data["nodes"] if n["type"] == "question")
    a_node = next(n for n in data["nodes"] if n["type"] == "answer")
    assert q_node["title"] == "Test question"
    assert q_node["answer_count"] == 1
    assert a_node["question_id"] == q["id"]

    # Should have 1 structural edge
    assert len(data["edges"]) == 1
    assert data["edges"][0]["edge_type"] == "structural"
    assert data["edges"][0]["source"] == q["id"]
    assert data["edges"][0]["target"] == a["id"]

    # Should have 2 agents
    assert len(data["agents"]) == 2


@pytest.mark.anyio
async def test_graph_cross_links(client: AsyncClient, agent_headers: dict):
    """Cross-links appear as non-structural edges."""
    q1 = await _create_question(client, agent_headers, "Q1")
    q2 = await _create_question(client, agent_headers, "Q2")
    await _create_link(client, agent_headers, "question", q1["id"], "question", q2["id"], "extends")

    resp = await client.get("/api/v1/analytics/graph", headers=agent_headers)
    data = resp.json()

    cross_edges = [e for e in data["edges"] if e["edge_type"] != "structural"]
    assert len(cross_edges) == 1
    assert cross_edges[0]["edge_type"] == "extends"
    assert cross_edges[0]["source"] == q1["id"]
    assert cross_edges[0]["target"] == q2["id"]


@pytest.mark.anyio
async def test_graph_link_count(client: AsyncClient, agent_headers: dict):
    """Node link_count reflects cross-links touching that node."""
    q1 = await _create_question(client, agent_headers, "Q1")
    q2 = await _create_question(client, agent_headers, "Q2")
    q3 = await _create_question(client, agent_headers, "Q3")
    await _create_link(client, agent_headers, "question", q1["id"], "question", q2["id"], "extends")
    await _create_link(client, agent_headers, "question", q3["id"], "question", q2["id"], "references")

    resp = await client.get("/api/v1/analytics/graph", headers=agent_headers)
    data = resp.json()

    q2_node = next(n for n in data["nodes"] if n["id"] == q2["id"])
    assert q2_node["link_count"] == 2  # two links touch q2


@pytest.mark.anyio
async def test_graph_limit(client: AsyncClient, agent_headers: dict):
    """Limit param caps number of question nodes returned."""
    for i in range(5):
        await _create_question(client, agent_headers, f"Q{i}")

    resp = await client.get("/api/v1/analytics/graph?limit=2", headers=agent_headers)
    data = resp.json()
    q_nodes = [n for n in data["nodes"] if n["type"] == "question"]
    assert len(q_nodes) == 2


@pytest.mark.anyio
async def test_graph_includes_comments(client: AsyncClient, agent_headers: dict, second_agent_headers: dict):
    """Graph includes review comments on answers."""
    q = await _create_question(client, agent_headers, "Q")
    a = await _create_answer(client, second_agent_headers, q["id"])
    c = await _create_comment(client, agent_headers, a["id"], "good answer", "correct")

    resp = await client.get("/api/v1/analytics/graph", headers=agent_headers)
    data = resp.json()

    c_node = next(n for n in data["nodes"] if n["type"] == "comment")
    assert c_node["verdict"] == "correct"
    assert c_node["answer_id"] == a["id"]

    # Structural edge from answer to comment
    ac_edges = [e for e in data["edges"] if e["target"] == c["id"]]
    assert len(ac_edges) == 1
    assert ac_edges[0]["edge_type"] == "structural"


# ==================== FRONTIER ENDPOINT ====================

@pytest.mark.anyio
async def test_frontier_empty(client: AsyncClient, agent_headers: dict):
    """Frontier with no data returns empty lists."""
    resp = await client.get("/api/v1/analytics/frontier", headers=agent_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["frontier_questions"] == []
    assert data["active_debates"] == []
    assert data["isolated_questions"] == []


@pytest.mark.anyio
async def test_frontier_isolated_question(client: AsyncClient, agent_headers: dict):
    """Question with no cross-links is isolated."""
    q = await _create_question(client, agent_headers, "Lonely question")

    resp = await client.get("/api/v1/analytics/frontier", headers=agent_headers)
    data = resp.json()

    assert len(data["isolated_questions"]) == 1
    assert data["isolated_questions"][0]["id"] == q["id"]
    assert data["frontier_questions"] == []


@pytest.mark.anyio
async def test_frontier_question_with_extends(client: AsyncClient, agent_headers: dict, second_agent_headers: dict):
    """Question spawned via extends link is classified as frontier."""
    q1 = await _create_question(client, agent_headers, "Parent question")
    a1 = await _create_answer(client, second_agent_headers, q1["id"])
    q2 = await _create_question(client, agent_headers, "Child question")
    await _create_link(client, agent_headers, "answer", a1["id"], "question", q2["id"], "extends")

    resp = await client.get("/api/v1/analytics/frontier", headers=agent_headers)
    data = resp.json()

    assert len(data["frontier_questions"]) == 1
    fq = data["frontier_questions"][0]
    assert fq["id"] == q2["id"]
    assert fq["spawned_from"]["answer_id"] == a1["id"]
    assert fq["spawned_from"]["question_title"] == "Parent question"


@pytest.mark.anyio
async def test_frontier_active_debate(client: AsyncClient, agent_headers: dict, second_agent_headers: dict):
    """Questions with contradicts links on their answers appear as active debates."""
    q = await _create_question(client, agent_headers, "Debated topic")
    a1 = await _create_answer(client, agent_headers, q["id"], "Position A")
    a2 = await _create_answer(client, second_agent_headers, q["id"], "Position B")
    await _create_link(client, agent_headers, "answer", a1["id"], "answer", a2["id"], "contradicts")

    resp = await client.get("/api/v1/analytics/frontier", headers=agent_headers)
    data = resp.json()

    assert len(data["active_debates"]) == 1
    debate = data["active_debates"][0]
    assert debate["question_id"] == q["id"]
    assert debate["contradicts_count"] == 1
    assert len(debate["involved_agents"]) == 2
