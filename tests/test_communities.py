import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_community(client: AsyncClient, agent_headers: dict):
    resp = await client.post(
        "/api/v1/communities",
        json={
            "name": "algorithms",
            "display_name": "Algorithms",
            "description": "Algorithm design and analysis",
        },
        headers=agent_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "algorithms"
    assert data["display_name"] == "Algorithms"
    assert data["member_count"] == 1


@pytest.mark.asyncio
async def test_human_session_can_create_community(
    client: AsyncClient,
    human_session_cookie: str,
):
    resp = await client.post(
        "/api/v1/communities",
        json={
            "name": "human-owned",
            "display_name": "Human Owned",
            "description": "Created via session auth",
        },
        cookies={"session": human_session_cookie},
    )
    assert resp.status_code == 201
    assert resp.json()["member_count"] == 1


@pytest.mark.asyncio
async def test_create_community_duplicate_name_returns_409(
    client: AsyncClient, agent_headers: dict
):
    payload = {
        "name": "ml",
        "display_name": "Machine Learning",
        "description": "ML topics",
    }
    await client.post("/api/v1/communities", json=payload, headers=agent_headers)
    resp = await client.post("/api/v1/communities", json=payload, headers=agent_headers)
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_create_community_invalid_name_returns_422(
    client: AsyncClient, agent_headers: dict
):
    resp = await client.post(
        "/api/v1/communities",
        json={
            "name": "Has Spaces!",
            "display_name": "Bad Name",
            "description": "test",
        },
        headers=agent_headers,
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_list_communities(client: AsyncClient, agent_headers: dict):
    for name in ["alpha", "beta", "gamma"]:
        await client.post(
            "/api/v1/communities",
            json={"name": name, "display_name": name.title(), "description": f"{name} community"},
            headers=agent_headers,
        )
    resp = await client.get("/api/v1/communities", headers=agent_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 3
    assert "has_more" in data


@pytest.mark.asyncio
async def test_list_communities_cursor_pagination(client: AsyncClient, agent_headers: dict):
    for i in range(3):
        await client.post(
            "/api/v1/communities",
            json={"name": f"page-{i}", "display_name": f"Page {i}", "description": "test"},
            headers=agent_headers,
        )
    resp1 = await client.get("/api/v1/communities?limit=2", headers=agent_headers)
    assert len(resp1.json()["items"]) == 2
    assert resp1.json()["has_more"] is True

    resp2 = await client.get(
        f"/api/v1/communities?limit=2&cursor={resp1.json()['next_cursor']}",
        headers=agent_headers,
    )
    assert len(resp2.json()["items"]) == 1
    assert resp2.json()["has_more"] is False


@pytest.mark.asyncio
async def test_get_community_detail(client: AsyncClient, agent_headers: dict):
    create_resp = await client.post(
        "/api/v1/communities",
        json={"name": "detail", "display_name": "Detail", "description": "test community"},
        headers=agent_headers,
    )
    community_id = create_resp.json()["id"]
    resp = await client.get(f"/api/v1/communities/{community_id}", headers=agent_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "detail"
    assert data["member_count"] == 1


@pytest.mark.asyncio
async def test_get_community_not_found(client: AsyncClient, agent_headers: dict):
    resp = await client.get(
        "/api/v1/communities/00000000-0000-0000-0000-000000000000",
        headers=agent_headers,
    )
    assert resp.status_code == 404


# --- Membership tests ---


@pytest.mark.asyncio
async def test_join_community(
    client: AsyncClient, agent_headers: dict, second_agent_headers: dict
):
    create_resp = await client.post(
        "/api/v1/communities",
        json={"name": "joinable", "display_name": "Joinable", "description": "test"},
        headers=agent_headers,
    )
    community_id = create_resp.json()["id"]
    resp = await client.post(
        f"/api/v1/communities/{community_id}/join",
        headers=second_agent_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["role"] == "subscriber"


@pytest.mark.asyncio
async def test_join_community_already_member_returns_409(
    client: AsyncClient, agent_headers: dict
):
    create_resp = await client.post(
        "/api/v1/communities",
        json={"name": "already", "display_name": "Already", "description": "test"},
        headers=agent_headers,
    )
    community_id = create_resp.json()["id"]
    resp = await client.post(
        f"/api/v1/communities/{community_id}/join",
        headers=agent_headers,
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_leave_community(
    client: AsyncClient, agent_headers: dict, second_agent_headers: dict
):
    create_resp = await client.post(
        "/api/v1/communities",
        json={"name": "leavable", "display_name": "Leavable", "description": "test"},
        headers=agent_headers,
    )
    community_id = create_resp.json()["id"]
    await client.post(f"/api/v1/communities/{community_id}/join", headers=second_agent_headers)
    resp = await client.delete(
        f"/api/v1/communities/{community_id}/leave",
        headers=second_agent_headers,
    )
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_owner_cannot_leave(client: AsyncClient, agent_headers: dict):
    create_resp = await client.post(
        "/api/v1/communities",
        json={"name": "owned", "display_name": "Owned", "description": "test"},
        headers=agent_headers,
    )
    community_id = create_resp.json()["id"]
    resp = await client.delete(
        f"/api/v1/communities/{community_id}/leave",
        headers=agent_headers,
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_list_members(
    client: AsyncClient, agent_headers: dict, second_agent_headers: dict
):
    create_resp = await client.post(
        "/api/v1/communities",
        json={"name": "members", "display_name": "Members", "description": "test"},
        headers=agent_headers,
    )
    community_id = create_resp.json()["id"]
    await client.post(f"/api/v1/communities/{community_id}/join", headers=second_agent_headers)
    resp = await client.get(
        f"/api/v1/communities/{community_id}/members",
        headers=agent_headers,
    )
    assert resp.status_code == 200
    assert len(resp.json()["members"]) == 2
    roles = {m["role"] for m in resp.json()["members"]}
    assert "owner" in roles
    assert "subscriber" in roles


@pytest.mark.asyncio
async def test_list_communities_invalid_cursor(client: AsyncClient, agent_headers: dict):
    resp = await client.get("/api/v1/communities?cursor=badcursor", headers=agent_headers)
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_join_nonexistent_community_returns_404(
    client: AsyncClient, agent_headers: dict
):
    resp = await client.post(
        "/api/v1/communities/00000000-0000-0000-0000-000000000000/join",
        headers=agent_headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_leave_not_a_member_returns_404(
    client: AsyncClient, agent_headers: dict, second_agent_headers: dict
):
    create_resp = await client.post(
        "/api/v1/communities",
        json={"name": "notjoined", "display_name": "Not Joined", "description": "test"},
        headers=agent_headers,
    )
    community_id = create_resp.json()["id"]
    resp = await client.delete(
        f"/api/v1/communities/{community_id}/leave",
        headers=second_agent_headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_members_nonexistent_community_returns_404(
    client: AsyncClient, agent_headers: dict
):
    resp = await client.get(
        "/api/v1/communities/00000000-0000-0000-0000-000000000000/members",
        headers=agent_headers,
    )
    assert resp.status_code == 404
