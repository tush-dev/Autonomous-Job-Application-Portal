from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Integer
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
    from sqlalchemy import select, func
    from app.models.application import JobApplication
    from app.models.user import User as UserModel

    total_users = (await db.execute(select(func.count(UserModel.id)))).scalar() or 0
    total_applications = (await db.execute(select(func.count(JobApplication.id)))).scalar() or 0
    submitted = (await db.execute(
        select(func.count(JobApplication.id)).where(JobApplication.status == "applied")
    )).scalar() or 0
    interviews = (await db.execute(
        select(func.count(JobApplication.id)).where(JobApplication.status == "interview")
    )).scalar() or 0
    offers = (await db.execute(
        select(func.count(JobApplication.id)).where(JobApplication.status == "offer")
    )).scalar() or 0

    return {
        "total_users": total_users,
        "total_applications": total_applications,
        "submitted": submitted,
        "interviews": interviews,
        "offers": offers,
    }


@router.get("/logs")
async def get_logs(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select, desc
    from app.models.misc import ActivityLog

    result = await db.execute(
        select(ActivityLog).order_by(desc(ActivityLog.created_at)).limit(100)
    )
    logs = result.scalars().all()
    return {"logs": logs, "total": len(logs)}


@router.get("/audit-logs")
async def get_audit_logs(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select, desc
    from app.models.misc import AuditLog

    result = await db.execute(
        select(AuditLog).order_by(desc(AuditLog.created_at)).limit(100)
    )
    logs = result.scalars().all()
    return {"logs": logs, "total": len(logs)}


@router.get("/ai-usage")
async def get_ai_usage(
    admin: User = Depends(get_current_admin),
    db: AsyncSession = Depends(get_db),
):
    from sqlalchemy import select, func, desc
    from app.models.misc import AIRequest

    result = await db.execute(
        select(
            AIRequest.model,
            func.count(AIRequest.id).label("requests"),
            func.avg(AIRequest.latency_ms).label("avg_latency_ms"),
            func.sum(AIRequest.prompt_tokens).label("total_prompt_tokens"),
            func.sum(AIRequest.completion_tokens).label("total_completion_tokens"),
            func.sum(AIRequest.cost_cents).label("total_cost_cents"),
            func.sum(func.cast(AIRequest.cache_hit, Integer)).label("cache_hits"),
        ).group_by(AIRequest.model)
    )
    rows = result.all()
    return {
        "usage": [
            {
                "model": r.model,
                "requests": r.requests,
                "avg_latency_ms": round(float(r.avg_latency_ms), 1) if r.avg_latency_ms else 0,
                "total_prompt_tokens": r.total_prompt_tokens or 0,
                "total_completion_tokens": r.total_completion_tokens or 0,
                "total_cost_cents": r.total_cost_cents or 0,
                "cache_hits": r.cache_hits or 0,
            }
            for r in rows
        ]
    }
