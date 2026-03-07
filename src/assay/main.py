import hashlib
import os
from functools import lru_cache

from fastapi import FastAPI
from fastapi.responses import Response
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from assay.config import settings
from assay.rate_limit import limiter
from assay.routers import (
    agents,
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


@lru_cache(maxsize=1)
def _load_skill_content() -> tuple[str, str]:
    skill_path = os.path.join(os.path.dirname(__file__), "..", "..", "static", "skill.md")
    with open(skill_path) as f:
        content = f.read()
    version = hashlib.sha256(content.encode()).hexdigest()[:12]
    return content, version


def create_app() -> FastAPI:
    application = FastAPI(title="Assay", version="0.1.0")
    application.state.limiter = limiter
    application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    @application.get("/health")
    async def health():
        return {"status": "ok"}

    application.include_router(auth.router)
    application.include_router(agents.router)
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
        content, _version = _load_skill_content()
        content = content.replace("{{BASE_URL}}", settings.base_url)
        return Response(content=content, media_type="text/markdown")

    @application.get("/api/v1/skill/version")
    async def skill_version():
        _content, version = _load_skill_content()
        return {"version": version}

    @application.get("/agent-guide")
    async def serve_agent_guide():
        guide_path = os.path.join(os.path.dirname(__file__), "..", "..", "static", "agent-guide.md")
        with open(guide_path) as f:
            content = f.read()
        content = content.replace("{BASE_URL}", settings.base_url)
        return Response(content=content, media_type="text/markdown")

    return application


app = create_app()
