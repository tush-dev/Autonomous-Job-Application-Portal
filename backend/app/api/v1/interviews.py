from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import structlog
from typing import Optional

from app.core.database import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.services.interview_service import InterviewService

router = APIRouter()
logger = structlog.get_logger()


@router.get("")
async def list_interviews(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    upcoming: Optional[bool] = None,
):
    service = InterviewService(db)
    interviews = await service.list_interviews(current_user.id, upcoming=upcoming)
    return interviews


@router.post("")
async def create_interview(
    application_id: str,
    scheduled_at: str,
    interview_type: Optional[str] = None,
    duration_minutes: int = 60,
    location: Optional[str] = None,
    meeting_link: Optional[str] = None,
    notes: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    service = InterviewService(db)
    interview = await service.create_interview(
        user_id=current_user.id,
        application_id=application_id,
        scheduled_at=scheduled_at,
        interview_type=interview_type,
        duration_minutes=duration_minutes,
        location=location,
        meeting_link=meeting_link,
        notes=notes,
    )
    return interview


@router.patch("/{interview_id}")
async def update_interview(
    interview_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    **kwargs,
):
    service = InterviewService(db)
    interview = await service.update_interview(current_user.id, interview_id, **kwargs)
    return interview
