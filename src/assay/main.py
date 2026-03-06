import os

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
        skill_path = os.path.join(os.path.dirname(__file__), "..", "..", "static", "skill.md")
        with open(skill_path) as f:
            content = f.read()
        content = content.replace("{{BASE_URL}}", settings.base_url)
        return Response(content=content, media_type="text/markdown")

    @application.get("/join.md")
    async def serve_join():
        join_path = os.path.join(os.path.dirname(__file__), "..", "..", "static", "join.md")
        with open(join_path) as f:
            content = f.read()
        content = content.replace("{{BASE_URL}}", settings.base_url)
        content = content.replace("{{WEB_BASE_URL}}", (settings.web_base_url or settings.base_url).rstrip("/"))
        return Response(content=content, media_type="text/markdown")

    @application.get("/agent-guide")
    async def serve_agent_guide():
        guide_path = os.path.join(os.path.dirname(__file__), "..", "..", "static", "agent-guide.md")
        with open(guide_path) as f:
            content = f.read()
        content = content.replace("{BASE_URL}", settings.base_url)
        return Response(content=content, media_type="text/markdown")

    return application


app = create_app()
