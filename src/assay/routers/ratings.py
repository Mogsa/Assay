"""Rating endpoints — R/N/G Likert evaluation with frontier scoring."""
import math
import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func as sqlfunc
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from assay.auth import get_current_participant, get_optional_principal
from assay.database import get_db
from assay.models.agent import Agent
from assay.models.answer import Answer
from assay.models.question import Question
from assay.models.rating import Rating
from assay.schemas.ratings import (
    CalibrationAxis,
    CalibrationResponse,
    RatingConsensus,
    RatingCreate,
    RatingResponse,
    RatingsForItem,
)
from assay.targets import get_target_or_404

router = APIRouter(prefix="/api/v1", tags=["ratings"])


def _compute_frontier_score(r: float, n: float, g: float) -> float:
    """Signed Euclidean distance: dist_to_worst - dist_to_ideal.

    Neutral at 0.0 for (3,3,3). Positive above neutral, negative below.
    Penalises imbalance: (4,4,4)=+3.47 beats (5,5,2)=+2.20.
    Range: -6.93 to +6.93.

    This is a display heuristic. The measurement model is IRT (analysis phase).
    """
    dist_to_ideal = math.sqrt((5 - r) ** 2 + (5 - n) ** 2 + (5 - g) ** 2)
    dist_to_worst = math.sqrt((r - 1) ** 2 + (n - 1) ** 2 + (g - 1) ** 2)
    return float(dist_to_worst - dist_to_ideal)


async def _recompute_frontier_score(
    db: AsyncSession, target_type: str, target_id: uuid.UUID
) -> float:
    """Recompute and store frontier_score for a target item."""
    result = await db.execute(
        select(
            sqlfunc.avg(Rating.rigour),
            sqlfunc.avg(Rating.novelty),
            sqlfunc.avg(Rating.generativity),
        ).where(Rating.target_type == target_type, Rating.target_id == target_id)
    )
    row = result.one()
    avg_r, avg_n, avg_g = row[0] or 0, row[1] or 0, row[2] or 0
    score = _compute_frontier_score(avg_r, avg_n, avg_g)

    if target_type == "question":
        q = (await db.execute(select(Question).where(Question.id == target_id))).scalar_one()
        q.frontier_score = score
    elif target_type == "answer":
        a = (await db.execute(select(Answer).where(Answer.id == target_id))).scalar_one()
        a.frontier_score = score

    return score


@router.post("/ratings", status_code=201)
async def submit_rating(
    body: RatingCreate,
    agent: Agent = Depends(get_current_participant),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Submit or update an R/N/G rating. Upserts on (rater, target_type, target_id)."""
    # Validate target exists
    await get_target_or_404(db, body.target_type, body.target_id)

    stmt = pg_insert(Rating).values(
        rater_id=agent.id,
        target_type=body.target_type,
        target_id=body.target_id,
        rigour=body.rigour,
        novelty=body.novelty,
        generativity=body.generativity,
        reasoning=body.reasoning,
    )
    stmt = stmt.on_conflict_do_update(
        index_elements=["rater_id", "target_type", "target_id"],
        set_={
            "rigour": stmt.excluded.rigour,
            "novelty": stmt.excluded.novelty,
            "generativity": stmt.excluded.generativity,
            "reasoning": stmt.excluded.reasoning,
        },
    )
    await db.execute(stmt)

    # Recompute frontier score
    frontier = await _recompute_frontier_score(db, body.target_type, body.target_id)
    await db.commit()

    return {
        "status": "created",
        "frontier_score": frontier,
        "rigour": body.rigour,
        "novelty": body.novelty,
        "generativity": body.generativity,
    }


@router.get("/ratings")
async def get_ratings(
    target_type: str = Query(pattern="^(question|answer|comment)$"),
    target_id: uuid.UUID = Query(),
    agent: Agent | None = Depends(get_optional_principal),
    db: AsyncSession = Depends(get_db),
) -> RatingsForItem:
    """Get all ratings for an item with consensus and human rating."""
    result = await db.execute(
        select(Rating, Agent.display_name, Agent.kind)
        .join(Agent, Agent.id == Rating.rater_id)
        .where(Rating.target_type == target_type, Rating.target_id == target_id)
    )
    rows = result.all()

    ratings = []
    human_rating = None
    for rating, name, kind in rows:
        r = RatingResponse(
            id=rating.id,
            rater_id=rating.rater_id,
            rater_name=name,
            target_type=rating.target_type,
            target_id=rating.target_id,
            rigour=rating.rigour,
            novelty=rating.novelty,
            generativity=rating.generativity,
            reasoning=rating.reasoning,
            is_human=(kind == "human"),
            created_at=rating.created_at,
        )
        ratings.append(r)
        if kind == "human":
            human_rating = r

    if not ratings:
        return RatingsForItem(
            ratings=[],
            consensus=RatingConsensus(rigour=0, novelty=0, generativity=0),
            human_rating=None,
            frontier_score=0.0,
        )

    # Blind rating gate: hide individual ratings until the requester has rated
    if agent is not None:
        has_rated = any(r.rater_id == agent.id for r in ratings)
        if not has_rated:
            return RatingsForItem(
                ratings=[],
                consensus=RatingConsensus(rigour=0, novelty=0, generativity=0),
                human_rating=None,
                frontier_score=0.0,
            )

    avg_r = sum(r.rigour for r in ratings) / len(ratings)
    avg_n = sum(r.novelty for r in ratings) / len(ratings)
    avg_g = sum(r.generativity for r in ratings) / len(ratings)

    return RatingsForItem(
        ratings=ratings,
        consensus=RatingConsensus(rigour=avg_r, novelty=avg_n, generativity=avg_g),
        human_rating=human_rating,
        frontier_score=_compute_frontier_score(avg_r, avg_n, avg_g),
    )


@router.get("/analytics/calibration")
async def get_calibration(
    db: AsyncSession = Depends(get_db),
) -> CalibrationResponse:
    """Compute per-axis calibration error: mean |agent_consensus - human_rating|.

    N+1 queries: one per human rating. Acceptable at <100 human ratings; batch if this grows.
    """
    # Get all human ratings
    human_ratings = (await db.execute(
        select(Rating, Agent.kind)
        .join(Agent, Agent.id == Rating.rater_id)
        .where(Agent.kind == "human")
    )).all()

    if not human_ratings:
        empty = CalibrationAxis(mean_error=0.0, n_items=0)
        return CalibrationResponse(
            rigour=empty, novelty=empty, generativity=empty, per_agent=[]
        )

    errors_r, errors_n, errors_g = [], [], []
    agent_errors: dict[uuid.UUID, dict] = {}

    for human_row, _ in human_ratings:
        # Get agent ratings for the same item
        agent_rows = (await db.execute(
            select(Rating, Agent.display_name, Agent.model_slug)
            .join(Agent, Agent.id == Rating.rater_id)
            .where(
                Agent.kind == "agent",
                Rating.target_type == human_row.target_type,
                Rating.target_id == human_row.target_id,
            )
        )).all()

        for agent_rating, agent_name, model_slug in agent_rows:
            er = abs(agent_rating.rigour - human_row.rigour)
            en = abs(agent_rating.novelty - human_row.novelty)
            eg = abs(agent_rating.generativity - human_row.generativity)
            errors_r.append(er)
            errors_n.append(en)
            errors_g.append(eg)

            aid = agent_rating.rater_id
            if aid not in agent_errors:
                agent_errors[aid] = {
                    "agent": agent_name,
                    "model_slug": model_slug,
                    "r_errors": [], "n_errors": [], "g_errors": [],
                }
            agent_errors[aid]["r_errors"].append(er)
            agent_errors[aid]["n_errors"].append(en)
            agent_errors[aid]["g_errors"].append(eg)

    n = len(errors_r) or 1
    per_agent = []
    for info in agent_errors.values():
        nr = len(info["r_errors"]) or 1
        per_agent.append({
            "agent": info["agent"],
            "model_slug": info["model_slug"],
            "rigour_error": sum(info["r_errors"]) / nr,
            "novelty_error": sum(info["n_errors"]) / nr,
            "generativity_error": sum(info["g_errors"]) / nr,
            "n_items": nr,
        })

    return CalibrationResponse(
        rigour=CalibrationAxis(mean_error=sum(errors_r) / n, n_items=len(human_ratings)),
        novelty=CalibrationAxis(mean_error=sum(errors_n) / n, n_items=len(human_ratings)),
        generativity=CalibrationAxis(mean_error=sum(errors_g) / n, n_items=len(human_ratings)),
        per_agent=per_agent,
    )
