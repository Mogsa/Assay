"""Rating model — R/N/G Likert evaluation of content."""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index, SmallInteger, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from assay.database import Base


class Rating(Base):
    __tablename__ = "ratings"
    __table_args__ = (
        UniqueConstraint("rater_id", "target_type", "target_id"),
        Index("idx_ratings_target", "target_type", "target_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    rater_id: Mapped[uuid.UUID] = mapped_column(index=True)
    target_type: Mapped[str] = mapped_column(String(16))  # "question" | "answer" | "comment"
    target_id: Mapped[uuid.UUID] = mapped_column()
    rigour: Mapped[int] = mapped_column(SmallInteger)
    novelty: Mapped[int] = mapped_column(SmallInteger)
    generativity: Mapped[int] = mapped_column(SmallInteger)
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
