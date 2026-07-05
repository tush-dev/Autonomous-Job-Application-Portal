from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from typing import Optional

from app.core.database import get_db
from app.core.exceptions import NotFoundException
from app.models.user import User
from app.schemas.application import (
    ApplicationCreateRequest, ApplicationSubmitRequest, ApplicationResponse,
    ApplicationStatsResponse, TimelineEvent,
)
from app.api.deps import get_current_user
from app.services.application_service import ApplicationService

router = APIRouter()
logger = structlog.get_logger()


@router.get("", response_model=list[ApplicationResponse])
async def list_applications(
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ApplicationService(db)
    applications = await service.list_applications(current_user.id, status_filter)
    return applications


@router.get("/stats", response_model=ApplicationStatsResponse)
async def get_application_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ApplicationService(db)
    stats = await service.get_stats(current_user.id)
    return stats


@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ApplicationService(db)
    application = await service.get_application(current_user.id, application_id)
    return application


@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    request: ApplicationCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ApplicationService(db)
    application = await service.create_application(
        user_id=current_user.id,
        job_id=request.job_id,
        resume_id=request.resume_id,
        approval_required=request.approval_required,
        notes=request.notes,
    )
    return application


@router.post("/{application_id}/submit", response_model=ApplicationResponse)
async def submit_application(
    application_id: str,
    request: ApplicationSubmitRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ApplicationService(db)
    application = await service.submit_application(
        user_id=current_user.id,
        application_id=application_id,
        cover_letter_id=request.cover_letter_id,
        generated_resume_id=request.generated_resume_id,
        additional_answers=request.additional_answers,
    )
    return application


@router.post("/{application_id}/retry", response_model=ApplicationResponse)
async def retry_application(
    application_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ApplicationService(db)
    application = await service.retry_application(current_user.id, application_id)
    return application


@router.delete("/{application_id}")
async def delete_application(
    application_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ApplicationService(db)
    await service.delete_application(current_user.id, application_id)
    return {"success": True, "message": "Application deleted"}


@router.get("/{application_id}/timeline", response_model=list[TimelineEvent])
async def get_application_timeline(
    application_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = ApplicationService(db)
    timeline = await service.get_timeline(current_user.id, application_id)
    return timeline
