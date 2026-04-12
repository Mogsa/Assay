import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from assay.auth import get_optional_principal
from assay.database import get_db
from assay.models.activity_log import ActivityLog
from assay.models.agent import Agent
from assay.pagination import decode_cursor, encode_cursor
from assay.schemas.activity_log import ActivityLogEntry

router = APIRouter(prefix="/api/v1/log", tags=["activity"])


@router.get("", response_model=dict)
async def list_activity(
    _principal: Agent | None = Depends(get_optional_principal),
    db: AsyncSession = Depends(get_db),
    actor: uuid.UUID | None = None,
    since: datetime | None = None,
    cursor: str | None = None,
    limit: int = Query(50, ge=1, le=100),
) -> dict:
    stmt = (
        select(ActivityLog, Agent.display_name)
        .join(Agent, Agent.id == ActivityLog.actor_id)
        .order_by(ActivityLog.created_at.desc(), ActivityLog.id.desc())
    )

    if actor is not None:
        stmt = stmt.where(ActivityLog.actor_id == actor)

    if since is not None:
        stmt = stmt.where(ActivityLog.created_at >= since)

    if cursor:
        try:
            decoded = decode_cursor(cursor)
            cursor_ts = datetime.fromisoformat(decoded["created_at"])
            cursor_id = decoded["id"]
            stmt = stmt.where(
                (ActivityLog.created_at < cursor_ts)
                | (
                    (ActivityLog.created_at == cursor_ts)
                    & (ActivityLog.id < cursor_id)
                )
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise HTTPException(status_code=400, detail="Invalid cursor") from exc

    result = await db.execute(stmt.limit(limit + 1))
    rows = result.all()

    has_more = len(rows) > limit
    items_raw = rows[:limit]

    next_cursor = None
    if has_more and items_raw:
        last_entry, _ = items_raw[-1]
        next_cursor = encode_cursor(
            {"created_at": last_entry.created_at, "id": str(last_entry.id)}
        )

    return {
        "items": [
            ActivityLogEntry(
                id=entry.id,
                actor_id=entry.actor_id,
                actor_name=display_name,
                action=entry.action,
                target_type=entry.target_type,
                target_id=entry.target_id,
                summary=entry.summary,
                created_at=entry.created_at,
            )
            for entry, display_name in items_raw
        ],
        "has_more": has_more,
        "next_cursor": next_cursor,
    }
