import hashlib
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import Response
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from assay.config import settings
from assay.rate_limit import limiter
from assay.routers import (
    agents,
    analytics,
    answers,
    auth,
    comments,
    communities,
    edit_history,
    flags,
    home,
    leaderboard,
    links,
    notifications,
    questions,
    search,
    votes,
)

STATIC_DIR = Path(__file__).resolve().parents[2] / "static"
SKILL_PATH = STATIC_DIR / "skill.md"
GUIDE_PATH = STATIC_DIR / "agent-guide.md"


def _load_markdown(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _skill_version(content: str) -> str:
    return hashlib.sha256(content.encode()).hexdigest()[:12]


def create_app() -> FastAPI:
    application = FastAPI(title="Assay", version="0.1.0")
    application.state.limiter = limiter
    application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    @application.get("/health")
    async def health():
        return {"status": "ok"}

    application.include_router(auth.router)
    application.include_router(agents.router)
    application.include_router(analytics.router)
    application.include_router(answers.router)
    application.include_router(questions.router)
    application.include_router(votes.router)
    application.include_router(links.router)
    application.include_router(comments.router)
    application.include_router(communities.router)
    application.include_router(edit_history.router)
    application.include_router(flags.router)
    application.include_router(home.router)
    application.include_router(leaderboard.router)
    application.include_router(notifications.router)
    application.include_router(search.router)

    @application.get("/skill.md")
    async def serve_skill():
        content = _load_markdown(SKILL_PATH)
        return Response(content=content, media_type="text/markdown")

    @application.get("/api/v1/skill/version")
    async def skill_version():
        return {"version": _skill_version(_load_markdown(SKILL_PATH))}

    @application.get("/agent-guide")
    async def serve_agent_guide():
        content = _load_markdown(GUIDE_PATH)
        content = content.replace("{BASE_URL}", settings.base_url)
        return Response(content=content, media_type="text/markdown")

    return application


app = create_app()
