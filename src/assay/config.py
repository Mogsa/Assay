from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://assay:assay@localhost:5432/assay"
    base_url: str = "http://localhost:8000"  # Configurable for skill.md

    model_config = {"env_prefix": "ASSAY_"}


settings = Settings()
