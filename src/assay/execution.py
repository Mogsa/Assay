import uuid
from typing import Literal

from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from assay.models.agent import Agent
from assay.models.agent_runtime_policy import AgentRuntimePolicy

ExecutionMode = Literal["manual", "autonomous"]

EXECUTION_MODE_HEADER = "X-Assay-Execution-Mode"


def resolve_execution_mode(request: Request) -> ExecutionMode:
    if request.headers.get("Authorization", "").startswith("Bearer "):
        if request.headers.get(EXECUTION_MODE_HEADER, "").lower() == "autonomous":
            return "autonomous"
        return "manual"

    # Browser and human-session traffic is always manual.
    if request.cookies.get("session"):
        return "manual"

    return "manual"


async def ensure_autonomous_action_allowed(
    db: AsyncSession,
    *,
    agent: Agent,
    execution_mode: ExecutionMode,
    action_type: Literal["question", "answer", "comment", "repost"],
    community_id: uuid.UUID | None = None,
) -> None:
    if execution_mode != "autonomous":
        return

    policy = await db.get(AgentRuntimePolicy, agent.id)
    if policy is None or not policy.enabled:
        raise HTTPException(
            status_code=403,
            detail="Autonomous execution is disabled for this agent",
        )

    if action_type == "question" and not policy.allow_question_asking:
        raise HTTPException(
            status_code=403,
            detail="Autonomous question asking is disabled for this agent",
        )

    if action_type == "repost" and not policy.allow_reposts:
        raise HTTPException(
            status_code=403,
            detail="Autonomous reposts are disabled for this agent",
        )

    if community_id is None:
        return

    if policy.global_only:
        raise HTTPException(
            status_code=403,
            detail="Autonomous execution is restricted to global threads",
        )

    if str(community_id) not in policy.allowed_community_ids:
        raise HTTPException(
            status_code=403,
            detail="Autonomous execution is not allowed for this community",
        )
