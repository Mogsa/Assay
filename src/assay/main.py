from fastapi import FastAPI

from assay.routers import agents, answers, questions, votes


def create_app() -> FastAPI:
    application = FastAPI(title="Assay", version="0.1.0")

    @application.get("/health")
    async def health():
        return {"status": "ok"}

    application.include_router(agents.router)
    application.include_router(answers.router)
    application.include_router(questions.router)
    application.include_router(votes.router)

    return application


app = create_app()
