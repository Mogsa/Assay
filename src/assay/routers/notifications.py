import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, tuple_, update
from sqlalchemy.ext.asyncio import AsyncSession

from assay.auth import get_current_principal
from assay.database import get_db
from assay.models.agent import Agent
from assay.models.notification import Notification
from assay.pagination import decode_cursor, encode_cursor
from assay.schemas.notification import NotificationResponse

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


def _to_response(n: Notification) -> NotificationResponse:
    return NotificationResponse(
        id=n.id,
        agent_id=n.agent_id,
        type=n.type,
        source_agent_id=n.source_agent_id,
        target_type=n.target_type,
        target_id=n.target_id,
        preview=n.preview,
        is_read=n.is_read,
        created_at=n.created_at,
    )


@router.get("", response_model=dict)
async def list_notifications(
    agent: Agent = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db),
    unread_only: bool = False,
    cursor: str | None = None,
    limit: int = Query(20, ge=1, le=100),
):
    stmt = (
        select(Notification)
        .where(Notification.agent_id == agent.id)
        .order_by(Notification.created_at.desc(), Notification.id.desc())
    )

    if unread_only:
        stmt = stmt.where(Notification.is_read == False)  # noqa: E712

    if cursor:
        try:
            c = decode_cursor(cursor)
            stmt = stmt.where(
                tuple_(Notification.created_at, Notification.id)
                < tuple_(
                    datetime.fromisoformat(c["created_at"]),
                    uuid.UUID(c["id"]),
                )
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise HTTPException(status_code=400, detail="Invalid cursor") from exc

    stmt = stmt.limit(limit + 1)
    result = await db.execute(stmt)
    notifications = result.scalars().all()

    has_more = len(notifications) > limit
    items = notifications[:limit]

    next_cursor = None
    if has_more and items:
        last = items[-1]
        next_cursor = encode_cursor(
            {"created_at": last.created_at, "id": str(last.id)}
        )

    return {
        "items": [_to_response(n) for n in items],
        "has_more": has_more,
        "next_cursor": next_cursor,
    }


@router.put("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_read(
    notification_id: uuid.UUID,
    agent: Agent = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Notification).where(Notification.id == notification_id)
    )
    notification = result.scalar_one_or_none()
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")

    if notification.agent_id != agent.id:
        raise HTTPException(status_code=403, detail="Not your notification")

    notification.is_read = True
    await db.flush()
    await db.refresh(notification)
    return _to_response(notification)


@router.post("/read-all", response_model=dict)
async def mark_all_read(
    agent: Agent = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        update(Notification)
        .where(Notification.agent_id == agent.id, Notification.is_read == False)  # noqa: E712
        .values(is_read=True)
    )
    await db.flush()
    return {"updated_count": result.rowcount}
