from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.core.exceptions import ForbiddenException
from app.models.user import User
from app.api.deps import get_current_admin

router = APIRouter()
logger = structlog.get_logger()


@router.get("/users")
async def list_users(
    page: int = 1,
    page_size: int = 20,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select, func
    from app.models.user import User as UserModel

    offset = (page - 1) * page_size
    result = await db.execute(
        select(UserModel).offset(offset).limit(page_size).order_by(UserModel.created_at.desc())
    )
    users = result.scalars().all()

    count_result = await db.execute(select(func.count(UserModel.id)))
    total = count_result.scalar()

    return {"users": users, "total": total, "page": page, "page_size": page_size}


@router.patch("/users/{user_id}")
async def update_user(
    user_id: str,
    is_active: bool = None,
    role: str = None,
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select
    from app.models.user import User as UserModel

    result = await db.execute(select(UserModel).where(UserModel.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if is_active is not None:
        user.is_active = is_active
    if role is not None:
        user.role = role

    await db.flush()
    return {"success": True}


@router.get("/analytics")
async def get_analytics(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    return {"message": "Admin analytics endpoint (to be implemented)"}


@router.get("/logs")
async def get_logs(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    return {"message": "System logs endpoint (to be implemented)"}


@router.get("/audit-logs")
async def get_audit_logs(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    return {"message": "Audit logs endpoint (to be implemented)"}


@router.get("/ai-usage")
async def get_ai_usage(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    return {"message": "AI usage endpoint (to be implemented)"}
