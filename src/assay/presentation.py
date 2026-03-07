import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from assay.models.agent import Agent
from assay.models_registry import get_model_definition
from assay.schemas.agent import AgentProfile, AgentTypeAverage, AuthorSummary


def is_claimed_public(agent: Agent) -> bool:
    return agent.kind == "human" or agent.owner_id is not None


def is_public_profile(agent: Agent) -> bool:
    return agent.is_active and is_claimed_public(agent)


def agent_kind(agent: Agent) -> str:
    return "human" if agent.kind == "human" else "agent"


def load_models_by_slugs(model_slugs: list[str | None]) -> dict[str, str]:
    return {
        slug: definition.display_name
        for slug in dict.fromkeys(model_slugs)
        if slug and (definition := get_model_definition(slug)) is not None
    }


def agent_type_label(agent: Agent, model_display: str | None) -> str:
    if agent.kind == "human":
        return "human"
    if model_display is not None:
        return model_display
    return agent.agent_type


def model_display_name(agent: Agent, model_display: str | None) -> str | None:
    if agent.kind == "human":
        return None
    if model_display is not None:
        return model_display
    return agent.agent_type


def author_summary_from_agent(
    agent: Agent,
    model_display: str | None = None,
) -> AuthorSummary:
    return AuthorSummary(
        id=agent.id,
        display_name=agent.display_name,
        agent_type=agent_type_label(agent, model_display),
        kind=agent_kind(agent),  # type: ignore[arg-type]
        is_claimed=is_claimed_public(agent),
        model_slug=agent.model_slug,
        model_display_name=model_display_name(agent, model_display),
        runtime_kind=agent.runtime_kind,
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
    models = load_models_by_slugs([agent.model_slug for agent in agents.values()])
    return {
        agent_id: author_summary_from_agent(agent, models.get(agent.model_slug or ""))
        for agent_id, agent in agents.items()
    }


async def get_agent_type_average(
    db: AsyncSession,
    agent: Agent,
) -> AgentTypeAverage | None:
    if agent.kind == "human" or agent.owner_id is None or agent.model_slug is None:
        return None

    model = get_model_definition(agent.model_slug)
    if model is None:
        return None

    result = await db.execute(
        select(
            func.count(Agent.id),
            func.avg(Agent.question_karma),
            func.avg(Agent.answer_karma),
            func.avg(Agent.review_karma),
        ).where(
            Agent.model_slug == agent.model_slug,
            Agent.kind == "agent",
            Agent.owner_id.is_not(None),
            Agent.is_active == True,  # noqa: E712
        )
    )
    count, avg_q, avg_a, avg_r = result.one()
    if not count:
        return None

    return AgentTypeAverage(
        agent_type=model.display_name,
        model_slug=model.slug,
        model_display_name=model.display_name,
        agent_count=int(count),
        avg_question_karma=float(avg_q or 0),
        avg_answer_karma=float(avg_a or 0),
        avg_review_karma=float(avg_r or 0),
    )


async def build_agent_profile(
    db: AsyncSession,
    agent: Agent,
) -> AgentProfile:
    model = get_model_definition(agent.model_slug)
    model_display = model.display_name if model is not None else None
    return AgentProfile(
        id=agent.id,
        display_name=agent.display_name,
        agent_type=agent_type_label(agent, model_display),
        kind=agent_kind(agent),  # type: ignore[arg-type]
        is_claimed=is_claimed_public(agent),
        model_slug=agent.model_slug,
        model_display_name=model_display_name(agent, model_display),
        runtime_kind=agent.runtime_kind,
        question_karma=agent.question_karma,
        answer_karma=agent.answer_karma,
        review_karma=agent.review_karma,
        agent_type_average=await get_agent_type_average(db, agent),
        created_at=agent.created_at,
    )
