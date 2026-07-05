from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.models.user import User
from app.api.deps import get_current_user

router = APIRouter()
logger = structlog.get_logger()


@router.get("")
async def list_notifications(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        __import__("sqlalchemy").select(__import__("app.models.notification", fromlist=["Notification"]).Notification)
        .where(__import__("app.models.notification", fromlist=["Notification"]).Notification.user_id == current_user.id)
        .order_by(__import__("app.models.notification", fromlist=["Notification"]).Notification.created_at.desc())
        .limit(50)
    )
    notifications = result.scalars().all()
    return notifications


@router.patch("/{notification_id}/read")
async def mark_as_read(
    notification_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.models.notification import Notification
    result = await db.execute(
        __import__("sqlalchemy").select(Notification)
        .where(Notification.id == notification_id)
        .where(Notification.user_id == current_user.id)
    )
    notification = result.scalar_one_or_none()
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")

    notification.is_read = True
    await db.flush()
    return {"success": True}


@router.post("/read-all")
async def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.models.notification import Notification
    await db.execute(
        __import__("sqlalchemy").update(Notification)
        .where(Notification.user_id == current_user.id)
        .where(Notification.is_read == False)
        .values(is_read=True)
    )
    await db.flush()
    return {"success": True}
