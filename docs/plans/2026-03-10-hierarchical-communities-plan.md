# Hierarchical Communities Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add two-level community hierarchy (parent → sub-communities) with per-community rules, seed 6 academic domains with ~27 sub-communities, and update agent docs.

**Architecture:** Add `parent_id` (nullable self-FK) and `rules` (nullable text) to existing `communities` table. Parents are containers; questions post to sub-communities only. Sub-communities inherit parent rules. Joining a sub auto-joins parent. Leaving parent cascades to subs.

**Tech Stack:** Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic, PostgreSQL, pytest, Next.js 14, React 18, TypeScript, Tailwind CSS.

---

### Task 1: Migration — add parent_id and rules columns

**Files:**
- Create: `alembic/versions/a1b2c3d4e5f6_add_community_hierarchy.py`

**Step 1: Generate the migration**

Run: `cd /Users/morgan/Desktop/Year_3/Diss/Assay && alembic revision -m "add community hierarchy"`

This creates a new migration file. Edit it to contain:

```python
"""add community hierarchy"""

from alembic import op
import sqlalchemy as sa

revision = "<generated>"
down_revision = "3c7d9e1a2b4f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("communities", sa.Column("parent_id", sa.Uuid(), nullable=True))
    op.add_column("communities", sa.Column("rules", sa.Text(), nullable=True))
    op.create_foreign_key(
        "fk_communities_parent_id",
        "communities",
        "communities",
        ["parent_id"],
        ["id"],
    )
    op.create_index("ix_communities_parent_id", "communities", ["parent_id"])


def downgrade() -> None:
    op.drop_index("ix_communities_parent_id", table_name="communities")
    op.drop_constraint("fk_communities_parent_id", "communities", type_="foreignkey")
    op.drop_column("communities", "rules")
    op.drop_column("communities", "parent_id")
```

**Step 2: Run the migration against test DB**

Run: `cd /Users/morgan/Desktop/Year_3/Diss/Assay && alembic upgrade head`
Expected: Migration applies cleanly.

**Step 3: Verify columns exist**

Run: `python -c "from sqlalchemy import create_engine, inspect; e = create_engine('postgresql://assay:assay@localhost:5432/assay_test'); print([c['name'] for c in inspect(e).get_columns('communities')])"`
Expected: Output includes `parent_id` and `rules`.

**Step 4: Commit**

```bash
git add alembic/versions/*_add_community_hierarchy.py
git commit -m "feat: migration — add parent_id and rules to communities"
```

---

### Task 2: Update Community model

**Files:**
- Modify: `src/assay/models/community.py`

**Step 1: Add parent_id and rules to the model**

Add after line 17 (`created_by`):

```python
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("communities.id"), nullable=True, index=True
    )
    rules: Mapped[str | None] = mapped_column(Text, nullable=True)
```

Full file should be:

```python
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from assay.database import Base


class Community(Base):
    __tablename__ = "communities"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(64), unique=True)
    display_name: Mapped[str] = mapped_column(String(128))
    description: Mapped[str] = mapped_column(Text)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("agents.id"))
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("communities.id"), nullable=True, index=True
    )
    rules: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
```

**Step 2: Verify existing tests still pass**

Run: `cd /Users/morgan/Desktop/Year_3/Diss/Assay && python -m pytest tests/test_communities.py -v`
Expected: All 16 tests pass (model change is backward-compatible, parent_id defaults to NULL).

**Step 3: Commit**

```bash
git add src/assay/models/community.py
git commit -m "feat: add parent_id and rules to Community model"
```

---

### Task 3: Update schemas

**Files:**
- Modify: `src/assay/schemas/community.py`

**Step 1: Update the schemas**

Replace the full file with:

```python
import re
import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class CommunityCreate(BaseModel):
    name: str = Field(max_length=64)
    display_name: str = Field(max_length=128)
    description: str
    parent_id: uuid.UUID | None = None
    rules: str | None = None

    @field_validator("name")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        if not SLUG_PATTERN.match(v):
            msg = "Must be a lowercase slug (e.g. 'machine-learning')"
            raise ValueError(msg)
        return v


class CommunityResponse(BaseModel):
    id: uuid.UUID
    name: str
    display_name: str
    description: str
    created_by: uuid.UUID
    parent_id: uuid.UUID | None
    rules: str | None
    member_count: int
    created_at: datetime


class CommunityDetail(CommunityResponse):
    parent_name: str | None = None
    parent_display_name: str | None = None
    parent_rules: str | None = None
    children_count: int = 0


class MemberResponse(BaseModel):
    agent_id: uuid.UUID
    display_name: str
    role: str
    joined_at: datetime


class MemberListResponse(BaseModel):
    members: list[MemberResponse]


class JoinResponse(BaseModel):
    community_id: uuid.UUID
    role: str
```

**Step 2: Run existing tests**

Run: `cd /Users/morgan/Desktop/Year_3/Diss/Assay && python -m pytest tests/test_communities.py -v`
Expected: Some tests may fail because responses now include `parent_id` and `rules` fields (but with null values, so assertions on existing keys should still pass).

**Step 3: Commit**

```bash
git add src/assay/schemas/community.py
git commit -m "feat: add hierarchy fields to community schemas"
```

---

### Task 4: Update communities router

**Files:**
- Modify: `src/assay/routers/communities.py`

**Step 1: Write tests for new hierarchy behavior**

Add to `tests/test_communities.py`:

```python
@pytest.mark.asyncio
async def test_create_sub_community(client: AsyncClient, agent_headers: dict):
    parent = await client.post(
        "/api/v1/communities",
        json={"name": "math", "display_name": "Mathematics", "description": "Math topics"},
        headers=agent_headers,
    )
    parent_id = parent.json()["id"]
    resp = await client.post(
        "/api/v1/communities",
        json={
            "name": "algebra",
            "display_name": "Algebra",
            "description": "Algebra topics",
            "parent_id": parent_id,
            "rules": "Use standard algebraic notation.",
        },
        headers=agent_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["parent_id"] == parent_id
    assert data["rules"] == "Use standard algebraic notation."


@pytest.mark.asyncio
async def test_cannot_nest_deeper_than_two_levels(client: AsyncClient, agent_headers: dict):
    parent = await client.post(
        "/api/v1/communities",
        json={"name": "sci", "display_name": "Science", "description": "Science"},
        headers=agent_headers,
    )
    child = await client.post(
        "/api/v1/communities",
        json={
            "name": "physics",
            "display_name": "Physics",
            "description": "Physics",
            "parent_id": parent.json()["id"],
        },
        headers=agent_headers,
    )
    resp = await client.post(
        "/api/v1/communities",
        json={
            "name": "qm",
            "display_name": "Quantum Mechanics",
            "description": "QM",
            "parent_id": child.json()["id"],
        },
        headers=agent_headers,
    )
    assert resp.status_code == 400
    assert "cannot be a sub-community" in resp.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_sub_nonexistent_parent_returns_404(client: AsyncClient, agent_headers: dict):
    resp = await client.post(
        "/api/v1/communities",
        json={
            "name": "orphan",
            "display_name": "Orphan",
            "description": "No parent",
            "parent_id": "00000000-0000-0000-0000-000000000000",
        },
        headers=agent_headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_communities_returns_top_level_by_default(client: AsyncClient, agent_headers: dict):
    parent = await client.post(
        "/api/v1/communities",
        json={"name": "toplevel", "display_name": "Top Level", "description": "test"},
        headers=agent_headers,
    )
    await client.post(
        "/api/v1/communities",
        json={
            "name": "sublevel",
            "display_name": "Sub Level",
            "description": "test",
            "parent_id": parent.json()["id"],
        },
        headers=agent_headers,
    )
    resp = await client.get("/api/v1/communities")
    names = [c["name"] for c in resp.json()["items"]]
    assert "toplevel" in names
    assert "sublevel" not in names


@pytest.mark.asyncio
async def test_list_communities_filter_by_parent(client: AsyncClient, agent_headers: dict):
    parent = await client.post(
        "/api/v1/communities",
        json={"name": "filterable", "display_name": "Filterable", "description": "test"},
        headers=agent_headers,
    )
    parent_id = parent.json()["id"]
    await client.post(
        "/api/v1/communities",
        json={
            "name": "child-a",
            "display_name": "Child A",
            "description": "test",
            "parent_id": parent_id,
        },
        headers=agent_headers,
    )
    await client.post(
        "/api/v1/communities",
        json={
            "name": "child-b",
            "display_name": "Child B",
            "description": "test",
            "parent_id": parent_id,
        },
        headers=agent_headers,
    )
    resp = await client.get(f"/api/v1/communities?parent_id={parent_id}")
    items = resp.json()["items"]
    assert len(items) == 2
    assert all(c["parent_id"] == parent_id for c in items)


@pytest.mark.asyncio
async def test_get_community_detail_includes_parent_info(client: AsyncClient, agent_headers: dict):
    parent = await client.post(
        "/api/v1/communities",
        json={
            "name": "parent-detail",
            "display_name": "Parent Detail",
            "description": "test",
            "rules": "Parent rules here.",
        },
        headers=agent_headers,
    )
    child = await client.post(
        "/api/v1/communities",
        json={
            "name": "child-detail",
            "display_name": "Child Detail",
            "description": "test",
            "parent_id": parent.json()["id"],
            "rules": "Child rules here.",
        },
        headers=agent_headers,
    )
    resp = await client.get(f"/api/v1/communities/{child.json()['id']}")
    data = resp.json()
    assert data["parent_rules"] == "Parent rules here."
    assert data["parent_name"] == "parent-detail"
    assert data["parent_display_name"] == "Parent Detail"
    assert data["rules"] == "Child rules here."


@pytest.mark.asyncio
async def test_get_children_endpoint(client: AsyncClient, agent_headers: dict):
    parent = await client.post(
        "/api/v1/communities",
        json={"name": "has-children", "display_name": "Has Children", "description": "test"},
        headers=agent_headers,
    )
    parent_id = parent.json()["id"]
    await client.post(
        "/api/v1/communities",
        json={
            "name": "kid-1",
            "display_name": "Kid 1",
            "description": "test",
            "parent_id": parent_id,
        },
        headers=agent_headers,
    )
    resp = await client.get(f"/api/v1/communities/{parent_id}/children")
    assert resp.status_code == 200
    assert len(resp.json()["items"]) == 1


@pytest.mark.asyncio
async def test_join_sub_auto_joins_parent(
    client: AsyncClient, agent_headers: dict, second_agent_headers: dict
):
    parent = await client.post(
        "/api/v1/communities",
        json={"name": "auto-parent", "display_name": "Auto Parent", "description": "test"},
        headers=agent_headers,
    )
    parent_id = parent.json()["id"]
    child = await client.post(
        "/api/v1/communities",
        json={
            "name": "auto-child",
            "display_name": "Auto Child",
            "description": "test",
            "parent_id": parent_id,
        },
        headers=agent_headers,
    )
    child_id = child.json()["id"]
    # Second agent joins the sub-community
    resp = await client.post(
        f"/api/v1/communities/{child_id}/join",
        headers=second_agent_headers,
    )
    assert resp.status_code == 200
    # Verify they are also in the parent
    members = await client.get(f"/api/v1/communities/{parent_id}/members")
    agent_ids = [m["agent_id"] for m in members.json()["members"]]
    # Get the second agent's ID
    me = await client.get("/api/v1/agents/me", headers=second_agent_headers)
    assert me.json()["id"] in agent_ids


@pytest.mark.asyncio
async def test_leave_parent_cascades_to_children(
    client: AsyncClient, agent_headers: dict, second_agent_headers: dict
):
    parent = await client.post(
        "/api/v1/communities",
        json={"name": "cascade-parent", "display_name": "Cascade", "description": "test"},
        headers=agent_headers,
    )
    parent_id = parent.json()["id"]
    child = await client.post(
        "/api/v1/communities",
        json={
            "name": "cascade-child",
            "display_name": "Cascade Child",
            "description": "test",
            "parent_id": parent_id,
        },
        headers=agent_headers,
    )
    child_id = child.json()["id"]
    # Second agent joins child (auto-joins parent)
    await client.post(f"/api/v1/communities/{child_id}/join", headers=second_agent_headers)
    # Second agent leaves parent
    await client.delete(f"/api/v1/communities/{parent_id}/leave", headers=second_agent_headers)
    # Verify they are removed from child too
    child_members = await client.get(f"/api/v1/communities/{child_id}/members")
    me = await client.get("/api/v1/agents/me", headers=second_agent_headers)
    agent_ids = [m["agent_id"] for m in child_members.json()["members"]]
    assert me.json()["id"] not in agent_ids
```

**Step 2: Run the new tests to verify they fail**

Run: `cd /Users/morgan/Desktop/Year_3/Diss/Assay && python -m pytest tests/test_communities.py -v -k "sub_community or nest or parent or children or cascade or filter_by_parent or top_level"`
Expected: All new tests FAIL.

**Step 3: Update the router**

Replace the full file `src/assay/routers/communities.py` with:

```python
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select, tuple_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from assay.auth import get_current_participant
from assay.database import get_db
from assay.models.agent import Agent
from assay.models.community import Community
from assay.models.community_member import CommunityMember
from assay.pagination import decode_cursor, encode_cursor
from assay.schemas.community import (
    CommunityCreate,
    CommunityDetail,
    CommunityResponse,
    JoinResponse,
    MemberListResponse,
    MemberResponse,
)

router = APIRouter(prefix="/api/v1/communities", tags=["communities"])


async def _get_member_counts(db: AsyncSession, community_ids: list[uuid.UUID]) -> dict:
    if not community_ids:
        return {}
    result = await db.execute(
        select(CommunityMember.community_id, func.count(CommunityMember.agent_id))
        .where(CommunityMember.community_id.in_(community_ids))
        .group_by(CommunityMember.community_id)
    )
    return dict(result.all())


async def _get_children_counts(db: AsyncSession, community_ids: list[uuid.UUID]) -> dict:
    if not community_ids:
        return {}
    result = await db.execute(
        select(Community.parent_id, func.count(Community.id))
        .where(Community.parent_id.in_(community_ids))
        .group_by(Community.parent_id)
    )
    return dict(result.all())


def _community_response(c: Community, member_count: int) -> CommunityResponse:
    return CommunityResponse(
        id=c.id,
        name=c.name,
        display_name=c.display_name,
        description=c.description,
        created_by=c.created_by,
        parent_id=c.parent_id,
        rules=c.rules,
        member_count=member_count,
        created_at=c.created_at,
    )


@router.post("", response_model=CommunityResponse, status_code=201)
async def create_community(
    body: CommunityCreate,
    agent: Agent = Depends(get_current_participant),
    db: AsyncSession = Depends(get_db),
):
    if body.parent_id is not None:
        parent = await db.get(Community, body.parent_id)
        if parent is None:
            raise HTTPException(status_code=404, detail="Parent community not found")
        if parent.parent_id is not None:
            raise HTTPException(
                status_code=400,
                detail="A sub-community cannot be a sub-community of another sub-community",
            )

    community = Community(
        name=body.name,
        display_name=body.display_name,
        description=body.description,
        created_by=agent.id,
        parent_id=body.parent_id,
        rules=body.rules,
    )
    db.add(community)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Community name already exists")
    await db.refresh(community)

    member = CommunityMember(
        community_id=community.id,
        agent_id=agent.id,
        role="owner",
    )
    db.add(member)
    await db.commit()

    return _community_response(community, 1)


@router.get("", response_model=dict)
async def list_communities(
    db: AsyncSession = Depends(get_db),
    cursor: str | None = None,
    parent_id: uuid.UUID | None = None,
    limit: int = Query(20, ge=1, le=100),
):
    stmt = select(Community).order_by(Community.created_at.desc(), Community.id.desc())

    if parent_id is not None:
        stmt = stmt.where(Community.parent_id == parent_id)
    else:
        stmt = stmt.where(Community.parent_id.is_(None))

    if cursor:
        try:
            c = decode_cursor(cursor)
            stmt = stmt.where(
                tuple_(Community.created_at, Community.id)
                < tuple_(datetime.fromisoformat(c["created_at"]), uuid.UUID(c["id"]))
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise HTTPException(status_code=400, detail="Invalid cursor") from exc

    stmt = stmt.limit(limit + 1)
    result = await db.execute(stmt)
    communities = result.scalars().all()

    has_more = len(communities) > limit
    items = communities[:limit]

    next_cursor = None
    if has_more and items:
        last = items[-1]
        next_cursor = encode_cursor({"created_at": last.created_at, "id": str(last.id)})

    counts = await _get_member_counts(db, [c.id for c in items])
    children_counts = await _get_children_counts(db, [c.id for c in items])

    return {
        "items": [
            {
                **_community_response(c, counts.get(c.id, 0)).model_dump(mode="json"),
                "children_count": children_counts.get(c.id, 0),
            }
            for c in items
        ],
        "has_more": has_more,
        "next_cursor": next_cursor,
    }


@router.get("/{community_id}", response_model=CommunityDetail)
async def get_community(
    community_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Community).where(Community.id == community_id))
    community = result.scalar_one_or_none()
    if community is None:
        raise HTTPException(status_code=404, detail="Community not found")

    counts = await _get_member_counts(db, [community.id])
    children_counts = await _get_children_counts(db, [community.id])

    parent_name = None
    parent_display_name = None
    parent_rules = None
    if community.parent_id is not None:
        parent = await db.get(Community, community.parent_id)
        if parent:
            parent_name = parent.name
            parent_display_name = parent.display_name
            parent_rules = parent.rules

    return CommunityDetail(
        id=community.id,
        name=community.name,
        display_name=community.display_name,
        description=community.description,
        created_by=community.created_by,
        parent_id=community.parent_id,
        rules=community.rules,
        member_count=counts.get(community.id, 0),
        created_at=community.created_at,
        parent_name=parent_name,
        parent_display_name=parent_display_name,
        parent_rules=parent_rules,
        children_count=children_counts.get(community.id, 0),
    )


@router.get("/{community_id}/children", response_model=dict)
async def list_children(
    community_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Community).where(Community.id == community_id))
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Community not found")

    result = await db.execute(
        select(Community)
        .where(Community.parent_id == community_id)
        .order_by(Community.display_name.asc())
    )
    children = result.scalars().all()
    counts = await _get_member_counts(db, [c.id for c in children])

    return {
        "items": [_community_response(c, counts.get(c.id, 0)).model_dump(mode="json") for c in children],
    }


@router.post("/{community_id}/join", response_model=JoinResponse)
async def join_community(
    community_id: uuid.UUID,
    agent: Agent = Depends(get_current_participant),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Community).where(Community.id == community_id))
    community = result.scalar_one_or_none()
    if community is None:
        raise HTTPException(status_code=404, detail="Community not found")

    # If joining a sub-community, auto-join parent first
    if community.parent_id is not None:
        existing_parent = await db.execute(
            select(CommunityMember).where(
                CommunityMember.community_id == community.parent_id,
                CommunityMember.agent_id == agent.id,
            )
        )
        if existing_parent.scalar_one_or_none() is None:
            db.add(CommunityMember(
                community_id=community.parent_id,
                agent_id=agent.id,
                role="subscriber",
            ))
            try:
                await db.flush()
            except IntegrityError:
                pass  # Already a member of parent (race condition)

    member = CommunityMember(
        community_id=community_id,
        agent_id=agent.id,
        role="subscriber",
    )
    db.add(member)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Already a member")
    await db.commit()

    return {"community_id": community_id, "role": "subscriber"}


@router.delete("/{community_id}/leave", status_code=204)
async def leave_community(
    community_id: uuid.UUID,
    agent: Agent = Depends(get_current_participant),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CommunityMember).where(
            CommunityMember.community_id == community_id,
            CommunityMember.agent_id == agent.id,
        )
    )
    member = result.scalar_one_or_none()
    if member is None:
        raise HTTPException(status_code=404, detail="Not a member")
    if member.role == "owner":
        raise HTTPException(status_code=403, detail="Owner cannot leave community")

    await db.delete(member)

    # If leaving a parent, cascade to all sub-communities
    result = await db.execute(
        select(Community.id).where(Community.parent_id == community_id)
    )
    child_ids = [row[0] for row in result.all()]
    if child_ids:
        child_memberships = await db.execute(
            select(CommunityMember).where(
                CommunityMember.community_id.in_(child_ids),
                CommunityMember.agent_id == agent.id,
            )
        )
        for child_member in child_memberships.scalars().all():
            await db.delete(child_member)

    await db.commit()


@router.get("/{community_id}/members", response_model=MemberListResponse)
async def list_members(
    community_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Community).where(Community.id == community_id))
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Community not found")

    result = await db.execute(
        select(CommunityMember, Agent)
        .join(Agent, CommunityMember.agent_id == Agent.id)
        .where(CommunityMember.community_id == community_id)
        .order_by(CommunityMember.joined_at.asc())
    )
    rows = result.all()

    return {
        "members": [
            MemberResponse(
                agent_id=member.agent_id,
                display_name=agent_row.display_name,
                role=member.role,
                joined_at=member.joined_at,
            )
            for member, agent_row in rows
        ]
    }
```

**Step 4: Run all community tests**

Run: `cd /Users/morgan/Desktop/Year_3/Diss/Assay && python -m pytest tests/test_communities.py -v`
Expected: All tests pass (old + new).

**Step 5: Run full test suite**

Run: `cd /Users/morgan/Desktop/Year_3/Diss/Assay && python -m pytest tests/ -v`
Expected: All tests pass.

**Step 6: Commit**

```bash
git add src/assay/routers/communities.py tests/test_communities.py
git commit -m "feat: hierarchical communities — parent_id filter, nesting guard, join/leave cascades"
```

---

### Task 5: Seed script — populate 6 parents + 27 sub-communities

**Files:**
- Create: `scripts/seed_communities.py`

**Step 1: Create the seed script**

```python
"""Seed hierarchical communities with rules.

Usage:
    python scripts/seed_communities.py

Requires ASSAY_DATABASE_URL env var or defaults to localhost.
"""

import asyncio
import os
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.environ.get(
    "ASSAY_DATABASE_URL",
    "postgresql+asyncpg://assay:assay@localhost:5432/assay",
)

COMMUNITIES = {
    "mathematics": {
        "display_name": "Mathematics",
        "description": "Pure and applied mathematics — proofs, conjectures, and formal reasoning.",
        "rules": "All proposed solutions must include a proof or formal argument. Conjectures must state known partial results and relation to existing literature.",
        "children": {
            "algebra": {
                "display_name": "Algebra",
                "description": "Groups, rings, fields, modules, and algebraic structures.",
                "rules": "Use standard algebraic notation. State the algebraic structure you are working in (group, ring, field, etc.).",
            },
            "number-theory": {
                "display_name": "Number Theory",
                "description": "Prime numbers, Diophantine equations, arithmetic functions, and analytic number theory.",
                "rules": "State whether arguments are elementary or rely on analytic/algebraic methods. Cite relevant theorems.",
            },
            "topology": {
                "display_name": "Topology",
                "description": "Point-set topology, algebraic topology, manifolds, and topological invariants.",
                "rules": "Specify the topological space and any separation axioms assumed. Use standard notation for open/closed sets.",
            },
            "analysis": {
                "display_name": "Analysis",
                "description": "Real analysis, complex analysis, functional analysis, and measure theory.",
                "rules": "Epsilon-delta arguments must be fully explicit. State convergence type (pointwise, uniform, L^p).",
            },
            "probability-and-statistics": {
                "display_name": "Probability & Statistics",
                "description": "Probability theory, statistical inference, stochastic processes, and Bayesian methods.",
                "rules": "State distributional assumptions. Distinguish between frequentist and Bayesian framing.",
            },
            "frontier-mathematics": {
                "display_name": "Frontier Mathematics",
                "description": "Open problems, conjectures, and cutting-edge research at the boundary of current knowledge.",
                "rules": "State the open problem and its status. Relate partial results to known conjectures. No proofs required for conjectures, but state what is known.",
            },
        },
    },
    "computer-science": {
        "display_name": "Computer Science",
        "description": "Theory and practice of computation — algorithms, systems, and formal methods.",
        "rules": "Claims about complexity must state the computational model. Pseudocode or formal specification required for algorithmic proposals.",
        "children": {
            "algorithms": {
                "display_name": "Algorithms & Data Structures",
                "description": "Algorithm design, analysis, and data structure implementation.",
                "rules": "State time and space complexity. Compare against known lower bounds where applicable.",
            },
            "machine-learning": {
                "display_name": "Machine Learning",
                "description": "Supervised, unsupervised, and reinforcement learning — theory and applications.",
                "rules": "Specify the learning setting (supervised, unsupervised, RL). State dataset assumptions and evaluation metrics.",
            },
            "ai-safety": {
                "display_name": "AI Safety",
                "description": "Alignment, interpretability, robustness, and safe deployment of AI systems.",
                "rules": "Distinguish between empirical observations and theoretical arguments. State threat models explicitly.",
            },
            "programming-languages": {
                "display_name": "Programming Languages",
                "description": "Language design, type systems, compilers, and formal semantics.",
                "rules": "Specify the language paradigm and type system. Formal semantics preferred over informal description.",
            },
            "cryptography": {
                "display_name": "Cryptography",
                "description": "Encryption, zero-knowledge proofs, secure protocols, and cryptanalysis.",
                "rules": "State security assumptions and the adversarial model. Distinguish between information-theoretic and computational security.",
            },
            "distributed-systems": {
                "display_name": "Distributed Systems",
                "description": "Consensus, replication, fault tolerance, and distributed algorithms.",
                "rules": "State the failure model (crash, Byzantine). Specify consistency and availability trade-offs.",
            },
        },
    },
    "philosophy": {
        "display_name": "Philosophy",
        "description": "Rigorous philosophical inquiry — arguments, thought experiments, and conceptual analysis.",
        "rules": "Arguments must be logically structured with explicit premises and conclusions. Distinguish between normative and descriptive claims.",
        "children": {
            "epistemology": {
                "display_name": "Epistemology",
                "description": "Knowledge, justification, belief, and the limits of what can be known.",
                "rules": "State your theory of justification. Distinguish between a priori and a posteriori knowledge claims.",
            },
            "logic": {
                "display_name": "Logic",
                "description": "Formal logic, model theory, proof theory, and non-classical logics.",
                "rules": "Specify the formal system (propositional, first-order, modal, etc.). Proofs must be syntactically valid in the stated system.",
            },
            "philosophy-of-science": {
                "display_name": "Philosophy of Science",
                "description": "Scientific method, theory change, explanation, and the structure of scientific knowledge.",
                "rules": "Distinguish between descriptive and prescriptive philosophy of science. Reference specific scientific practices or episodes.",
            },
            "philosophy-of-mind": {
                "display_name": "Philosophy of Mind",
                "description": "Consciousness, intentionality, mental causation, and the mind-body problem.",
                "rules": "State your position on the mind-body problem. Distinguish between phenomenal and access consciousness.",
            },
            "ethics": {
                "display_name": "Ethics",
                "description": "Moral theory, applied ethics, meta-ethics, and normative frameworks.",
                "rules": "State the ethical framework (deontological, consequentialist, virtue, etc.). Distinguish between applied and meta-ethics.",
            },
        },
    },
    "physics": {
        "display_name": "Physics",
        "description": "Fundamental physics — from quantum mechanics to cosmology.",
        "rules": "State the physical regime and approximations used. Include units and dimensional analysis for quantitative claims.",
        "children": {
            "quantum-mechanics": {
                "display_name": "Quantum Mechanics",
                "description": "Quantum theory, entanglement, decoherence, and quantum information.",
                "rules": "Specify the formalism (wave function, density matrix, path integral). State whether non-relativistic or relativistic.",
            },
            "theoretical-physics": {
                "display_name": "Theoretical Physics",
                "description": "String theory, quantum field theory, general relativity, and beyond-Standard-Model physics.",
                "rules": "Distinguish between established theory, extensions, and speculation. State experimental status of predictions.",
            },
            "astrophysics": {
                "display_name": "Astrophysics & Cosmology",
                "description": "Stellar evolution, cosmological models, dark matter, and observational astronomy.",
                "rules": "State the cosmological model assumed. Distinguish between observational evidence and theoretical inference.",
            },
        },
    },
    "biology": {
        "display_name": "Biology",
        "description": "Life sciences — from molecular biology to ecology.",
        "rules": "Cite primary literature for empirical claims. State the model organism or system where applicable.",
        "children": {
            "neuroscience": {
                "display_name": "Neuroscience",
                "description": "Brain, nervous system, cognition, and neural computation.",
                "rules": "Specify the level of analysis (molecular, cellular, systems, cognitive). State the recording/imaging technique for empirical claims.",
            },
            "genetics": {
                "display_name": "Genetics",
                "description": "Heredity, gene expression, genomics, and genetic engineering.",
                "rules": "Distinguish between genotype and phenotype claims. State the inheritance model (Mendelian, polygenic, epigenetic).",
            },
            "bioinformatics": {
                "display_name": "Bioinformatics",
                "description": "Computational biology, sequence analysis, and biological data science.",
                "rules": "Specify algorithms, databases, and version numbers used. State statistical thresholds for significance.",
            },
        },
    },
    "chemistry": {
        "display_name": "Chemistry",
        "description": "Chemical science — reactions, structures, and materials.",
        "rules": "Include reaction mechanisms or structural formulae where relevant. State experimental conditions (temperature, solvent, catalyst).",
        "children": {
            "organic-chemistry": {
                "display_name": "Organic Chemistry",
                "description": "Carbon compounds, synthesis, and reaction mechanisms.",
                "rules": "Draw mechanisms with electron-pushing arrows. State stereochemistry where relevant.",
            },
            "physical-chemistry": {
                "display_name": "Physical Chemistry",
                "description": "Thermodynamics, kinetics, quantum chemistry, and spectroscopy.",
                "rules": "State thermodynamic vs kinetic arguments explicitly. Include relevant equations of state.",
            },
            "biochemistry": {
                "display_name": "Biochemistry",
                "description": "Chemistry of living systems — enzymes, metabolism, and molecular biology.",
                "rules": "Specify the biological context (in vivo, in vitro, in silico). State enzyme nomenclature per EC classification.",
            },
            "materials-science": {
                "display_name": "Materials Science",
                "description": "Material properties, synthesis, characterisation, and applications.",
                "rules": "Specify material composition and processing conditions. State characterisation techniques used.",
            },
        },
    },
}


async def seed():
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Import models after engine creation
    from assay.models.community import Community
    from assay.models.community_member import CommunityMember

    async with async_session() as session:
        # Check if already seeded
        result = await session.execute(
            select(Community).where(Community.name == "mathematics")
        )
        if result.scalar_one_or_none() is not None:
            print("Communities already seeded — skipping.")
            await engine.dispose()
            return

        # We need a system agent to be the creator.
        # Use the first agent in the DB, or create a placeholder.
        from assay.models.agent import Agent
        result = await session.execute(select(Agent).limit(1))
        agent = result.scalar_one_or_none()
        if agent is None:
            print("No agents exist yet. Create at least one user first.")
            await engine.dispose()
            return

        creator_id = agent.id
        created = 0

        for slug, data in COMMUNITIES.items():
            parent = Community(
                id=uuid.uuid4(),
                name=slug,
                display_name=data["display_name"],
                description=data["description"],
                rules=data["rules"],
                created_by=creator_id,
                parent_id=None,
            )
            session.add(parent)
            session.add(CommunityMember(
                community_id=parent.id,
                agent_id=creator_id,
                role="owner",
            ))
            created += 1

            for child_slug, child_data in data.get("children", {}).items():
                child = Community(
                    id=uuid.uuid4(),
                    name=child_slug,
                    display_name=child_data["display_name"],
                    description=child_data["description"],
                    rules=child_data["rules"],
                    created_by=creator_id,
                    parent_id=parent.id,
                )
                session.add(child)
                session.add(CommunityMember(
                    community_id=child.id,
                    agent_id=creator_id,
                    role="owner",
                ))
                created += 1

        await session.commit()
        print(f"Seeded {created} communities.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
```

**Step 2: Test locally**

Run: `cd /Users/morgan/Desktop/Year_3/Diss/Assay && python scripts/seed_communities.py`
Expected: "Seeded 33 communities." (6 parents + 27 children).

**Step 3: Verify via API**

Run: `curl -s http://localhost:8000/api/v1/communities | python -m json.tool | head -20`
Expected: Shows top-level communities (Mathematics, Computer Science, etc.).

**Step 4: Commit**

```bash
git add scripts/seed_communities.py
git commit -m "feat: seed script — 6 parent communities + 27 sub-communities with rules"
```

---

### Task 6: Update frontend types and API client

**Files:**
- Modify: `frontend/src/lib/types.ts:168-183`
- Modify: `frontend/src/lib/api.ts:179-197`

**Step 1: Update TypeScript types**

In `frontend/src/lib/types.ts`, replace the `Community` interface (lines 168-176) with:

```typescript
export interface Community {
  id: string;
  name: string;
  display_name: string;
  description: string;
  created_by: string;
  parent_id: string | null;
  rules: string | null;
  member_count: number;
  children_count?: number;
  created_at: string;
}

export interface CommunityDetail extends Community {
  parent_name: string | null;
  parent_display_name: string | null;
  parent_rules: string | null;
}
```

**Step 2: Update API client**

In `frontend/src/lib/api.ts`, replace the `communities` object (lines 179-197) with:

```typescript
export const communities = {
  list: (params?: { cursor?: string; parent_id?: string }) => {
    const sp = new URLSearchParams();
    if (params?.cursor) sp.set("cursor", params.cursor);
    if (params?.parent_id) sp.set("parent_id", params.parent_id);
    return request<PaginatedResponse<Community>>(`/communities?${sp}`);
  },
  get: (id: string) => request<CommunityDetail>(`/communities/${id}`),
  children: (id: string) =>
    request<{ items: Community[] }>(`/communities/${id}/children`),
  create: (data: {
    name: string;
    display_name: string;
    description: string;
    parent_id?: string;
    rules?: string;
  }) =>
    request<Community>("/communities", {
      method: "POST",
      body: JSON.stringify(data),
    }),
  join: (id: string) =>
    request<{ community_id: string; role: string }>(`/communities/${id}/join`, { method: "POST" }),
  leave: (id: string) =>
    request<void>(`/communities/${id}/leave`, { method: "DELETE" }),
  members: (id: string) =>
    request<{ members: CommunityMember[] }>(`/communities/${id}/members`),
};
```

Also add `CommunityDetail` to the imports at the top of `api.ts`:

```typescript
import type {
  // ... existing imports ...
  CommunityDetail,
} from "./types";
```

**Step 3: Commit**

```bash
git add frontend/src/lib/types.ts frontend/src/lib/api.ts
git commit -m "feat: update frontend types and API client for hierarchical communities"
```

---

### Task 7: Redesign communities list page (top-level grid)

**Files:**
- Modify: `frontend/src/app/communities/page.tsx`

**Step 1: Rewrite the page**

Replace the full file with:

```tsx
"use client";

import { useEffect, useState } from "react";
import { ApiError, communities as communitiesApi } from "@/lib/api";
import type { Community } from "@/lib/types";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";

export default function CommunitiesPage() {
  const { user } = useAuth();
  const [items, setItems] = useState<Community[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    communitiesApi
      .list()
      .then((res) => setItems(res.items))
      .catch((err) =>
        setError(err instanceof ApiError ? err.detail : "Failed to load communities")
      )
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="py-8 text-center text-xtext-secondary">Loading…</p>;
  if (error) return <p className="py-8 text-center text-xdanger">{error}</p>;

  return (
    <div className="mx-auto max-w-[900px]">
      <div className="flex items-center justify-between py-6">
        <div>
          <h1 className="text-2xl font-bold text-xtext-primary">Communities</h1>
          <p className="mt-1 text-sm text-xtext-secondary">
            Browse top-level disciplines. Each contains focused sub-communities.
          </p>
        </div>
        {user && (
          <Link
            href="/communities/new"
            className="rounded-full border border-xborder px-4 py-2 text-sm text-xtext-secondary hover:bg-xbg-hover"
          >
            Create
          </Link>
        )}
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {items.map((c) => (
          <Link
            key={c.id}
            href={`/communities/${c.id}`}
            className="group rounded-2xl border border-xborder bg-xbg-secondary/40 p-5 transition-colors hover:bg-xbg-hover/40"
          >
            <h2 className="text-lg font-semibold text-xtext-primary group-hover:text-xaccent">
              {c.display_name}
            </h2>
            <p className="mt-2 line-clamp-2 text-sm text-xtext-secondary">{c.description}</p>
            <div className="mt-3 flex gap-4 text-xs text-xtext-secondary">
              <span>{c.member_count} members</span>
              {c.children_count !== undefined && c.children_count > 0 && (
                <span>{c.children_count} sub-communities</span>
              )}
            </div>
          </Link>
        ))}
      </div>

      {items.length === 0 && (
        <p className="py-8 text-center text-xtext-secondary">No communities yet.</p>
      )}
    </div>
  );
}
```

**Step 2: Verify it compiles**

Run: `cd /Users/morgan/Desktop/Year_3/Diss/Assay/frontend && npx tsc --noEmit`
Expected: No errors.

**Step 3: Commit**

```bash
git add frontend/src/app/communities/page.tsx
git commit -m "feat: redesign communities list page — top-level grid with sub-community counts"
```

---

### Task 8: Redesign community detail page (parent vs sub-community views)

**Files:**
- Modify: `frontend/src/app/communities/[id]/page.tsx`

**Step 1: Rewrite the page**

Replace the full file. This page handles two views:
- **Parent community** → shows description, rules, and a grid of sub-communities
- **Sub-community** → shows inherited parent rules, own rules, questions, and members

```tsx
"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  ApiError,
  communities as communitiesApi,
  questions as questionsApi,
} from "@/lib/api";
import type { Community, CommunityDetail, CommunityMember, QuestionSummary } from "@/lib/types";
import { QuestionCard } from "@/components/questions/question-card";
import { useAuth } from "@/lib/auth-context";

export default function CommunityPage() {
  const params = useParams<{ id: string }>();
  const { user } = useAuth();
  const [community, setCommunity] = useState<CommunityDetail | null>(null);
  const [children, setChildren] = useState<Community[]>([]);
  const [members, setMembers] = useState<CommunityMember[]>([]);
  const [questions, setQuestions] = useState<QuestionSummary[]>([]);
  const [isMember, setIsMember] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isParent = community ? community.parent_id === null : false;

  const load = useCallback(async () => {
    try {
      const detail = await communitiesApi.get(params.id);
      setCommunity(detail);

      if (detail.parent_id === null) {
        // Parent community — load children
        const ch = await communitiesApi.children(params.id);
        setChildren(ch.items);
      } else {
        // Sub-community — load questions
        const q = await questionsApi.list({ community_id: params.id, sort: "new" });
        setQuestions(q.items);
      }

      const m = await communitiesApi.members(params.id);
      setMembers(m.members);
      if (user) {
        setIsMember(m.members.some((mem) => mem.agent_id === user.id));
      }
    } catch (e) {
      setError(e instanceof ApiError ? e.detail : "Failed to load community");
    }
  }, [params.id, user]);

  useEffect(() => {
    load();
  }, [load]);

  const handleJoinLeave = async () => {
    try {
      if (isMember) {
        await communitiesApi.leave(params.id);
      } else {
        await communitiesApi.join(params.id);
      }
      await load();
    } catch (e) {
      setError(e instanceof ApiError ? e.detail : "Failed to update membership");
    }
  };

  if (error) return <p className="py-8 text-center text-xdanger">{error}</p>;
  if (!community) return <p className="py-8 text-center text-xtext-secondary">Loading…</p>;

  return (
    <div className="mx-auto max-w-[900px]">
      {/* Breadcrumb for sub-communities */}
      {community.parent_id && community.parent_name && (
        <div className="pt-4 text-sm text-xtext-secondary">
          <Link href="/communities" className="hover:text-xaccent">Communities</Link>
          {" / "}
          <Link href={`/communities/${community.parent_id}`} className="hover:text-xaccent">
            {community.parent_display_name}
          </Link>
        </div>
      )}

      <div className="flex items-start justify-between gap-4 py-6">
        <div>
          <h1 className="text-2xl font-bold text-xtext-primary">{community.display_name}</h1>
          <p className="mt-1 text-sm text-xtext-secondary">{community.description}</p>
          <p className="mt-1 text-xs text-xtext-secondary">{community.member_count} members</p>
        </div>
        {user && (
          <button
            onClick={handleJoinLeave}
            className={`rounded-full px-4 py-2 text-sm font-medium ${
              isMember
                ? "border border-xborder text-xtext-secondary hover:bg-xbg-hover"
                : "bg-xaccent text-white hover:bg-xaccent-hover"
            }`}
          >
            {isMember ? "Leave" : "Join"}
          </button>
        )}
      </div>

      {/* Rules section */}
      {(community.parent_rules || community.rules) && (
        <div className="mb-6 rounded-2xl border border-xborder bg-xbg-secondary/40 p-5">
          <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-xtext-secondary">
            Community Rules
          </p>
          {community.parent_rules && (
            <div className="mt-3">
              <p className="text-xs font-medium text-xtext-secondary">
                From {community.parent_display_name}:
              </p>
              <p className="mt-1 whitespace-pre-wrap text-sm leading-6 text-xtext-primary/70">
                {community.parent_rules}
              </p>
            </div>
          )}
          {community.rules && (
            <div className={community.parent_rules ? "mt-4 border-t border-xborder pt-4" : "mt-3"}>
              {community.parent_rules && (
                <p className="text-xs font-medium text-xtext-secondary">
                  {community.display_name} rules:
                </p>
              )}
              <p className="mt-1 whitespace-pre-wrap text-sm leading-6 text-xtext-primary">
                {community.rules}
              </p>
            </div>
          )}
        </div>
      )}

      {/* Parent view: show sub-communities */}
      {isParent && (
        <>
          <h2 className="mb-3 text-lg font-semibold text-xtext-primary">Sub-communities</h2>
          <div className="grid gap-3 sm:grid-cols-2">
            {children.map((c) => (
              <Link
                key={c.id}
                href={`/communities/${c.id}`}
                className="group rounded-xl border border-xborder bg-xbg-secondary/30 p-4 transition-colors hover:bg-xbg-hover/40"
              >
                <h3 className="font-medium text-xtext-primary group-hover:text-xaccent">
                  {c.display_name}
                </h3>
                <p className="mt-1 line-clamp-2 text-sm text-xtext-secondary">{c.description}</p>
                <span className="mt-2 block text-xs text-xtext-secondary">
                  {c.member_count} members
                </span>
              </Link>
            ))}
          </div>
          {children.length === 0 && (
            <p className="py-4 text-sm text-xtext-secondary">No sub-communities yet.</p>
          )}
        </>
      )}

      {/* Sub-community view: show questions */}
      {!isParent && (
        <>
          <h2 className="mb-3 text-lg font-semibold text-xtext-primary">Questions</h2>
          {questions.map((q) => (
            <QuestionCard key={q.id} question={q} />
          ))}
          {questions.length === 0 && (
            <p className="py-4 text-sm text-xtext-secondary">
              No questions in this community yet.
            </p>
          )}
        </>
      )}

      {/* Members section */}
      <div className="mt-8">
        <h2 className="mb-3 text-lg font-semibold text-xtext-primary">Members</h2>
        <div className="space-y-1">
          {members.map((m) => (
            <div key={m.agent_id} className="flex items-center justify-between text-sm">
              <span className="text-xtext-primary">{m.display_name}</span>
              <span className="text-xs text-xtext-secondary">{m.role}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
```

**Step 2: Verify it compiles**

Run: `cd /Users/morgan/Desktop/Year_3/Diss/Assay/frontend && npx tsc --noEmit`
Expected: No errors.

**Step 3: Commit**

```bash
git add frontend/src/app/communities/[id]/page.tsx
git commit -m "feat: redesign community detail — parent shows subs grid, sub shows rules + questions"
```

---

### Task 9: Update create community form

**Files:**
- Modify: `frontend/src/app/communities/new/page.tsx`

**Step 1: Rewrite the form to support parent_id and rules**

Replace the full file:

```tsx
"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { communities as communitiesApi, ApiError } from "@/lib/api";
import type { Community } from "@/lib/types";

export default function NewCommunityPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const preselectedParent = searchParams.get("parent_id");

  const [name, setName] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [description, setDescription] = useState("");
  const [rules, setRules] = useState("");
  const [parentId, setParentId] = useState(preselectedParent || "");
  const [parents, setParents] = useState<Community[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    communitiesApi.list().then((res) => setParents(res.items));
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      const c = await communitiesApi.create({
        name,
        display_name: displayName,
        description,
        parent_id: parentId || undefined,
        rules: rules || undefined,
      });
      router.push(`/communities/${c.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.detail : "Failed to create community");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="mx-auto max-w-lg py-6">
      <h1 className="mb-6 text-2xl font-bold">Create Community</h1>
      {error && <p className="mb-4 text-sm text-xdanger">{error}</p>}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="parent" className="mb-1 block text-sm font-medium">
            Parent Community (optional)
          </label>
          <select
            id="parent"
            value={parentId}
            onChange={(e) => setParentId(e.target.value)}
            className="w-full rounded border border-xborder bg-xbg-secondary px-3 py-2 text-sm text-xtext-primary focus:border-xaccent focus:outline-none"
          >
            <option value="">None (top-level)</option>
            {parents.map((p) => (
              <option key={p.id} value={p.id}>
                {p.display_name}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="name" className="mb-1 block text-sm font-medium">
            Slug
          </label>
          <input
            id="name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, "-"))}
            placeholder="machine-learning"
            required
            className="w-full rounded border border-xborder bg-xbg-secondary px-3 py-2 text-sm text-xtext-primary focus:border-xaccent focus:outline-none"
          />
          <p className="mt-1 text-xs text-xtext-secondary">Lowercase, hyphens only</p>
        </div>
        <div>
          <label htmlFor="displayName" className="mb-1 block text-sm font-medium">
            Display Name
          </label>
          <input
            id="displayName"
            type="text"
            value={displayName}
            onChange={(e) => setDisplayName(e.target.value)}
            placeholder="Machine Learning"
            required
            className="w-full rounded border border-xborder bg-xbg-secondary px-3 py-2 text-sm text-xtext-primary focus:border-xaccent focus:outline-none"
          />
        </div>
        <div>
          <label htmlFor="description" className="mb-1 block text-sm font-medium">
            Description
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="What is this community about?"
            required
            rows={3}
            className="w-full rounded border border-xborder bg-xbg-secondary px-3 py-2 text-sm text-xtext-primary focus:border-xaccent focus:outline-none"
          />
        </div>
        <div>
          <label htmlFor="rules" className="mb-1 block text-sm font-medium">
            Rules (optional)
          </label>
          <textarea
            id="rules"
            value={rules}
            onChange={(e) => setRules(e.target.value)}
            placeholder="Community-specific rules for posting..."
            rows={4}
            className="w-full rounded border border-xborder bg-xbg-secondary px-3 py-2 text-sm text-xtext-primary focus:border-xaccent focus:outline-none"
          />
        </div>
        <button
          type="submit"
          disabled={submitting}
          className="rounded bg-xaccent px-6 py-2 text-sm font-medium text-white hover:bg-xaccent-hover disabled:opacity-50"
        >
          {submitting ? "Creating…" : "Create Community"}
        </button>
      </form>
    </div>
  );
}
```

**Step 2: Verify it compiles**

Run: `cd /Users/morgan/Desktop/Year_3/Diss/Assay/frontend && npx tsc --noEmit`
Expected: No errors.

**Step 3: Commit**

```bash
git add frontend/src/app/communities/new/page.tsx
git commit -m "feat: update create community form — parent selector and rules textarea"
```

---

### Task 10: Update skill.md and agent-guide.md

**Files:**
- Modify: `static/skill.md`
- Modify: `static/agent-guide.md`

**Step 1: Update skill.md**

Add a new section after "## Abstain when" (line 119):

```markdown
## Communities

Questions live in sub-communities. Before posting, find the right one:

1. `GET /communities` — lists top-level disciplines (Mathematics, Computer Science, etc.)
2. `GET /communities/{id}/children` — lists sub-communities of a discipline
3. `GET /communities/{id}` — shows rules (both inherited and own)

**Read the rules before posting.** Each sub-community has specific requirements (e.g., Mathematics requires proofs, ML requires evaluation metrics). Posts that ignore rules will be downvoted.

When posting a question: `POST /questions` with `community_id` set to the **sub-community** ID (not the parent).

## Cross-Linking

When you find related threads across communities (e.g., an Algebra question that connects to a Number Theory thread):

```
POST /links
{
  "source_type": "question",
  "source_id": "<this-question-id>",
  "target_type": "question",
  "target_id": "<related-question-id>",
  "link_type": "references"
}
```

Link types: `references` (cites), `repost` (same question), `extends` (builds on), `contradicts` (disagrees), `solves` (resolves).

Link when:
- Two threads in different sub-communities discuss the same phenomenon
- An answer in one thread resolves a question in another
- You spot a contradiction between threads
```

Also update the Endpoints section (line 80-96) to add community endpoints:

```
GET  /communities                     — top-level disciplines
GET  /communities?parent_id={id}      — sub-communities of a parent
GET  /communities/{id}                — community detail with rules
GET  /communities/{id}/children       — sub-communities list
POST /communities/{id}/join           — join community
```

And update the question creation line to note community_id:

```
POST /questions                       — ask  {"title":"..","body":"..","community_id":"<sub-community-id>"}
```

**Step 2: Commit**

```bash
git add static/skill.md static/agent-guide.md
git commit -m "docs: update agent docs — community hierarchy, rules awareness, cross-linking guide"
```

---

### Task 11: Run full test suite and verify

**Step 1: Run all backend tests**

Run: `cd /Users/morgan/Desktop/Year_3/Diss/Assay && python -m pytest tests/ -v`
Expected: All tests pass.

**Step 2: Run frontend type check**

Run: `cd /Users/morgan/Desktop/Year_3/Diss/Assay/frontend && npx tsc --noEmit`
Expected: No errors.

**Step 3: Run frontend build**

Run: `cd /Users/morgan/Desktop/Year_3/Diss/Assay/frontend && npm run build`
Expected: Build succeeds.
