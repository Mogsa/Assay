from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from assay.catalog_service import resolve_model_runtime_selection
from assay.config import settings
from assay.database import get_db
from assay.models.agent import Agent
from assay.models.agent_auth_token import AgentAuthToken
from assay.models.cli_device_authorization import CliDeviceAuthorization
from assay.schemas.cli_auth import (
    CliDeviceApproveRequest,
    CliDeviceApprovalResponse,
    CliDevicePollRequest,
    CliDeviceStartRequest,
    CliDeviceStartResponse,
    CliDeviceTokenResponse,
    CliTokenRefreshRequest,
)
from assay.tokens import hash_token, new_opaque_token, new_user_code
from assay.auth import get_current_human
from assay.rate_limit import limiter

router = APIRouter(prefix="/api/v1/cli", tags=["cli-auth"])

DEVICE_CODE_TTL = timedelta(minutes=15)
DEVICE_CODE_INTERVAL = 5
ACCESS_TOKEN_TTL = timedelta(hours=1)
REFRESH_TOKEN_TTL = timedelta(days=30)


def _verification_uri() -> str:
    return f"{settings.base_url.rstrip('/')}/cli/device"


async def _issue_agent_tokens(
    db: AsyncSession,
    *,
    agent_id,
) -> tuple[str, str]:
    access_token, access_token_hash = new_opaque_token()
    refresh_token, refresh_token_hash = new_opaque_token()
    db.add(
        AgentAuthToken(
            agent_id=agent_id,
            token_hash=access_token_hash,
            token_kind="access",
            expires_at=datetime.now(timezone.utc) + ACCESS_TOKEN_TTL,
        )
    )
    db.add(
        AgentAuthToken(
            agent_id=agent_id,
            token_hash=refresh_token_hash,
            token_kind="refresh",
            expires_at=datetime.now(timezone.utc) + REFRESH_TOKEN_TTL,
        )
    )
    await db.flush()
    return access_token, refresh_token


@router.post("/device/start", response_model=CliDeviceStartResponse, status_code=201)
@limiter.limit("10/minute")
async def start_device_login(
    request: Request,
    response: Response,
    body: CliDeviceStartRequest,
    db: AsyncSession = Depends(get_db),
):
    model, runtime, support = await resolve_model_runtime_selection(
        db,
        model_slug=body.model_slug,
        runtime_kind=body.runtime_kind,
        agent_type=None,
        custom_model=body.custom_model,
    )
    if support.support_level == "warning" and not body.provider_terms_acknowledged:
        raise HTTPException(
            status_code=400,
            detail=support.terms_warning or "Provider terms acknowledgment is required",
        )
    device_code, device_code_hash = new_opaque_token()
    user_code, user_code_hash = new_user_code()
    verification_uri = _verification_uri()
    db.add(
        CliDeviceAuthorization(
            device_code_hash=device_code_hash,
            user_code_hash=user_code_hash,
            display_name=body.display_name,
            model_slug=model.slug,
            runtime_kind=runtime.slug,
            status="pending",
            expires_at=datetime.now(timezone.utc) + DEVICE_CODE_TTL,
        )
    )
    await db.flush()
    return CliDeviceStartResponse(
        device_code=device_code,
        user_code=user_code,
        verification_uri=verification_uri,
        verification_uri_complete=f"{verification_uri}?user_code={user_code}",
        expires_in=int(DEVICE_CODE_TTL.total_seconds()),
        interval=DEVICE_CODE_INTERVAL,
        support_level=support.support_level,
        terms_warning=support.terms_warning,
    )


@router.post("/device/poll")
async def poll_device_login(
    body: CliDevicePollRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CliDeviceAuthorization).where(
            CliDeviceAuthorization.device_code_hash == hash_token(body.device_code)
        )
    )
    auth_request = result.scalar_one_or_none()
    if auth_request is None:
        raise HTTPException(status_code=404, detail="invalid_device_code")

    now = datetime.now(timezone.utc)
    if auth_request.expires_at <= now:
        auth_request.status = "expired"
        await db.flush()
        raise HTTPException(status_code=410, detail="expired_token")
    if auth_request.status == "denied":
        raise HTTPException(status_code=403, detail="access_denied")
    if auth_request.status != "approved" or auth_request.agent_id is None:
        return JSONResponse(status_code=202, content={"status": "pending"})
    if auth_request.consumed_at is not None:
        raise HTTPException(status_code=410, detail="expired_token")

    agent = await db.get(Agent, auth_request.agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")

    access_token, refresh_token = await _issue_agent_tokens(db, agent_id=agent.id)
    auth_request.consumed_at = now
    await db.flush()
    return CliDeviceTokenResponse(
        status="approved",
        agent_id=agent.id,
        display_name=agent.display_name,
        model_slug=agent.model_slug or "",
        runtime_kind=agent.runtime_kind or "",
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=int(ACCESS_TOKEN_TTL.total_seconds()),
    )


@router.post("/device/approve", response_model=CliDeviceApprovalResponse)
async def approve_device_login(
    body: CliDeviceApproveRequest,
    owner: Agent = Depends(get_current_human),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CliDeviceAuthorization).where(
            CliDeviceAuthorization.user_code_hash == hash_token(body.user_code)
        )
    )
    auth_request = result.scalar_one_or_none()
    if auth_request is None:
        raise HTTPException(status_code=404, detail="Invalid user code")

    if auth_request.expires_at <= datetime.now(timezone.utc):
        auth_request.status = "expired"
        await db.flush()
        raise HTTPException(status_code=410, detail="Device code expired")
    if auth_request.status == "approved":
        raise HTTPException(status_code=409, detail="Device code already approved")
    if auth_request.status == "denied":
        raise HTTPException(status_code=409, detail="Device code already denied")

    model, runtime, _support = await resolve_model_runtime_selection(
        db,
        model_slug=auth_request.model_slug,
        runtime_kind=auth_request.runtime_kind,
        agent_type=None,
    )
    agent: Agent | None = None
    if body.agent_id is not None:
        agent = await db.get(Agent, body.agent_id)
        if agent is None or agent.owner_id != owner.id:
            raise HTTPException(status_code=404, detail="Agent not found")
        if agent.kind != "agent":
            raise HTTPException(status_code=400, detail="Only AI agents can be linked")
        if agent.model_slug != model.slug or agent.runtime_kind != runtime.slug:
            raise HTTPException(
                status_code=400,
                detail="Existing agent model/runtime does not match this device request",
            )
    else:
        agent = Agent(
            display_name=auth_request.display_name,
            agent_type=model.display_name,
            kind="agent",
            model_slug=model.slug,
            runtime_kind=runtime.slug,
            owner_id=owner.id,
        )
        db.add(agent)
        await db.flush()
        await db.refresh(agent)

    auth_request.status = "approved"
    auth_request.owner_id = owner.id
    auth_request.agent_id = agent.id
    auth_request.approved_at = datetime.now(timezone.utc)
    await db.flush()
    return CliDeviceApprovalResponse(
        status="approved",
        agent_id=agent.id,
        display_name=agent.display_name,
        model_slug=agent.model_slug or "",
        runtime_kind=agent.runtime_kind or "",
    )


@router.post("/device/deny")
async def deny_device_login(
    body: CliDeviceApproveRequest,
    owner: Agent = Depends(get_current_human),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CliDeviceAuthorization).where(
            CliDeviceAuthorization.user_code_hash == hash_token(body.user_code)
        )
    )
    auth_request = result.scalar_one_or_none()
    if auth_request is None:
        raise HTTPException(status_code=404, detail="Invalid user code")
    if auth_request.expires_at <= datetime.now(timezone.utc):
        auth_request.status = "expired"
        await db.flush()
        raise HTTPException(status_code=410, detail="Device code expired")
    if auth_request.status == "approved":
        raise HTTPException(status_code=409, detail="Device code already approved")

    auth_request.status = "denied"
    auth_request.owner_id = owner.id
    auth_request.denied_at = datetime.now(timezone.utc)
    await db.flush()
    return {"status": "denied"}


@router.post("/token/refresh", response_model=CliDeviceTokenResponse)
async def refresh_cli_token(
    body: CliTokenRefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    token_hash = hash_token(body.refresh_token)
    result = await db.execute(
        select(AgentAuthToken).where(
            AgentAuthToken.token_hash == token_hash,
            AgentAuthToken.token_kind == "refresh",
            AgentAuthToken.revoked_at.is_(None),
        )
    )
    refresh_token = result.scalar_one_or_none()
    if refresh_token is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    if refresh_token.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=401, detail="Refresh token expired")

    refresh_token.revoked_at = datetime.now(timezone.utc)
    agent = await db.get(Agent, refresh_token.agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")

    access_token, new_refresh_token = await _issue_agent_tokens(db, agent_id=agent.id)
    await db.flush()
    return CliDeviceTokenResponse(
        status="approved",
        agent_id=agent.id,
        display_name=agent.display_name,
        model_slug=agent.model_slug or "",
        runtime_kind=agent.runtime_kind or "",
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=int(ACCESS_TOKEN_TTL.total_seconds()),
    )
