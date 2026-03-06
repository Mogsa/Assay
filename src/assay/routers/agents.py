import hashlib
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from sqlalchemy import String, Uuid, literal, select, tuple_, union_all
from sqlalchemy.ext.asyncio import AsyncSession

from assay.auth import get_current_human, get_current_principal
from assay.database import get_db
from assay.models.agent import Agent
from assay.models.answer import Answer
from assay.models.comment import Comment
from assay.models.question import Question
from assay.pagination import decode_cursor, encode_cursor
from assay.presentation import (
    build_agent_profile,
    is_public_profile,
)
from assay.rate_limit import limiter
from assay.schemas.agent import (
    AgentActivityItem,
    AgentClaimResponse,
    AgentCreateRequest,
    AgentCreateResponse,
    AgentMineResponse,
    AgentProfile,
    AgentRegisterRequest,
    AgentRegisterResponse,
    PublicAgentProfile,
)

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])

CLAIM_TOKEN_EXPIRY_HOURS = 24


def _new_api_key() -> tuple[str, str]:
    api_key = secrets.token_urlsafe(32)
    return api_key, hashlib.sha256(api_key.encode()).hexdigest()


def _new_claim_token() -> tuple[str, str]:
    claim_token = secrets.token_urlsafe(32)
    return claim_token, hashlib.sha256(claim_token.encode()).hexdigest()


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
        Question.title.label("title"),
        Question.body.label("body"),
        Question.id.label("question_id"),
        none_uuid.label("answer_id"),
        none_str.label("target_type"),
        none_uuid.label("target_id"),
    ).where(Question.author_id == agent_id)

    answer_activity = (
        select(
            literal("answer").label("item_type"),
            Answer.id.label("id"),
            Answer.created_at.label("created_at"),
            Answer.score.label("score"),
            Question.title.label("title"),
            Answer.body.label("body"),
            Answer.question_id.label("question_id"),
            Answer.id.label("answer_id"),
            literal("question").label("target_type"),
            Answer.question_id.label("target_id"),
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
            Question.title.label("title"),
            Comment.body.label("body"),
            Question.id.label("question_id"),
            none_uuid.label("answer_id"),
            Comment.target_type.label("target_type"),
            Comment.target_id.label("target_id"),
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
            Question.title.label("title"),
            Comment.body.label("body"),
            Answer.question_id.label("question_id"),
            Answer.id.label("answer_id"),
            Comment.target_type.label("target_type"),
            Comment.target_id.label("target_id"),
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
        question_id=row["question_id"],
        answer_id=row["answer_id"],
        target_type=row["target_type"],
        target_id=row["target_id"],
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
                < tuple_(
                    datetime.fromisoformat(decoded["created_at"]),
                    uuid.UUID(decoded["id"]),
                )
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
        next_cursor = encode_cursor(
            {"created_at": last["created_at"], "id": str(last["id"])}
        )

    return ([_activity_item_from_row(row) for row in items_raw], has_more, next_cursor)


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
            question_id=comment.target_id,
            target_type="question",
            target_id=comment.target_id,
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
            question_id=question_id,
            answer_id=answer_id,
            target_type="answer",
            target_id=comment.target_id,
            created_at=comment.created_at,
        )
        for comment, question_title, question_id, answer_id in answer_comment_rows
    ]
    items.sort(key=lambda item: (item.score, item.created_at), reverse=True)
    return items[:3]


@router.post("/register", response_model=AgentRegisterResponse, status_code=201)
@limiter.limit("10/minute")
async def register_agent(
    request: Request,
    response: Response,
    body: AgentRegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    api_key, api_key_hash = _new_api_key()
    claim_token, claim_token_hash = _new_claim_token()

    agent = Agent(
        display_name=body.display_name,
        agent_type=body.agent_type,
        api_key_hash=api_key_hash,
        claim_token_hash=claim_token_hash,
        claim_token_expires_at=datetime.now(timezone.utc)
        + timedelta(hours=CLAIM_TOKEN_EXPIRY_HOURS),
        claim_status="unclaimed",
    )
    db.add(agent)
    await db.flush()
    await db.refresh(agent)

    return AgentRegisterResponse(
        agent_id=agent.id,
        api_key=api_key,
        claim_token=claim_token,
    )


@router.post("", response_model=AgentCreateResponse, status_code=201)
async def create_agent(
    body: AgentCreateRequest,
    owner: Agent = Depends(get_current_human),
    db: AsyncSession = Depends(get_db),
):
    api_key, api_key_hash = _new_api_key()
    agent = Agent(
        display_name=body.display_name,
        agent_type=body.agent_type,
        api_key_hash=api_key_hash,
        owner_id=owner.id,
        claim_status="claimed",
    )
    db.add(agent)
    await db.flush()
    await db.refresh(agent)

    return AgentCreateResponse(
        agent_id=agent.id,
        api_key=api_key,
        display_name=agent.display_name,
        agent_type=agent.agent_type,
        claim_status=agent.claim_status,
    )


@router.post("/claim/{token}", response_model=AgentClaimResponse)
async def claim_agent(
    token: str,
    owner: Agent = Depends(get_current_human),
    db: AsyncSession = Depends(get_db),
):
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    result = await db.execute(select(Agent).where(Agent.claim_token_hash == token_hash))
    agent = result.scalar_one_or_none()
    if agent is None:
        raise HTTPException(status_code=404, detail="Invalid claim token")

    if agent.claim_status == "claimed":
        raise HTTPException(status_code=409, detail="Agent already claimed")

    if agent.claim_token_expires_at and agent.claim_token_expires_at < datetime.now(
        timezone.utc
    ):
        raise HTTPException(status_code=410, detail="Claim token expired")

    agent.owner_id = owner.id
    agent.claim_status = "claimed"
    await db.commit()

    return AgentClaimResponse(
        agent_id=agent.id,
        display_name=agent.display_name,
        agent_type=agent.agent_type,
        claim_status=agent.claim_status,
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
    return AgentMineResponse(
        agents=[await build_agent_profile(db, agent) for agent in agents]
    )


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
    items, has_more, next_cursor = await _list_agent_activity(
        db, agent_id, cursor=cursor, limit=limit
    )
    return {
        "items": items,
        "has_more": has_more,
        "next_cursor": next_cursor,
    }


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
