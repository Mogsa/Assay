import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from assay.database import Base


class QuestionRead(Base):
    __tablename__ = "question_reads"
    __table_args__ = (
        UniqueConstraint("agent_id", "question_id", name="uq_question_reads_agent_question"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    agent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agents.id"))
    question_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("questions.id"))
    read_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
