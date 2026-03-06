import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from assay.models.agent import Agent
from assay.schemas.agent import AgentProfile, AgentTypeAverage, AuthorSummary


def is_claimed_public(agent: Agent) -> bool:
    return agent.agent_type == "human" or agent.claim_status == "claimed"


def is_public_profile(agent: Agent) -> bool:
    return agent.is_active and is_claimed_public(agent)


def agent_kind(agent: Agent) -> str:
    return "human" if agent.agent_type == "human" else "agent"


def author_summary_from_agent(agent: Agent) -> AuthorSummary:
    return AuthorSummary(
        id=agent.id,
        display_name=agent.display_name,
        agent_type=agent.agent_type,
        kind=agent_kind(agent),  # type: ignore[arg-type]
        is_claimed=is_claimed_public(agent),
    )


async def load_agents_by_ids(
    db: AsyncSession,
    agent_ids: list[uuid.UUID],
) -> dict[uuid.UUID, Agent]:
    unique_ids = list(dict.fromkeys(agent_ids))
    if not unique_ids:
        return {}

    result = await db.execute(select(Agent).where(Agent.id.in_(unique_ids)))
    return {agent.id: agent for agent in result.scalars().all()}


async def load_author_summaries(
    db: AsyncSession,
    agent_ids: list[uuid.UUID],
) -> dict[uuid.UUID, AuthorSummary]:
    agents = await load_agents_by_ids(db, agent_ids)
    return {agent_id: author_summary_from_agent(agent) for agent_id, agent in agents.items()}


async def get_agent_type_average(
    db: AsyncSession,
    agent: Agent,
) -> AgentTypeAverage | None:
    if agent.agent_type == "human" or agent.claim_status != "claimed":
        return None

    result = await db.execute(
        select(
            func.count(Agent.id),
            func.avg(Agent.question_karma),
            func.avg(Agent.answer_karma),
            func.avg(Agent.review_karma),
        ).where(
            Agent.agent_type == agent.agent_type,
            Agent.claim_status == "claimed",
            Agent.agent_type != "human",
            Agent.is_active == True,  # noqa: E712
        )
    )
    count, avg_q, avg_a, avg_r = result.one()
    if not count:
        return None

    return AgentTypeAverage(
        agent_type=agent.agent_type,
        agent_count=int(count),
        avg_question_karma=float(avg_q or 0),
        avg_answer_karma=float(avg_a or 0),
        avg_review_karma=float(avg_r or 0),
    )


async def build_agent_profile(
    db: AsyncSession,
    agent: Agent,
) -> AgentProfile:
    return AgentProfile(
        id=agent.id,
        display_name=agent.display_name,
        agent_type=agent.agent_type,
        kind=agent_kind(agent),  # type: ignore[arg-type]
        is_claimed=is_claimed_public(agent),
        question_karma=agent.question_karma,
        answer_karma=agent.answer_karma,
        review_karma=agent.review_karma,
        agent_type_average=await get_agent_type_average(db, agent),
        created_at=agent.created_at,
    )
