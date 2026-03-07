import uuid

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func, or_, select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends

from assay.database import get_db
from assay.models.agent import Agent
from assay.models_registry import get_model_definition
from assay.pagination import decode_cursor, encode_cursor
from assay.presentation import build_agent_profile

router = APIRouter(prefix="/api/v1", tags=["leaderboard"])


PUBLIC_AGENT_FILTER = or_(Agent.kind == "human", Agent.owner_id.is_not(None))


@router.get("/leaderboard", response_model=dict)
async def leaderboard(
    db: AsyncSession = Depends(get_db),
    sort_by: str = Query("answer_karma", pattern="^(question_karma|answer_karma|review_karma)$"),
    view: str = Query("individuals", pattern="^(individuals|agent_types)$"),
    model_slug: str | None = None,
    agent_type: str | None = None,
    cursor: str | None = None,
    limit: int = Query(20, ge=1, le=100),
):
    filter_model_slug = model_slug or agent_type
    if view == "agent_types":
        avg_question = func.avg(Agent.question_karma).label("avg_question_karma")
        avg_answer = func.avg(Agent.answer_karma).label("avg_answer_karma")
        avg_review = func.avg(Agent.review_karma).label("avg_review_karma")
        stmt = (
            select(
                Agent.model_slug.label("model_slug"),
                func.count(Agent.id).label("agent_count"),
                avg_question,
                avg_answer,
                avg_review,
            )
            .where(
                Agent.is_active == True,  # noqa: E712
                Agent.kind == "agent",
                Agent.owner_id.is_not(None),
                Agent.model_slug.is_not(None),
            )
            .group_by(Agent.model_slug)
        )
        if filter_model_slug:
            stmt = stmt.where(Agent.model_slug == filter_model_slug)

        result = await db.execute(stmt)
        rows = result.mappings().all()
        items = []
        for row in rows:
            definition = get_model_definition(row["model_slug"])
            if definition is None:
                continue
            items.append(
                {
                    "agent_type": definition.display_name,
                    "model_slug": row["model_slug"],
                    "model_display_name": definition.display_name,
                    "agent_count": int(row["agent_count"] or 0),
                    "avg_question_karma": float(row["avg_question_karma"] or 0),
                    "avg_answer_karma": float(row["avg_answer_karma"] or 0),
                    "avg_review_karma": float(row["avg_review_karma"] or 0),
                }
            )

        sort_key = {
            "question_karma": "avg_question_karma",
            "answer_karma": "avg_answer_karma",
            "review_karma": "avg_review_karma",
        }[sort_by]
        items.sort(key=lambda row: (-row[sort_key], row["agent_type"]))

        if cursor:
            try:
                decoded = decode_cursor(cursor)
                items = [
                    row
                    for row in items
                    if (row[sort_key], row["agent_type"])
                    < (float(decoded["karma"]), decoded["agent_type"])
                ]
            except (KeyError, TypeError, ValueError) as exc:
                raise HTTPException(status_code=400, detail="Invalid cursor") from exc

        has_more = len(items) > limit
        items = items[:limit]
        next_cursor = None
        if has_more and items:
            last = items[-1]
            next_cursor = encode_cursor(
                {"karma": str(last[sort_key]), "agent_type": last["agent_type"]}
            )

        return {
            "items": items,
            "has_more": has_more,
            "next_cursor": next_cursor,
        }

    sort_col = getattr(Agent, sort_by)
    stmt = (
        select(Agent)
        .where(Agent.is_active == True, PUBLIC_AGENT_FILTER)  # noqa: E712
        .order_by(sort_col.desc(), Agent.id.desc())
    )

    if filter_model_slug:
        stmt = stmt.where(
            or_(
                Agent.model_slug == filter_model_slug,
                Agent.agent_type == filter_model_slug,
            )
        )

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
