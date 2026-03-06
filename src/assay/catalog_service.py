from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from assay.catalog import infer_runtime_kind, resolve_legacy_alias
from assay.models.model_catalog import ModelCatalog
from assay.models.model_runtime_support import ModelRuntimeSupport
from assay.models.runtime_catalog import RuntimeCatalog


async def get_model_or_404(db: AsyncSession, slug: str) -> ModelCatalog:
    model = await db.get(ModelCatalog, slug)
    if model is None or not model.is_active:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


async def get_runtime_or_404(db: AsyncSession, slug: str) -> RuntimeCatalog:
    runtime = await db.get(RuntimeCatalog, slug)
    if runtime is None or not runtime.is_active:
        raise HTTPException(status_code=404, detail="Runtime not found")
    return runtime


async def validate_model_runtime_support(
    db: AsyncSession,
    *,
    model_slug: str,
    runtime_kind: str,
) -> tuple[ModelCatalog, RuntimeCatalog]:
    model = await get_model_or_404(db, model_slug)
    runtime = await get_runtime_or_404(db, runtime_kind)
    supported = await db.execute(
        select(ModelRuntimeSupport).where(
            ModelRuntimeSupport.model_slug == model_slug,
            ModelRuntimeSupport.runtime_slug == runtime_kind,
        )
    )
    if supported.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=400,
            detail="Selected runtime is not supported for the chosen model",
        )
    return model, runtime


async def resolve_model_runtime_selection(
    db: AsyncSession,
    *,
    model_slug: str | None,
    runtime_kind: str | None,
    agent_type: str | None,
) -> tuple[ModelCatalog, RuntimeCatalog]:
    resolved_model_slug = model_slug
    if resolved_model_slug is None and agent_type:
        resolved_model_slug = resolve_legacy_alias(agent_type)
    if resolved_model_slug is None:
        raise HTTPException(
            status_code=400,
            detail="model_slug is required for non-human agents",
        )

    resolved_runtime_kind = runtime_kind or infer_runtime_kind(
        model_slug=resolved_model_slug,
        agent_type=agent_type,
    )
    return await validate_model_runtime_support(
        db,
        model_slug=resolved_model_slug,
        runtime_kind=resolved_runtime_kind,
    )
