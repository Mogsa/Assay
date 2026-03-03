import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from assay.database import Base


class Link(Base):
    __tablename__ = "links"
    __table_args__ = (
        UniqueConstraint(
            "source_type", "source_id", "target_type", "target_id", "link_type"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    source_type: Mapped[str] = mapped_column(String(16))  # "question" or "answer"
    source_id: Mapped[uuid.UUID] = mapped_column()
    target_type: Mapped[str] = mapped_column(String(16))  # "question" or "answer"
    target_id: Mapped[uuid.UUID] = mapped_column()
    link_type: Mapped[str] = mapped_column(String(16))  # references/extends/contradicts/solves
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("agents.id"))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
