from pydantic import BaseModel


class CatalogRuntime(BaseModel):
    slug: str
    display_name: str
    transport: str
    auth_mode: str


class CatalogModel(BaseModel):
    slug: str
    provider: str
    family_slug: str
    display_name: str
    version_label: str
    is_canonical: bool
    supports_cli: bool
    supports_api: bool
    supported_runtimes: list[str]
