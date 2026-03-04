import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from assay.database import get_db
from assay.models.agent import Agent
from assay.models.session import Session
from assay.schemas.auth import LoginRequest, LoginResponse, SignupRequest, SignupResponse

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

SESSION_MAX_AGE = 30 * 24 * 3600  # 30 days in seconds


def _create_session_cookie(response: JSONResponse, session_token: str) -> None:
    response.set_cookie(
        key="session",
        value=session_token,
        httponly=True,
        samesite="lax",
        max_age=SESSION_MAX_AGE,
    )


async def _create_session(db: AsyncSession, agent_id) -> str:
    session_token = secrets.token_urlsafe(32)
    session_hash = hashlib.sha256(session_token.encode()).hexdigest()
    session = Session(
        id=session_hash,
        agent_id=agent_id,
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=SESSION_MAX_AGE),
    )
    db.add(session)
    await db.flush()
    return session_token


@router.post("/signup", status_code=201)
async def signup(body: SignupRequest, db: AsyncSession = Depends(get_db)):
    password_hash = bcrypt.hashpw(body.password.encode(), bcrypt.gensalt()).decode()

    agent = Agent(
        display_name=body.display_name,
        agent_type="human",
        email=body.email,
        password_hash=password_hash,
    )
    db.add(agent)
    try:
        await db.flush()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="Email already registered")
    await db.refresh(agent)

    session_token = await _create_session(db, agent.id)
    await db.commit()

    data = SignupResponse(agent_id=agent.id, display_name=agent.display_name)
    response = JSONResponse(content=data.model_dump(mode="json"), status_code=201)
    _create_session_cookie(response, session_token)
    return response


@router.post("/login")
async def login(body: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Agent).where(Agent.email == body.email))
    agent = result.scalar_one_or_none()
    if agent is None or agent.password_hash is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not bcrypt.checkpw(body.password.encode(), agent.password_hash.encode()):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    session_token = await _create_session(db, agent.id)
    await db.commit()

    data = LoginResponse(agent_id=agent.id, display_name=agent.display_name)
    response = JSONResponse(content=data.model_dump(mode="json"))
    _create_session_cookie(response, session_token)
    return response


@router.post("/logout")
async def logout(request: Request, db: AsyncSession = Depends(get_db)):
    session_token = request.cookies.get("session")
    if not session_token:
        raise HTTPException(status_code=401, detail="No session")

    session_hash = hashlib.sha256(session_token.encode()).hexdigest()
    result = await db.execute(select(Session).where(Session.id == session_hash))
    session = result.scalar_one_or_none()
    if session:
        await db.delete(session)
        await db.commit()

    response = JSONResponse(content={"status": "logged_out"})
    response.delete_cookie("session")
    return response
