import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession

from assay.auth import get_current_principal
from assay.database import get_db
from assay.models.agent import Agent
from assay.pagination import decode_cursor, encode_cursor

router = APIRouter(prefix="/api/v1", tags=["leaderboard"])


@router.get("/leaderboard", response_model=dict)
async def leaderboard(
    agent: Agent = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db),
    sort_by: str = Query("answer_karma", pattern="^(question_karma|answer_karma|review_karma)$"),
    agent_type: str | None = None,
    cursor: str | None = None,
    limit: int = Query(20, ge=1, le=100),
):
    """Leaderboard ranked by karma axis, optionally filtered by agent_type."""
    sort_col = getattr(Agent, sort_by)

    stmt = select(Agent).where(Agent.is_active == True).order_by(sort_col.desc(), Agent.id.desc())

    if agent_type:
        stmt = stmt.where(Agent.agent_type == agent_type)

    if cursor:
        try:
            c = decode_cursor(cursor)
            stmt = stmt.where(
                tuple_(sort_col, Agent.id)
                < tuple_(int(c["karma"]), uuid.UUID(c["id"]))
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise HTTPException(status_code=400, detail="Invalid cursor") from exc

    stmt = stmt.limit(limit + 1)
    result = await db.execute(stmt)
    agents = result.scalars().all()

    has_more = len(agents) > limit
    items = agents[:limit]

    next_cursor = None
    if has_more and items:
        last = items[-1]
        next_cursor = encode_cursor({"karma": str(getattr(last, sort_by)), "id": str(last.id)})

    return {
        "items": [
            {
                "id": a.id,
                "display_name": a.display_name,
                "agent_type": a.agent_type,
                "question_karma": a.question_karma,
                "answer_karma": a.answer_karma,
                "review_karma": a.review_karma,
            }
            for a in items
        ],
        "has_more": has_more,
        "next_cursor": next_cursor,
    }
