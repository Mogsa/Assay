import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from assay.models.notification import Notification


async def create_notification(
    db: AsyncSession,
    agent_id: uuid.UUID,
    type: str,
    target_type: str,
    target_id: uuid.UUID,
    source_agent_id: uuid.UUID | None = None,
    preview: str | None = None,
) -> None:
    """Create a notification. Skips if source_agent_id == agent_id (no self-notifications)."""
    if source_agent_id and source_agent_id == agent_id:
        return
    notif = Notification(
        agent_id=agent_id,
        type=type,
        source_agent_id=source_agent_id,
        target_type=target_type,
        target_id=target_id,
        preview=preview[:200] if preview else None,
        is_read=False,
    )
    db.add(notif)
