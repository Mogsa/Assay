from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from assay.database import get_db
from assay.models.model_catalog import ModelCatalog
from assay.models.model_runtime_support import ModelRuntimeSupport
from assay.models.runtime_catalog import RuntimeCatalog
from assay.schemas.catalog import CatalogModel, CatalogRuntime

router = APIRouter(prefix="/api/v1/catalog", tags=["catalog"])


async def _runtime_map(db: AsyncSession) -> dict[str, list[str]]:
    result = await db.execute(select(ModelRuntimeSupport))
    support_rows = result.scalars().all()
    runtime_map: dict[str, list[str]] = {}
    for row in support_rows:
        runtime_map.setdefault(row.model_slug, []).append(row.runtime_slug)
    return runtime_map


@router.get("/models", response_model=list[CatalogModel])
async def list_models(db: AsyncSession = Depends(get_db)):
    runtime_map = await _runtime_map(db)
    result = await db.execute(
        select(ModelCatalog)
        .where(ModelCatalog.is_active == True)  # noqa: E712
        .order_by(ModelCatalog.provider.asc(), ModelCatalog.display_name.asc())
    )
    models = result.scalars().all()
    return [
        CatalogModel(
            slug=model.slug,
            provider=model.provider,
            family_slug=model.family_slug,
            display_name=model.display_name,
            version_label=model.version_label,
            is_canonical=model.is_canonical,
            supports_cli=model.supports_cli,
            supports_api=model.supports_api,
            supported_runtimes=runtime_map.get(model.slug, []),
        )
        for model in models
    ]


@router.get("/runtimes", response_model=list[CatalogRuntime])
async def list_runtimes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(RuntimeCatalog)
        .where(RuntimeCatalog.is_active == True)  # noqa: E712
        .order_by(RuntimeCatalog.display_name.asc())
    )
    runtimes = result.scalars().all()
    return [
        CatalogRuntime(
            slug=runtime.slug,
            display_name=runtime.display_name,
            transport=runtime.transport,
            auth_mode=runtime.auth_mode,
        )
        for runtime in runtimes
    ]


@router.get("/models/{model_slug}/runtimes", response_model=list[CatalogRuntime])
async def list_model_runtimes(
    model_slug: str,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(RuntimeCatalog)
        .join(
            ModelRuntimeSupport,
            ModelRuntimeSupport.runtime_slug == RuntimeCatalog.slug,
        )
        .where(
            ModelRuntimeSupport.model_slug == model_slug,
            RuntimeCatalog.is_active == True,  # noqa: E712
        )
        .order_by(RuntimeCatalog.display_name.asc())
    )
    runtimes = result.scalars().all()
    return [
        CatalogRuntime(
            slug=runtime.slug,
            display_name=runtime.display_name,
            transport=runtime.transport,
            auth_mode=runtime.auth_mode,
        )
        for runtime in runtimes
    ]
