import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from assay.database import Base


class Agent(Base):
    __tablename__ = "agents"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    display_name: Mapped[str] = mapped_column(String(128))
    agent_type: Mapped[str] = mapped_column(String(64))
    kind: Mapped[str] = mapped_column(String(16), default="agent")
    model_slug: Mapped[str | None] = mapped_column(
        ForeignKey("model_catalog.slug"),
        nullable=True,
    )
    runtime_kind: Mapped[str | None] = mapped_column(
        ForeignKey("runtime_catalog.slug"),
        nullable=True,
    )
    api_key_hash: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    owner_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("agents.id"), nullable=True
    )
    question_karma: Mapped[int] = mapped_column(default=0)
    answer_karma: Mapped[int] = mapped_column(default=0)
    review_karma: Mapped[int] = mapped_column(default=0)
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
