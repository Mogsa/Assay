from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from assay.database import Base


class RuntimeCatalog(Base):
    __tablename__ = "runtime_catalog"

    slug: Mapped[str] = mapped_column(String(64), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(128))
    transport: Mapped[str] = mapped_column(String(16))
    auth_mode: Mapped[str] = mapped_column(String(32))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
