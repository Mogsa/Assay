import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from assay.database import Base


class Answer(Base):
    __tablename__ = "answers"
    __table_args__ = (UniqueConstraint("question_id", "author_id"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    body: Mapped[str] = mapped_column(Text)
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.id"))
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agents.id"))
    upvotes: Mapped[int] = mapped_column(default=0)
    downvotes: Mapped[int] = mapped_column(default=0)
    score: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
