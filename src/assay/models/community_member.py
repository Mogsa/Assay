import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, PrimaryKeyConstraint, String, func
from sqlalchemy.orm import Mapped, mapped_column

from assay.database import Base


class CommunityMember(Base):
    __tablename__ = "community_members"
    __table_args__ = (
        PrimaryKeyConstraint("community_id", "agent_id"),
    )

    community_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("communities.id"))
    agent_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("agents.id"), index=True)
    role: Mapped[str] = mapped_column(String(16), server_default="subscriber")
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
