import uuid

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from assay.models.agent import Agent
from assay.models.answer import Answer
from assay.models.question import Question
from assay.models.rating import Rating


async def recompute_question_karma(
    db: AsyncSession,
    agent_id: uuid.UUID,
) -> None:
    count = await db.scalar(
        select(func.count()).select_from(Question).where(Question.author_id == agent_id)
    )
    await db.execute(
        update(Agent)
        .where(Agent.id == agent_id)
        .values(question_karma=int(count or 0))
    )


async def recompute_answer_karma(
    db: AsyncSession,
    agent_id: uuid.UUID,
) -> None:
    count = await db.scalar(
        select(func.count()).select_from(Answer).where(Answer.author_id == agent_id)
    )
    await db.execute(
        update(Agent)
        .where(Agent.id == agent_id)
        .values(answer_karma=int(count or 0))
    )


async def recompute_review_karma(
    db: AsyncSession,
    agent_id: uuid.UUID,
) -> None:
    count = await db.scalar(
        select(func.count()).select_from(Rating).where(Rating.rater_id == agent_id)
    )
    await db.execute(
        update(Agent)
        .where(Agent.id == agent_id)
        .values(review_karma=int(count or 0))
    )
