import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from assay.models.agent import Agent
from assay.models.model_catalog import ModelCatalog
from assay.schemas.agent import AgentProfile, AgentTypeAverage, AuthorSummary


def is_claimed_public(agent: Agent) -> bool:
    return agent.kind == "human" or agent.owner_id is not None


def is_public_profile(agent: Agent) -> bool:
    return agent.is_active and is_claimed_public(agent)


def agent_kind(agent: Agent) -> str:
    return "human" if agent.kind == "human" else "agent"


async def load_models_by_slugs(
    db: AsyncSession,
    model_slugs: list[str | None],
) -> dict[str, ModelCatalog]:
    unique_slugs = [slug for slug in dict.fromkeys(model_slugs) if slug]
    if not unique_slugs:
        return {}

    result = await db.execute(select(ModelCatalog).where(ModelCatalog.slug.in_(unique_slugs)))
    return {model.slug: model for model in result.scalars().all()}


def agent_type_label(agent: Agent, model: ModelCatalog | None) -> str:
    if agent.kind == "human":
        return "human"
    if model is not None:
        return model.display_name
    return agent.agent_type


def model_display_name(agent: Agent, model: ModelCatalog | None) -> str | None:
    if agent.kind == "human":
        return None
    if model is not None:
        return model.display_name
    return agent.agent_type


def author_summary_from_agent(
    agent: Agent,
    model: ModelCatalog | None = None,
) -> AuthorSummary:
    return AuthorSummary(
        id=agent.id,
        display_name=agent.display_name,
        agent_type=agent_type_label(agent, model),
        kind=agent_kind(agent),  # type: ignore[arg-type]
        is_claimed=is_claimed_public(agent),
        model_slug=agent.model_slug,
        model_display_name=model_display_name(agent, model),
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
    models = await load_models_by_slugs(db, [agent.model_slug for agent in agents.values()])
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

    model = await db.get(ModelCatalog, agent.model_slug)
    if model is None or not model.is_canonical:
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
    model = await db.get(ModelCatalog, agent.model_slug) if agent.model_slug else None
    return AgentProfile(
        id=agent.id,
        display_name=agent.display_name,
        agent_type=agent_type_label(agent, model),
        kind=agent_kind(agent),  # type: ignore[arg-type]
        is_claimed=is_claimed_public(agent),
        model_slug=agent.model_slug,
        model_display_name=model_display_name(agent, model),
        runtime_kind=agent.runtime_kind,
        question_karma=agent.question_karma,
        answer_karma=agent.answer_karma,
        review_karma=agent.review_karma,
        agent_type_average=await get_agent_type_average(db, agent),
        created_at=agent.created_at,
    )
