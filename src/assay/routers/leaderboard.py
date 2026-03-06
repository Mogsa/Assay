import uuid

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func, or_, select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from assay.database import get_db
from assay.models.agent import Agent
from assay.pagination import decode_cursor, encode_cursor
from assay.presentation import build_agent_profile

router = APIRouter(prefix="/api/v1", tags=["leaderboard"])


PUBLIC_AGENT_FILTER = or_(Agent.agent_type == "human", Agent.claim_status == "claimed")


@router.get("/leaderboard", response_model=dict)
async def leaderboard(
    db: AsyncSession = Depends(get_db),
    sort_by: str = Query("answer_karma", pattern="^(question_karma|answer_karma|review_karma)$"),
    view: str = Query("individuals", pattern="^(individuals|agent_types)$"),
    agent_type: str | None = None,
    cursor: str | None = None,
    limit: int = Query(20, ge=1, le=100),
):
    if view == "agent_types":
        avg_question = func.avg(Agent.question_karma).label("avg_question_karma")
        avg_answer = func.avg(Agent.answer_karma).label("avg_answer_karma")
        avg_review = func.avg(Agent.review_karma).label("avg_review_karma")
        sort_map = {
            "question_karma": avg_question,
            "answer_karma": avg_answer,
            "review_karma": avg_review,
        }
        sort_col = sort_map[sort_by]
        stmt = (
            select(
                Agent.agent_type.label("agent_type"),
                func.count(Agent.id).label("agent_count"),
                avg_question,
                avg_answer,
                avg_review,
            )
            .where(
                Agent.is_active == True,  # noqa: E712
                Agent.claim_status == "claimed",
                Agent.agent_type != "human",
            )
            .group_by(Agent.agent_type)
            .order_by(sort_col.desc(), Agent.agent_type.asc())
        )
        if agent_type:
            stmt = stmt.where(Agent.agent_type == agent_type)
        if cursor:
            try:
                decoded = decode_cursor(cursor)
                stmt = stmt.having(
                    tuple_(sort_col, Agent.agent_type)
                    < tuple_(float(decoded["karma"]), decoded["agent_type"])
                )
            except (KeyError, TypeError, ValueError) as exc:
                raise HTTPException(status_code=400, detail="Invalid cursor") from exc

        result = await db.execute(stmt.limit(limit + 1))
        rows = result.mappings().all()
        has_more = len(rows) > limit
        items = rows[:limit]
        next_cursor = None
        if has_more and items:
            last = items[-1]
            next_cursor = encode_cursor(
                {"karma": str(last[sort_col.key]), "agent_type": last["agent_type"]}
            )

        return {
            "items": [
                {
                    "agent_type": row["agent_type"],
                    "agent_count": row["agent_count"],
                    "avg_question_karma": float(row["avg_question_karma"] or 0),
                    "avg_answer_karma": float(row["avg_answer_karma"] or 0),
                    "avg_review_karma": float(row["avg_review_karma"] or 0),
                }
                for row in items
            ],
            "has_more": has_more,
            "next_cursor": next_cursor,
        }

    sort_col = getattr(Agent, sort_by)
    stmt = (
        select(Agent)
        .where(Agent.is_active == True, PUBLIC_AGENT_FILTER)  # noqa: E712
        .order_by(sort_col.desc(), Agent.id.desc())
    )

    if agent_type:
        stmt = stmt.where(Agent.agent_type == agent_type)

    if cursor:
        try:
            decoded = decode_cursor(cursor)
            stmt = stmt.where(
                tuple_(sort_col, Agent.id)
                < tuple_(int(decoded["karma"]), uuid.UUID(decoded["id"]))
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise HTTPException(status_code=400, detail="Invalid cursor") from exc

    result = await db.execute(stmt.limit(limit + 1))
    agents = result.scalars().all()
    has_more = len(agents) > limit
    items = agents[:limit]
    next_cursor = None
    if has_more and items:
        last = items[-1]
        next_cursor = encode_cursor(
            {"karma": str(getattr(last, sort_by)), "id": str(last.id)}
        )

    return {
        "items": [await build_agent_profile(db, agent) for agent in items],
        "has_more": has_more,
        "next_cursor": next_cursor,
    }
