from pydantic import BaseModel


class CatalogRuntime(BaseModel):
    slug: str
    display_name: str
    transport: str
    auth_mode: str
    support_level: str = "supported"
    terms_warning: str | None = None


class CatalogCustomModel(BaseModel):
    provider: str
    model_name: str


class CatalogModel(BaseModel):
    slug: str
    provider: str
    family_slug: str
    display_name: str
    version_label: str
    is_canonical: bool
    supports_cli: bool
    supports_api: bool
    support_level: str = "supported"
    terms_warning: str | None = None
    supported_runtimes: list[str]
    supported_runtime_details: list[CatalogRuntime] = []
