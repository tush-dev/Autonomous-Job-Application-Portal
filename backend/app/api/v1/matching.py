from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
import structlog

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.models.user import User
from app.models.resume import Resume
from app.schemas.matching import DashboardResponse, CareerInsightResponse
from app.api.deps import get_current_user
from app.services.matching_service import MatchingService

router = APIRouter()
logger = structlog.get_logger()


async def _get_active_resume_id(user: User, db: AsyncSession) -> str:
    if user.active_resume_id:
        return str(user.active_resume_id)
    result = await db.execute(
        select(Resume.id)
        .where(Resume.user_id == user.id, Resume.parsing_status == "COMPLETED")
        .order_by(desc(Resume.created_at))
        .limit(1)
    )
    row = result.scalar_one_or_none()
    if not row:
        raise NotFoundException("No completed resume found. Upload and parse a resume first.")
    return str(row)


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    resume_id = await _get_active_resume_id(current_user, db)
    service = MatchingService(db)
    result = await service.get_dashboard(current_user.id, resume_id)
    return result


@router.get("/jobs/recommended", response_model=list)
async def get_recommended_jobs(
    limit: int = Query(default=10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    resume_id = await _get_active_resume_id(current_user, db)
    service = MatchingService(db)
    jobs = await service.get_recommended_jobs(current_user.id, resume_id, limit)
    return jobs


@router.get("/insights", response_model=CareerInsightResponse)
async def get_career_insights(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    resume_id = await _get_active_resume_id(current_user, db)
    service = MatchingService(db)
    insights = await service.generate_career_insights(current_user.id, resume_id)
    return insights


@router.post("/score")
async def score_jobs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    resume_id = await _get_active_resume_id(current_user, db)
    service = MatchingService(db)
    scored = await service.score_jobs_for_resume(current_user.id, resume_id)
    return {"scored": scored, "message": f"Scored {scored} jobs against your resume"}
