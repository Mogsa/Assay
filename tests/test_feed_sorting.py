from httpx import AsyncClient


async def test_feed_default_is_new(client: AsyncClient, agent_headers):
    """Default sort is newest first (ordered by created_at desc)."""
    for i in range(3):
        await client.post(
            "/api/v1/questions",
            json={"title": f"Q{i}", "body": f"body {i}"},
            headers=agent_headers,
        )

    resp = await client.get("/api/v1/questions", headers=agent_headers)
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) == 3
    # Verify descending order by created_at
    timestamps = [item["created_at"] for item in items]
    assert timestamps == sorted(timestamps, reverse=True)


async def test_feed_sort_new(client: AsyncClient, agent_headers):
    """Explicit sort=new returns results ordered by created_at desc."""
    for i in range(3):
        await client.post(
            "/api/v1/questions",
            json={"title": f"SortNew{i}", "body": "body"},
            headers=agent_headers,
        )

    resp = await client.get(
        "/api/v1/questions", params={"sort": "new"}, headers=agent_headers
    )
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) >= 3
    # Verify descending order by created_at
    timestamps = [item["created_at"] for item in items]
    assert timestamps == sorted(timestamps, reverse=True)


async def test_feed_sort_hot(client: AsyncClient, agent_headers, second_agent_headers):
    """Sort=hot returns results ordered by recency plus frontier score."""
    await client.post(
        "/api/v1/questions",
        json={"title": "Cold Q", "body": "no votes"},
        headers=agent_headers,
    )
    resp2 = await client.post(
        "/api/v1/questions",
        json={"title": "Hot Q", "body": "many votes"},
        headers=agent_headers,
    )
    hot_id = resp2.json()["id"]

    await client.post(
        "/api/v1/ratings",
        json={
            "target_type": "question",
            "target_id": hot_id,
            "rigour": 5,
            "novelty": 5,
            "generativity": 5,
        },
        headers=second_agent_headers,
    )

    resp = await client.get(
        "/api/v1/questions", params={"sort": "hot"}, headers=agent_headers
    )
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) == 2
    titles = {item["title"] for item in items}
    assert titles == {"Cold Q", "Hot Q"}
    assert items[0]["title"] == "Hot Q"


async def test_feed_sort_contested(client: AsyncClient, agent_headers):
    """Sort=contested returns results (rating variance sorting works)."""
    await client.post(
        "/api/v1/questions",
        json={"title": "Contested Q", "body": "body"},
        headers=agent_headers,
    )

    resp = await client.get(
        "/api/v1/questions", params={"sort": "contested"}, headers=agent_headers
    )
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert len(items) == 1


async def test_feed_invalid_sort(client: AsyncClient, agent_headers):
    """Invalid sort value returns 422."""
    resp = await client.get(
        "/api/v1/questions", params={"sort": "invalid"}, headers=agent_headers
    )
    assert resp.status_code == 422


async def test_feed_min_disagreement_filter(client: AsyncClient, agent_headers):
    """min_disagreement filters out questions with low disagreement_score."""
    await client.post(
        "/api/v1/questions",
        json={"title": "Quiet Q", "body": "body"},
        headers=agent_headers,
    )

    # All freshly created questions have disagreement_score = 0.0
    resp = await client.get(
        "/api/v1/questions",
        params={"sort": "contested", "min_disagreement": 0.5},
        headers=agent_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["items"] == []

    # min_disagreement = 0.0 returns everything
    resp = await client.get(
        "/api/v1/questions",
        params={"sort": "contested", "min_disagreement": 0.0},
        headers=agent_headers,
    )
    assert resp.status_code == 200
    assert len(resp.json()["items"]) >= 1


async def test_feed_exclude_rated_by_me_question_only(
    client: AsyncClient, agent_headers, second_agent_headers
):
    """exclude_rated_by_me hides questions where caller has rated the question itself."""
    q1 = await client.post(
        "/api/v1/questions",
        json={"title": "Will rate question", "body": "body"},
        headers=agent_headers,
    )
    await client.post(
        "/api/v1/questions",
        json={"title": "Will not rate", "body": "body"},
        headers=agent_headers,
    )

    # second_agent rates only q1 directly
    await client.post(
        "/api/v1/ratings",
        json={
            "target_type": "question",
            "target_id": q1.json()["id"],
            "rigour": 4,
            "novelty": 4,
            "generativity": 4,
        },
        headers=second_agent_headers,
    )

    # Without filter, second_agent sees both
    resp = await client.get("/api/v1/questions", headers=second_agent_headers)
    titles = {item["title"] for item in resp.json()["items"]}
    assert "Will rate question" in titles
    assert "Will not rate" in titles

    # With filter, second_agent sees only the unrated one
    resp = await client.get(
        "/api/v1/questions",
        params={"exclude_rated_by_me": "true"},
        headers=second_agent_headers,
    )
    titles = {item["title"] for item in resp.json()["items"]}
    assert "Will rate question" not in titles
    assert "Will not rate" in titles

    # Per-caller, not global: agent_headers (the asker) still sees both
    resp = await client.get(
        "/api/v1/questions",
        params={"exclude_rated_by_me": "true"},
        headers=agent_headers,
    )
    titles = {item["title"] for item in resp.json()["items"]}
    assert "Will rate question" in titles
    assert "Will not rate" in titles


async def test_feed_exclude_rated_by_me_via_answer(
    client: AsyncClient, agent_headers, second_agent_headers
):
    """exclude_rated_by_me hides a question if caller has rated any of its answers.

    Pins Option B semantics: rating an answer counts as engaging with the
    parent thread. Without this, regression to question-only would silently
    break the human review workflow.
    """
    q1 = await client.post(
        "/api/v1/questions",
        json={"title": "Has rated answer", "body": "body"},
        headers=agent_headers,
    )
    q1_id = q1.json()["id"]
    await client.post(
        "/api/v1/questions",
        json={"title": "Untouched", "body": "body"},
        headers=agent_headers,
    )

    # asker posts an answer to q1
    ans = await client.post(
        f"/api/v1/questions/{q1_id}/answers",
        json={"body": "An answer"},
        headers=agent_headers,
    )
    aid = ans.json()["id"]

    # second_agent rates the ANSWER, not the question
    await client.post(
        "/api/v1/ratings",
        json={
            "target_type": "answer",
            "target_id": aid,
            "rigour": 5,
            "novelty": 5,
            "generativity": 5,
        },
        headers=second_agent_headers,
    )

    # With filter, second_agent should not see q1 (rated an answer in its thread)
    resp = await client.get(
        "/api/v1/questions",
        params={"exclude_rated_by_me": "true"},
        headers=second_agent_headers,
    )
    titles = {item["title"] for item in resp.json()["items"]}
    assert "Has rated answer" not in titles
    assert "Untouched" in titles
