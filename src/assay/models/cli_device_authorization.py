import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column

from assay.database import Base


class CliDeviceAuthorization(Base):
    __tablename__ = "cli_device_authorizations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    device_code_hash: Mapped[str] = mapped_column(String(64), unique=True)
    user_code_hash: Mapped[str] = mapped_column(String(64), unique=True)
    display_name: Mapped[str] = mapped_column(String(128))
    model_slug: Mapped[str] = mapped_column(
        String(128),
        ForeignKey("model_catalog.slug"),
    )
    runtime_kind: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("runtime_catalog.slug"),
    )
    status: Mapped[str] = mapped_column(String(16), default="pending")
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("agents.id"),
        nullable=True,
    )
    agent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("agents.id"),
        nullable=True,
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    denied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    consumed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    __table_args__ = (
        Index("idx_cli_device_authorizations_expiry", "expires_at"),
        Index("idx_cli_device_authorizations_status", "status"),
    )
