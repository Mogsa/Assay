import secrets
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy import String, Uuid, func, literal, select, tuple_, union_all
from sqlalchemy.ext.asyncio import AsyncSession

from assay.auth import get_current_human, get_current_principal, get_optional_principal
from assay.database import get_db
from assay.models.agent import Agent
from assay.models.answer import Answer
from assay.models.link import Link
from assay.models.comment import Comment
from assay.models.question import Question
from assay.models_registry import (
    get_model_definition,
    get_runtime_definition,
    iter_model_definitions,
    iter_runtime_definitions,
)
from assay.pagination import decode_cursor, encode_cursor
from assay.tokens import hash_token
from assay.presentation import build_agent_profile, is_public_profile
from assay.rate_limit import limiter
from assay.schemas.analytics import ResearchStatsResponse
from assay.schemas.agent import (
    AgentActivityItem,
    AgentApiKeyResponse,
    AgentCreateRequest,
    AgentMineResponse,
    AgentProfile,
    PublicAgentProfile,
)

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])


def _new_api_key() -> tuple[str, str]:
    api_key = f"sk_{secrets.token_urlsafe(32)}"
    return api_key, hash_token(api_key)


async def _get_public_agent_or_404(db: AsyncSession, agent_id: uuid.UUID) -> Agent:
    agent = await db.get(Agent, agent_id)
    if agent is None or not is_public_profile(agent):
        raise HTTPException(status_code=404, detail="Profile not found")
    return agent


def _activity_union(agent_id: uuid.UUID):
    none_uuid = literal(None, type_=Uuid())
    none_str = literal(None, type_=String())

    question_activity = select(
        literal("question").label("item_type"),
        Question.id.label("id"),
        Question.created_at.label("created_at"),
        Question.score.label("score"),
        Question.created_via.label("created_via"),
        Question.title.label("title"),
        Question.body.label("body"),
        Question.id.label("question_id"),
        none_uuid.label("answer_id"),
        none_str.label("target_type"),
        none_uuid.label("target_id"),
        none_str.label("verdict"),
    ).where(Question.author_id == agent_id)

    answer_activity = (
        select(
            literal("answer").label("item_type"),
            Answer.id.label("id"),
            Answer.created_at.label("created_at"),
            Answer.score.label("score"),
            Answer.created_via.label("created_via"),
            Question.title.label("title"),
            Answer.body.label("body"),
            Answer.question_id.label("question_id"),
            Answer.id.label("answer_id"),
            literal("question").label("target_type"),
            Answer.question_id.label("target_id"),
            none_str.label("verdict"),
        )
        .join(Question, Question.id == Answer.question_id)
        .where(Answer.author_id == agent_id)
    )

    question_comment_activity = (
        select(
            literal("comment").label("item_type"),
            Comment.id.label("id"),
            Comment.created_at.label("created_at"),
            Comment.score.label("score"),
            Comment.created_via.label("created_via"),
            Question.title.label("title"),
            Comment.body.label("body"),
            Question.id.label("question_id"),
            none_uuid.label("answer_id"),
            Comment.target_type.label("target_type"),
            Comment.target_id.label("target_id"),
            Comment.verdict.label("verdict"),
        )
        .join(Question, Question.id == Comment.target_id)
        .where(Comment.author_id == agent_id, Comment.target_type == "question")
    )

    answer_comment_activity = (
        select(
            literal("comment").label("item_type"),
            Comment.id.label("id"),
            Comment.created_at.label("created_at"),
            Comment.score.label("score"),
            Comment.created_via.label("created_via"),
            Question.title.label("title"),
            Comment.body.label("body"),
            Answer.question_id.label("question_id"),
            Answer.id.label("answer_id"),
            Comment.target_type.label("target_type"),
            Comment.target_id.label("target_id"),
            Comment.verdict.label("verdict"),
        )
        .join(Answer, Answer.id == Comment.target_id)
        .join(Question, Question.id == Answer.question_id)
        .where(Comment.author_id == agent_id, Comment.target_type == "answer")
    )

    return union_all(
        question_activity,
        answer_activity,
        question_comment_activity,
        answer_comment_activity,
    ).subquery()


def _activity_item_from_row(row) -> AgentActivityItem:
    return AgentActivityItem(
        item_type=row["item_type"],
        id=row["id"],
        title=row["title"],
        body=row["body"],
        score=row["score"],
        created_via=row["created_via"],
        question_id=row["question_id"],
        answer_id=row["answer_id"],
        target_type=row["target_type"],
        target_id=row["target_id"],
        verdict=row["verdict"],
        created_at=row["created_at"],
    )


async def _list_agent_activity(
    db: AsyncSession,
    agent_id: uuid.UUID,
    *,
    cursor: str | None = None,
    limit: int = 20,
) -> tuple[list[AgentActivityItem], bool, str | None]:
    activity = _activity_union(agent_id)
    stmt = select(activity).order_by(activity.c.created_at.desc(), activity.c.id.desc())

    if cursor:
        try:
            decoded = decode_cursor(cursor)
            stmt = stmt.where(
                tuple_(activity.c.created_at, activity.c.id)
                < tuple_(datetime.fromisoformat(decoded["created_at"]), uuid.UUID(decoded["id"]))
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise HTTPException(status_code=400, detail="Invalid cursor") from exc

    result = await db.execute(stmt.limit(limit + 1))
    rows = result.mappings().all()

    has_more = len(rows) > limit
    items_raw = rows[:limit]
    next_cursor = None
    if has_more and items_raw:
        last = items_raw[-1]
        next_cursor = encode_cursor({"created_at": last["created_at"], "id": str(last["id"])})

    return ([_activity_item_from_row(row) for row in items_raw], has_more, next_cursor)


async def _get_owned_agent_or_404(
    db: AsyncSession,
    *,
    owner_id: uuid.UUID,
    agent_id: uuid.UUID,
) -> Agent:
    agent = await db.get(Agent, agent_id)
    if agent is None or agent.owner_id != owner_id:
        raise HTTPException(status_code=404, detail="Agent not found")
    if agent.kind == "human":
        raise HTTPException(status_code=400, detail="Human profiles do not have API keys")
    return agent


async def _recent_questions(db: AsyncSession, agent_id: uuid.UUID) -> list[AgentActivityItem]:
    result = await db.execute(
        select(Question)
        .where(Question.author_id == agent_id)
        .order_by(Question.created_at.desc(), Question.id.desc())
        .limit(3)
    )
    return [
        AgentActivityItem(
            item_type="question",
            id=question.id,
            title=question.title,
            body=question.body,
            score=question.score,
            created_via=question.created_via,
            question_id=question.id,
            created_at=question.created_at,
        )
        for question in result.scalars().all()
    ]


async def _top_answers(db: AsyncSession, agent_id: uuid.UUID) -> list[AgentActivityItem]:
    result = await db.execute(
        select(Answer, Question.title)
        .join(Question, Question.id == Answer.question_id)
        .where(Answer.author_id == agent_id)
        .order_by(Answer.score.desc(), Answer.created_at.desc())
        .limit(3)
    )
    return [
        AgentActivityItem(
            item_type="answer",
            id=answer.id,
            title=question_title,
            body=answer.body,
            score=answer.score,
            created_via=answer.created_via,
            question_id=answer.question_id,
            answer_id=answer.id,
            target_type="question",
            target_id=answer.question_id,
            created_at=answer.created_at,
        )
        for answer, question_title in result.all()
    ]


async def _top_reviews(db: AsyncSession, agent_id: uuid.UUID) -> list[AgentActivityItem]:
    question_comment_rows = (
        await db.execute(
            select(Comment, Question.title, literal(None, type_=Uuid()))
            .join(Question, Question.id == Comment.target_id)
            .where(Comment.author_id == agent_id, Comment.target_type == "question")
        )
    ).all()
    answer_comment_rows = (
        await db.execute(
            select(Comment, Question.title, Answer.question_id, Answer.id)
            .join(Answer, Answer.id == Comment.target_id)
            .join(Question, Question.id == Answer.question_id)
            .where(Comment.author_id == agent_id, Comment.target_type == "answer")
        )
    ).all()

    items = [
        AgentActivityItem(
            item_type="comment",
            id=comment.id,
            title=question_title,
            body=comment.body,
            score=comment.score,
            created_via=comment.created_via,
            question_id=comment.target_id,
            target_type="question",
            target_id=comment.target_id,
            verdict=comment.verdict,
            created_at=comment.created_at,
        )
        for comment, question_title, _answer_id in question_comment_rows
    ] + [
        AgentActivityItem(
            item_type="comment",
            id=comment.id,
            title=question_title,
            body=comment.body,
            score=comment.score,
            created_via=comment.created_via,
            question_id=question_id,
            answer_id=answer_id,
            target_type="answer",
            target_id=comment.target_id,
            verdict=comment.verdict,
            created_at=comment.created_at,
        )
        for comment, question_title, question_id, answer_id in answer_comment_rows
    ]
    items.sort(key=lambda item: (item.score, item.created_at), reverse=True)
    return items[:3]


@router.get("/registry")
async def get_registry():
    return {
        "models": [
            {"slug": m.slug, "display_name": m.display_name, "provider": m.provider}
            for m in iter_model_definitions()
        ],
        "runtimes": [
            {"slug": r.slug, "display_name": r.display_name}
            for r in iter_runtime_definitions()
        ],
    }


@router.post("", response_model=AgentApiKeyResponse, status_code=201)
@limiter.limit("10/minute")
async def create_agent(
    request: Request,
    response: Response,
    body: AgentCreateRequest,
    owner: Agent = Depends(get_current_human),
    db: AsyncSession = Depends(get_db),
):
    model = get_model_definition(body.model_slug)
    if model is None:
        raise HTTPException(status_code=400, detail="Unknown model slug")

    runtime = get_runtime_definition(body.runtime_kind)
    if runtime is None:
        raise HTTPException(status_code=400, detail="Unknown runtime kind")

    api_key, api_key_hash = _new_api_key()
    agent = Agent(
        display_name=body.display_name,
        agent_type=model.display_name,
        kind="agent",
        model_slug=model.slug,
        runtime_kind=runtime.slug,
        api_key_hash=api_key_hash,
        owner_id=owner.id,
    )
    db.add(agent)
    await db.flush()
    profile = await build_agent_profile(db, agent)
    return AgentApiKeyResponse(
        agent_id=agent.id,
        api_key=api_key,
        display_name=agent.display_name,
        agent_type=profile.agent_type,
        model_slug=profile.model_slug,
        model_display_name=profile.model_display_name,
        runtime_kind=profile.runtime_kind,
    )


@router.get("/mine", response_model=AgentMineResponse)
async def list_my_agents(
    owner: Agent = Depends(get_current_human),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Agent).where(Agent.owner_id == owner.id).order_by(Agent.created_at.desc())
    )
    agents = result.scalars().all()
    return AgentMineResponse(agents=[await build_agent_profile(db, agent) for agent in agents])


@router.get("/me", response_model=AgentProfile)
async def get_me(
    agent: Agent = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db),
):
    return await build_agent_profile(db, agent)


@router.get("/{agent_id}/activity", response_model=dict)
async def get_public_activity(
    agent_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    cursor: str | None = None,
    limit: int = Query(20, ge=1, le=100),
):
    await _get_public_agent_or_404(db, agent_id)
    items, has_more, next_cursor = await _list_agent_activity(db, agent_id, cursor=cursor, limit=limit)
    return {"items": items, "has_more": has_more, "next_cursor": next_cursor}


@router.get("/{agent_id}/research-stats", response_model=ResearchStatsResponse)
async def get_research_stats(
    agent_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _principal: Agent | None = Depends(get_optional_principal),
):
    # Count links by type
    link_rows = (await db.execute(
        select(Link.link_type, func.count(Link.id))
        .where(Link.created_by == agent_id)
        .group_by(Link.link_type)
    )).all()

    links_by_type = {"references": 0, "repost": 0, "extends": 0, "contradicts": 0, "solves": 0}
    total = 0
    for link_type, count in link_rows:
        links_by_type[link_type] = count
        total += count

    # Count progeny: extends links to questions
    progeny_count = (await db.execute(
        select(func.count(Link.id))
        .where(Link.created_by == agent_id)
        .where(Link.link_type == "extends")
        .where(Link.target_type == "question")
    )).scalar() or 0

    return ResearchStatsResponse(
        links_created=total,
        links_by_type=links_by_type,
        progeny_count=progeny_count,
    )


@router.get("/{agent_id}", response_model=PublicAgentProfile)
async def get_public_profile(
    agent_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    agent = await _get_public_agent_or_404(db, agent_id)
    profile = await build_agent_profile(db, agent)
    return PublicAgentProfile(
        **profile.model_dump(),
        recent_questions=await _recent_questions(db, agent.id),
        top_answers=await _top_answers(db, agent.id),
        top_reviews=await _top_reviews(db, agent.id),
    )


@router.post("/{agent_id}/api-key", response_model=AgentApiKeyResponse)
async def rotate_agent_api_key(
    agent_id: uuid.UUID,
    owner: Agent = Depends(get_current_human),
    db: AsyncSession = Depends(get_db),
):
    agent = await _get_owned_agent_or_404(db, owner_id=owner.id, agent_id=agent_id)
    api_key, api_key_hash = _new_api_key()
    agent.api_key_hash = api_key_hash
    await db.flush()
    profile = await build_agent_profile(db, agent)
    return AgentApiKeyResponse(
        agent_id=agent.id,
        api_key=api_key,
        display_name=agent.display_name,
        agent_type=profile.agent_type,
        model_slug=profile.model_slug,
        model_display_name=profile.model_display_name,
        runtime_kind=profile.runtime_kind,
    )
