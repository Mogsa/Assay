from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from assay.catalog import (
    ANTHROPIC_CLI_WARNING,
    CUSTOM_MODEL_WARNING,
    custom_model_slug,
    infer_runtime_kind,
    resolve_legacy_alias,
)
from assay.models.model_catalog import ModelCatalog
from assay.models.model_runtime_support import ModelRuntimeSupport
from assay.models.runtime_catalog import RuntimeCatalog
from assay.schemas.catalog import CatalogCustomModel


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


async def get_runtime_support(
    db: AsyncSession,
    *,
    model_slug: str,
    runtime_kind: str,
) -> ModelRuntimeSupport | None:
    result = await db.execute(
        select(ModelRuntimeSupport).where(
            ModelRuntimeSupport.model_slug == model_slug,
            ModelRuntimeSupport.runtime_slug == runtime_kind,
        )
    )
    return result.scalar_one_or_none()


async def validate_model_runtime_support(
    db: AsyncSession,
    *,
    model_slug: str,
    runtime_kind: str,
) -> tuple[ModelCatalog, RuntimeCatalog, ModelRuntimeSupport]:
    model = await get_model_or_404(db, model_slug)
    runtime = await get_runtime_or_404(db, runtime_kind)
    support = await get_runtime_support(
        db,
        model_slug=model_slug,
        runtime_kind=runtime_kind,
    )
    if support is None:
        raise HTTPException(
            status_code=400,
            detail="Selected runtime is not supported for the chosen model",
        )
    return model, runtime, support


async def ensure_custom_model_support(
    db: AsyncSession,
    *,
    custom_model: CatalogCustomModel,
    runtime_kind: str,
) -> tuple[ModelCatalog, RuntimeCatalog, ModelRuntimeSupport]:
    runtime = await get_runtime_or_404(db, runtime_kind)

    provider = custom_model.provider.strip()
    model_name = custom_model.model_name.strip()
    if not provider or not model_name:
        raise HTTPException(status_code=400, detail="custom_model provider and model_name are required")

    slug = custom_model_slug(provider, model_name)
    model = await db.get(ModelCatalog, slug)
    if model is None:
        model = ModelCatalog(
            slug=slug,
            provider=provider.lower(),
            family_slug=f"custom/{provider.lower()}",
            display_name=model_name,
            version_label="custom",
            is_active=True,
            is_canonical=False,
            supports_cli=runtime.transport == "cli",
            supports_api=runtime.transport == "api",
        )
        db.add(model)
        await db.flush()

    support = await get_runtime_support(db, model_slug=slug, runtime_kind=runtime.slug)
    if support is None:
        support = ModelRuntimeSupport(
            model_slug=slug,
            runtime_slug=runtime.slug,
            support_level="warning",
            terms_warning=CUSTOM_MODEL_WARNING,
        )
        db.add(support)
        await db.flush()

    return model, runtime, support


def default_support_metadata(*, model_slug: str, runtime_kind: str) -> tuple[str, str | None]:
    if model_slug.startswith("anthropic/") and runtime_kind == "claude-cli":
        return "warning", ANTHROPIC_CLI_WARNING
    return "supported", None


async def resolve_model_runtime_selection(
    db: AsyncSession,
    *,
    model_slug: str | None,
    runtime_kind: str | None,
    agent_type: str | None,
    custom_model: CatalogCustomModel | None = None,
) -> tuple[ModelCatalog, RuntimeCatalog, ModelRuntimeSupport]:
    if (model_slug is None) == (custom_model is None):
        raise HTTPException(
            status_code=400,
            detail="Provide exactly one of model_slug or custom_model",
        )

    if custom_model is not None:
        if runtime_kind is None:
            raise HTTPException(status_code=400, detail="runtime_kind is required for custom models")
        return await ensure_custom_model_support(
            db,
            custom_model=custom_model,
            runtime_kind=runtime_kind,
        )

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
    model, runtime, support = await validate_model_runtime_support(
        db,
        model_slug=resolved_model_slug,
        runtime_kind=resolved_runtime_kind,
    )
    if not support.support_level:
        support_level, terms_warning = default_support_metadata(
            model_slug=model.slug,
            runtime_kind=runtime.slug,
        )
        support.support_level = support_level
        support.terms_warning = terms_warning
        await db.flush()
    return model, runtime, support
