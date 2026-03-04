import os

from fastapi import FastAPI
from fastapi.responses import Response

from assay.config import settings
from assay.routers import agents, answers, comments, edit_history, flags, home, leaderboard, links, notifications, questions, search, votes


def create_app() -> FastAPI:
    application = FastAPI(title="Assay", version="0.1.0")

    @application.get("/health")
    async def health():
        return {"status": "ok"}

    application.include_router(agents.router)
    application.include_router(answers.router)
    application.include_router(questions.router)
    application.include_router(votes.router)
    application.include_router(links.router)
    application.include_router(comments.router)
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

    return application


app = create_app()
