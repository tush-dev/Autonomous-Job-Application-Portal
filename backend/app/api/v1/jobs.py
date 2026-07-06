from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
import structlog

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.models.user import User
from app.schemas.job import JobSearchRequest, JobSearchResponse, JobResponse
from app.api.deps import get_current_user
from app.services.job_service import JobService

router = APIRouter()
logger = structlog.get_logger()


@router.post("/search", response_model=JobSearchResponse)
async def search_jobs(
    request: JobSearchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    logger.info("search_jobs_request",
                 query=request.query,
                 min_match_score=request.min_match_score,
                 sort_by=request.sort_by,
                 page=request.page)
    service = JobService(db)
    result = await service.search_jobs(
        user_id=current_user.id,
        query=request.query,
        location=request.location,
        remote=request.remote,
        salary_min=request.salary_min,
        salary_max=request.salary_max,
        sources=request.sources,
        exclude_applied=request.exclude_applied,
        page=request.page,
        page_size=request.page_size,
        min_match_score=request.min_match_score,
        sort_by=request.sort_by,
    )
    return result


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = JobService(db)
    job = await service.get_job(current_user.id, job_id)
    return job


@router.post("/{job_id}/save")
async def save_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = JobService(db)
    await service.save_job(current_user.id, job_id)
    return {"success": True, "message": "Job saved"}


@router.delete("/{job_id}/save")
async def unsave_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = JobService(db)
    await service.unsave_job(current_user.id, job_id)
    return {"success": True, "message": "Job unsaved"}


@router.get("/saved/list", response_model=list[JobResponse])
async def list_saved_jobs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = JobService(db)
    jobs = await service.list_saved_jobs(current_user.id)
    return jobs
