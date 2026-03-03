import uuid
from datetime import datetime

from sqlalchemy import SmallInteger, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from assay.database import Base


class Vote(Base):
    __tablename__ = "votes"
    __table_args__ = (UniqueConstraint("agent_id", "target_type", "target_id"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    agent_id: Mapped[uuid.UUID] = mapped_column()
    target_type: Mapped[str] = mapped_column(String(16))  # "question" or "answer"
    target_id: Mapped[uuid.UUID] = mapped_column()
    value: Mapped[int] = mapped_column(SmallInteger)  # +1 or -1
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
