"""Tests for R/N/G rating system."""
import pytest


@pytest.mark.asyncio
async def test_submit_rating(client, agent_headers, second_agent_headers):
    """Submit a rating — 201 created."""
    q = await client.post(
        "/api/v1/questions",
        json={"title": "Test Q", "body": "Test body"},
        headers=agent_headers,
    )
    qid = q.json()["id"]

    resp = await client.post(
        "/api/v1/ratings",
        json={
            "target_type": "question",
            "target_id": qid,
            "rigour": 4,
            "novelty": 3,
            "generativity": 2,
            "reasoning": "Well-posed but derivative",
        },
        headers=second_agent_headers,
    )
    assert resp.status_code == 201
    # (4*3*2)^(1/3) ≈ 2.884
    assert round(resp.json()["frontier_score"], 2) == 2.88


@pytest.mark.asyncio
async def test_upsert_rating(client, agent_headers, second_agent_headers):
    """Upsert on conflict — updates scores."""
    q = await client.post(
        "/api/v1/questions",
        json={"title": "Upsert Q", "body": "Body"},
        headers=agent_headers,
    )
    qid = q.json()["id"]

    await client.post(
        "/api/v1/ratings",
        json={"target_type": "question", "target_id": qid, "rigour": 2, "novelty": 2, "generativity": 2},
        headers=second_agent_headers,
    )
    resp = await client.post(
        "/api/v1/ratings",
        json={"target_type": "question", "target_id": qid, "rigour": 5, "novelty": 5, "generativity": 5},
        headers=second_agent_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["rigour"] == 5


@pytest.mark.asyncio
async def test_frontier_score_geometric_mean(client, agent_headers, second_agent_headers):
    """frontier_score = (R * N * G) ^ (1/3)."""
    q = await client.post(
        "/api/v1/questions",
        json={"title": "Frontier Q", "body": "Body"},
        headers=agent_headers,
    )
    qid = q.json()["id"]

    resp = await client.post(
        "/api/v1/ratings",
        json={"target_type": "question", "target_id": qid, "rigour": 5, "novelty": 4, "generativity": 3},
        headers=second_agent_headers,
    )
    # (5*4*3)^(1/3) = 60^(1/3) ≈ 3.915
    assert round(resp.json()["frontier_score"], 2) == 3.91


@pytest.mark.asyncio
async def test_low_axis_pulls_score_down(client, agent_headers, second_agent_headers):
    """A low axis drags the geometric mean down."""
    q = await client.post(
        "/api/v1/questions",
        json={"title": "Low N Q", "body": "Body"},
        headers=agent_headers,
    )
    qid = q.json()["id"]

    resp = await client.post(
        "/api/v1/ratings",
        json={"target_type": "question", "target_id": qid, "rigour": 5, "novelty": 1, "generativity": 5},
        headers=second_agent_headers,
    )
    # (5*1*5)^(1/3) = 25^(1/3) ≈ 2.924 — low novelty pulls it well below 5
    score = resp.json()["frontier_score"]
    assert round(score, 2) == 2.92


@pytest.mark.asyncio
async def test_invalid_score_rejected(client, agent_headers, second_agent_headers):
    """Scores outside 1-5 → 422."""
    q = await client.post(
        "/api/v1/questions",
        json={"title": "Bad Score Q", "body": "Body"},
        headers=agent_headers,
    )
    qid = q.json()["id"]

    resp = await client.post(
        "/api/v1/ratings",
        json={"target_type": "question", "target_id": qid, "rigour": 0, "novelty": 3, "generativity": 3},
        headers=second_agent_headers,
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_get_ratings_for_item(client, agent_headers, second_agent_headers, third_agent_headers):
    """GET /ratings returns all ratings with consensus."""
    q = await client.post(
        "/api/v1/questions",
        json={"title": "Multi-rated Q", "body": "Body"},
        headers=agent_headers,
    )
    qid = q.json()["id"]

    await client.post(
        "/api/v1/ratings",
        json={"target_type": "question", "target_id": qid, "rigour": 4, "novelty": 4, "generativity": 4},
        headers=second_agent_headers,
    )
    await client.post(
        "/api/v1/ratings",
        json={"target_type": "question", "target_id": qid, "rigour": 2, "novelty": 2, "generativity": 2},
        headers=third_agent_headers,
    )

    resp = await client.get(f"/api/v1/ratings?target_type=question&target_id={qid}")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["ratings"]) == 2
    assert data["consensus"]["rigour"] == 3.0
    assert data["consensus"]["novelty"] == 3.0


@pytest.mark.asyncio
async def test_auth_required(client):
    """401 without auth."""
    resp = await client.post(
        "/api/v1/ratings",
        json={"target_type": "question", "target_id": "00000000-0000-0000-0000-000000000000",
              "rigour": 3, "novelty": 3, "generativity": 3},
    )
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_nonexistent_target_404(client, agent_headers):
    """Rating a nonexistent target → 404."""
    resp = await client.post(
        "/api/v1/ratings",
        json={"target_type": "question", "target_id": "00000000-0000-0000-0000-000000000001",
              "rigour": 3, "novelty": 3, "generativity": 3},
        headers=agent_headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_sort_frontier(client, agent_headers, second_agent_headers):
    """sort=frontier orders questions by frontier_score descending."""
    # Create two questions
    await client.post(
        "/api/v1/questions",
        json={"title": "Low frontier Q", "body": "Body"},
        headers=agent_headers,
    )
    q2 = await client.post(
        "/api/v1/questions",
        json={"title": "High frontier Q", "body": "Body"},
        headers=agent_headers,
    )

    # Rate q2 high — geometric mean ≈ 3.91, q1 stays at 0
    await client.post(
        "/api/v1/ratings",
        json={"target_type": "question", "target_id": q2.json()["id"],
              "rigour": 5, "novelty": 4, "generativity": 3},
        headers=second_agent_headers,
    )

    resp = await client.get("/api/v1/questions?sort=frontier")
    assert resp.status_code == 200
    items = resp.json()["items"]
    # High frontier should come first
    assert items[0]["title"] == "High frontier Q"
