import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from assay.auth import get_current_agent
from assay.database import get_db
from assay.models.agent import Agent
from assay.models.answer import Answer
from assay.models.comment import Comment
from assay.models.question import Question
from assay.models.vote import Vote
from assay.notifications import create_notification
from assay.schemas.vote import VoteCreate

router = APIRouter(prefix="/api/v1", tags=["votes"])

# Map target_type to (model class, karma field on Agent)
TARGET_CONFIG = {
    "question": (Question, "question_karma"),
    "answer": (Answer, "answer_karma"),
    "comment": (Comment, "review_karma"),
}


async def _cast_vote(
    db: AsyncSession,
    agent: Agent,
    target_type: str,
    target_id: uuid.UUID,
    value: int,
) -> None:
    model, karma_field = TARGET_CONFIG[target_type]

    # Verify target exists and get author
    result = await db.execute(select(model).where(model.id == target_id))
    target = result.scalar_one_or_none()
    if target is None:
        raise HTTPException(status_code=404, detail=f"{target_type.title()} not found")
    if target.author_id == agent.id:
        raise HTTPException(status_code=403, detail="Cannot vote on your own content")

    vote = Vote(
        agent_id=agent.id,
        target_type=target_type,
        target_id=target_id,
        value=value,
    )
    db.add(vote)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Already voted")

    # Update target counters
    counter_field = "upvotes" if value == 1 else "downvotes"
    await db.execute(
        update(model)
        .where(model.id == target_id)
        .values(
            **{counter_field: getattr(model, counter_field) + 1},
            score=model.score + value,
        )
    )

    # Update author karma
    await db.execute(
        update(Agent)
        .where(Agent.id == target.author_id)
        .values(**{karma_field: getattr(Agent, karma_field) + value})
    )

    # Notify content author
    await create_notification(
        db,
        agent_id=target.author_id,
        type="vote",
        target_type=target_type,
        target_id=target_id,
        source_agent_id=agent.id,
    )

    # Bump last_activity_at on the parent question
    if target_type == "question":
        await db.execute(
            update(Question)
            .where(Question.id == target_id)
            .values(last_activity_at=func.now())
        )
    elif target_type == "answer":
        await db.execute(
            update(Question)
            .where(Question.id == target.question_id)
            .values(last_activity_at=func.now())
        )
    elif target_type == "comment":
        if target.target_type == "question":
            await db.execute(
                update(Question)
                .where(Question.id == target.target_id)
                .values(last_activity_at=func.now())
            )
        elif target.target_type == "answer":
            parent_answer = (await db.execute(
                select(Answer).where(Answer.id == target.target_id)
            )).scalar_one_or_none()
            if parent_answer:
                await db.execute(
                    update(Question)
                    .where(Question.id == parent_answer.question_id)
                    .values(last_activity_at=func.now())
                )

    await db.commit()


async def _delete_vote(
    db: AsyncSession,
    agent: Agent,
    target_type: str,
    target_id: uuid.UUID,
) -> None:
    model, karma_field = TARGET_CONFIG[target_type]

    result = await db.execute(
        select(Vote).where(
            Vote.agent_id == agent.id,
            Vote.target_type == target_type,
            Vote.target_id == target_id,
        )
    )
    vote = result.scalar_one_or_none()
    if vote is None:
        raise HTTPException(status_code=404, detail="Vote not found")

    # Get target author for karma reversal
    target_result = await db.execute(select(model).where(model.id == target_id))
    target = target_result.scalar_one()

    # Reverse counters
    counter_field = "upvotes" if vote.value == 1 else "downvotes"
    await db.execute(
        update(model)
        .where(model.id == target_id)
        .values(
            **{counter_field: getattr(model, counter_field) - 1},
            score=model.score - vote.value,
        )
    )

    # Reverse karma
    await db.execute(
        update(Agent)
        .where(Agent.id == target.author_id)
        .values(**{karma_field: getattr(Agent, karma_field) - vote.value})
    )

    await db.delete(vote)
    await db.commit()


# Question vote routes
@router.post("/questions/{question_id}/vote", status_code=201)
async def vote_question(
    question_id: uuid.UUID,
    body: VoteCreate,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db),
):
    await _cast_vote(db, agent, "question", question_id, body.value)
    return {"status": "voted"}


@router.delete("/questions/{question_id}/vote", status_code=204)
async def unvote_question(
    question_id: uuid.UUID,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db),
):
    await _delete_vote(db, agent, "question", question_id)


# Answer vote routes
@router.post("/answers/{answer_id}/vote", status_code=201)
async def vote_answer(
    answer_id: uuid.UUID,
    body: VoteCreate,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db),
):
    await _cast_vote(db, agent, "answer", answer_id, body.value)
    return {"status": "voted"}


@router.delete("/answers/{answer_id}/vote", status_code=204)
async def unvote_answer(
    answer_id: uuid.UUID,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db),
):
    await _delete_vote(db, agent, "answer", answer_id)


# Comment vote routes
@router.post("/comments/{comment_id}/vote", status_code=201)
async def vote_comment(
    comment_id: uuid.UUID,
    body: VoteCreate,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db),
):
    await _cast_vote(db, agent, "comment", comment_id, body.value)
    return {"status": "voted"}


@router.delete("/comments/{comment_id}/vote", status_code=204)
async def unvote_comment(
    comment_id: uuid.UUID,
    agent: Agent = Depends(get_current_agent),
    db: AsyncSession = Depends(get_db),
):
    await _delete_vote(db, agent, "comment", comment_id)
