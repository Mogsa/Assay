FROM python:3.12-slim

WORKDIR /app

# Cache dependencies — only re-runs pip when pyproject.toml changes
COPY pyproject.toml ./
RUN pip install --no-cache-dir fastapi[standard]>=0.115 uvicorn[standard]>=0.34 \
    sqlalchemy[asyncio]>=2.0 asyncpg>=0.30 alembic>=1.14 \
    pydantic-settings>=2.7 bcrypt>=4.0 slowapi>=0.1.9 httpx>=0.28

COPY . .
RUN pip install --no-cache-dir -e .
RUN chmod +x /app/docker/api-entrypoint.sh

ENTRYPOINT ["/app/docker/api-entrypoint.sh"]
CMD ["uvicorn", "assay.main:app", "--host", "0.0.0.0", "--port", "8000"]
