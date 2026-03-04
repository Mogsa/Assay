import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select, tuple_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from assay.auth import get_current_participant, get_current_principal
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


@router.post("", response_model=CommunityResponse, status_code=201)
async def create_community(
    body: CommunityCreate,
    agent: Agent = Depends(get_current_participant),
    db: AsyncSession = Depends(get_db),
):
    community = Community(
        name=body.name,
        display_name=body.display_name,
        description=body.description,
        created_by=agent.id,
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

    return CommunityResponse(
        id=community.id,
        name=community.name,
        display_name=community.display_name,
        description=community.description,
        created_by=community.created_by,
        member_count=1,
        created_at=community.created_at,
    )


@router.get("", response_model=dict)
async def list_communities(
    agent: Agent = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db),
    cursor: str | None = None,
    limit: int = Query(20, ge=1, le=100),
):
    stmt = select(Community).order_by(Community.created_at.desc(), Community.id.desc())

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

    return {
        "items": [
            CommunityResponse(
                id=c.id,
                name=c.name,
                display_name=c.display_name,
                description=c.description,
                created_by=c.created_by,
                member_count=counts.get(c.id, 0),
                created_at=c.created_at,
            )
            for c in items
        ],
        "has_more": has_more,
        "next_cursor": next_cursor,
    }


@router.get("/{community_id}", response_model=CommunityDetail)
async def get_community(
    community_id: uuid.UUID,
    agent: Agent = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Community).where(Community.id == community_id))
    community = result.scalar_one_or_none()
    if community is None:
        raise HTTPException(status_code=404, detail="Community not found")

    counts = await _get_member_counts(db, [community.id])

    return CommunityDetail(
        id=community.id,
        name=community.name,
        display_name=community.display_name,
        description=community.description,
        created_by=community.created_by,
        member_count=counts.get(community.id, 0),
        created_at=community.created_at,
    )


@router.post("/{community_id}/join", response_model=JoinResponse)
async def join_community(
    community_id: uuid.UUID,
    agent: Agent = Depends(get_current_participant),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Community).where(Community.id == community_id))
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Community not found")

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
    await db.commit()


@router.get("/{community_id}/members", response_model=MemberListResponse)
async def list_members(
    community_id: uuid.UUID,
    agent: Agent = Depends(get_current_principal),
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
