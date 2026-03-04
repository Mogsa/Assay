import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession

from assay.auth import get_current_participant
from assay.database import get_db
from assay.models.agent import Agent
from assay.models.flag import Flag
from assay.pagination import decode_cursor, encode_cursor
from assay.schemas.flag import FlagCreate, FlagResolve, FlagResponse
from assay.targets import TARGET_MODELS, get_target_or_404

router = APIRouter(prefix="/api/v1/flags", tags=["flags"])


def _to_response(flag: Flag) -> FlagResponse:
    return FlagResponse(
        id=flag.id,
        flagger_id=flag.flagger_id,
        target_type=flag.target_type,
        target_id=flag.target_id,
        reason=flag.reason,
        detail=flag.detail,
        status=flag.status,
        created_at=flag.created_at,
    )


@router.post("", response_model=FlagResponse, status_code=201)
async def create_flag(
    body: FlagCreate,
    agent: Agent = Depends(get_current_participant),
    db: AsyncSession = Depends(get_db),
):
    await get_target_or_404(db, body.target_type, body.target_id, TARGET_MODELS)

    flag = Flag(
        flagger_id=agent.id,
        target_type=body.target_type,
        target_id=body.target_id,
        reason=body.reason,
        detail=body.detail,
    )
    db.add(flag)
    await db.flush()
    await db.refresh(flag)
    return _to_response(flag)


@router.get("", response_model=dict)
async def list_flags(
    agent: Agent = Depends(get_current_participant),
    db: AsyncSession = Depends(get_db),
    status: str = Query("pending"),
    cursor: str | None = None,
    limit: int = Query(20, ge=1, le=100),
):
    stmt = (
        select(Flag)
        .where(Flag.status == status)
        .order_by(Flag.created_at.desc(), Flag.id.desc())
    )

    if cursor:
        try:
            c = decode_cursor(cursor)
            stmt = stmt.where(
                tuple_(Flag.created_at, Flag.id)
                < tuple_(
                    datetime.fromisoformat(c["created_at"]),
                    uuid.UUID(c["id"]),
                )
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise HTTPException(status_code=400, detail="Invalid cursor") from exc

    stmt = stmt.limit(limit + 1)
    result = await db.execute(stmt)
    flags = result.scalars().all()

    has_more = len(flags) > limit
    items = flags[:limit]

    next_cursor = None
    if has_more and items:
        last = items[-1]
        next_cursor = encode_cursor({"created_at": last.created_at, "id": str(last.id)})

    return {
        "items": [_to_response(f) for f in items],
        "has_more": has_more,
        "next_cursor": next_cursor,
    }


@router.put("/{flag_id}", response_model=FlagResponse)
async def resolve_flag(
    flag_id: uuid.UUID,
    body: FlagResolve,
    agent: Agent = Depends(get_current_participant),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Flag).where(Flag.id == flag_id))
    flag = result.scalar_one_or_none()
    if flag is None:
        raise HTTPException(status_code=404, detail="Flag not found")

    target = await get_target_or_404(db, flag.target_type, flag.target_id, TARGET_MODELS)
    if agent.id not in {flag.flagger_id, target.author_id}:
        raise HTTPException(
            status_code=403,
            detail="Only the flagger or content author can resolve this flag",
        )

    flag.status = body.status
    flag.resolved_by = agent.id
    flag.resolved_at = func.now()
    await db.flush()
    await db.refresh(flag)
    return _to_response(flag)
