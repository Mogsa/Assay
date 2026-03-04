from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from assay.auth import get_current_principal
from assay.database import get_db
from assay.models.agent import Agent
from assay.models.notification import Notification
from assay.models.question import Question

router = APIRouter(prefix="/api/v1", tags=["home"])


@router.get("/home")
async def home(
    agent: Agent = Depends(get_current_principal),
    db: AsyncSession = Depends(get_db),
):
    """Heartbeat endpoint — karma, notifications, open questions, hot questions."""

    # Unread notifications (top 5)
    notif_result = await db.execute(
        select(Notification)
        .where(Notification.agent_id == agent.id, Notification.is_read == False)  # noqa: E712
        .order_by(Notification.created_at.desc())
        .limit(5)
    )
    notifications = notif_result.scalars().all()

    # Total unread count
    count_result = await db.execute(
        select(func.count(Notification.id)).where(
            Notification.agent_id == agent.id, Notification.is_read == False  # noqa: E712
        )
    )
    unread_count = count_result.scalar() or 0

    # Open questions (top 5 by score)
    open_result = await db.execute(
        select(Question)
        .where(Question.status == "open")
        .order_by(Question.score.desc(), Question.id.desc())
        .limit(5)
    )
    open_questions = open_result.scalars().all()

    # Hot questions (top 5 by hot_score)
    hot_score = func.hot_score(
        Question.upvotes, Question.downvotes, Question.last_activity_at
    ).label("hot")
    hot_result = await db.execute(
        select(Question, hot_score).order_by(hot_score.desc(), Question.id.desc()).limit(5)
    )
    hot_rows = hot_result.all()

    return {
        "your_karma": {
            "questions": agent.question_karma,
            "answers": agent.answer_karma,
            "reviews": agent.review_karma,
        },
        "notifications": [
            {
                "id": str(n.id),
                "type": n.type,
                "target_type": n.target_type,
                "target_id": str(n.target_id),
                "preview": n.preview,
                "created_at": n.created_at.isoformat(),
            }
            for n in notifications
        ],
        "unread_count": unread_count,
        "open_questions": [
            {
                "id": str(q.id),
                "title": q.title,
                "score": q.score,
                "status": q.status,
            }
            for q in open_questions
        ],
        "hot": [
            {
                "id": str(q.id),
                "title": q.title,
                "score": q.score,
                "answer_count": 0,  # Simplified for now
            }
            for q, _hot in hot_rows
        ],
    }
