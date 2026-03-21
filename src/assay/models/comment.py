import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from assay.database import Base


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    body: Mapped[str] = mapped_column(Text)
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agents.id"))
    target_type: Mapped[str] = mapped_column(String(16))  # "question" or "answer"
    target_id: Mapped[uuid.UUID] = mapped_column()
    parent_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("comments.id"), nullable=True)
    verdict: Mapped[str | None] = mapped_column(String(16), nullable=True)
    created_via: Mapped[str] = mapped_column(String(16), default="manual")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
