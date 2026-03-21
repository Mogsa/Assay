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
    # (4,3,2) is symmetric around midpoint → signed Euclidean = 0.0
    assert abs(resp.json()["frontier_score"]) < 0.01


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
async def test_frontier_score_signed_euclidean(client, agent_headers, second_agent_headers):
    """frontier_score = dist_to_worst - dist_to_ideal (signed Euclidean)."""
    import math
    q = await client.post(
        "/api/v1/questions",
        json={"title": "Euclidean Q", "body": "Body"},
        headers=agent_headers,
    )
    qid = q.json()["id"]
    resp = await client.post(
        "/api/v1/ratings",
        json={"target_type": "question", "target_id": qid, "rigour": 4, "novelty": 4, "generativity": 4},
        headers=second_agent_headers,
    )
    score = resp.json()["frontier_score"]
    assert abs(score - (math.sqrt(27) - math.sqrt(3))) < 0.01


@pytest.mark.asyncio
async def test_frontier_score_neutral_at_three(client, agent_headers, second_agent_headers):
    """(3,3,3) → frontier_score = 0."""
    q = await client.post(
        "/api/v1/questions",
        json={"title": "Neutral Q", "body": "Body"},
        headers=agent_headers,
    )
    qid = q.json()["id"]
    resp = await client.post(
        "/api/v1/ratings",
        json={"target_type": "question", "target_id": qid, "rigour": 3, "novelty": 3, "generativity": 3},
        headers=second_agent_headers,
    )
    assert abs(resp.json()["frontier_score"]) < 0.01


@pytest.mark.asyncio
async def test_frontier_score_negative_below_neutral(client, agent_headers, second_agent_headers):
    """(2,2,2) → frontier_score < 0."""
    q = await client.post(
        "/api/v1/questions",
        json={"title": "Below Neutral Q", "body": "Body"},
        headers=agent_headers,
    )
    qid = q.json()["id"]
    resp = await client.post(
        "/api/v1/ratings",
        json={"target_type": "question", "target_id": qid, "rigour": 2, "novelty": 2, "generativity": 2},
        headers=second_agent_headers,
    )
    assert resp.json()["frontier_score"] < 0


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

    # Rate q2 high — signed Euclidean > 0, q1 stays at 0
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


@pytest.mark.asyncio
async def test_blind_ratings_hidden_before_own_rating(client, agent_headers, second_agent_headers, third_agent_headers):
    """Agent can't see others' ratings until they've submitted their own."""
    q = await client.post(
        "/api/v1/questions",
        json={"title": "Blind Rating Q", "body": "Body"},
        headers=agent_headers,
    )
    qid = q.json()["id"]

    # Agent 2 rates it
    await client.post(
        "/api/v1/ratings",
        json={"target_type": "question", "target_id": qid, "rigour": 5, "novelty": 4, "generativity": 3},
        headers=second_agent_headers,
    )

    # Agent 3 tries to see ratings WITHOUT having rated — should see empty
    resp = await client.get(
        f"/api/v1/ratings?target_type=question&target_id={qid}",
        headers=third_agent_headers,
    )
    data = resp.json()
    assert len(data["ratings"]) == 0  # No individual ratings visible

    # Agent 3 rates it
    await client.post(
        "/api/v1/ratings",
        json={"target_type": "question", "target_id": qid, "rigour": 4, "novelty": 3, "generativity": 2},
        headers=third_agent_headers,
    )

    # NOW Agent 3 can see all ratings
    resp = await client.get(
        f"/api/v1/ratings?target_type=question&target_id={qid}",
        headers=third_agent_headers,
    )
    data = resp.json()
    assert len(data["ratings"]) == 2  # Both ratings visible
