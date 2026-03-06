from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from assay.database import Base


class ModelRuntimeSupport(Base):
    __tablename__ = "model_runtime_support"

    model_slug: Mapped[str] = mapped_column(
        String(128),
        ForeignKey("model_catalog.slug"),
        primary_key=True,
    )
    runtime_slug: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("runtime_catalog.slug"),
        primary_key=True,
    )
