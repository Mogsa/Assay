from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from assay.database import Base


class ModelCatalog(Base):
    __tablename__ = "model_catalog"

    slug: Mapped[str] = mapped_column(String(128), primary_key=True)
    provider: Mapped[str] = mapped_column(String(64))
    family_slug: Mapped[str] = mapped_column(String(128))
    display_name: Mapped[str] = mapped_column(String(128))
    version_label: Mapped[str] = mapped_column(String(64))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_canonical: Mapped[bool] = mapped_column(Boolean, default=True)
    supports_cli: Mapped[bool] = mapped_column(Boolean, default=True)
    supports_api: Mapped[bool] = mapped_column(Boolean, default=False)
