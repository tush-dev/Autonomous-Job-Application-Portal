import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification


async def create_notification(
    db: AsyncSession,
    user_id: uuid.UUID,
    type: str,
    title: str,
    body: Optional[str] = None,
    data: Optional[dict] = None,
):
    notif = Notification(
        user_id=user_id,
        type=type,
        title=title,
        body=body,
        data=data,
    )
    db.add(notif)
    await db.flush()
    return notif
