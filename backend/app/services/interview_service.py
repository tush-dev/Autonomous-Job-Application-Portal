from typing import Optional
import uuid
from datetime import datetime
import structlog

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.exceptions import NotFoundException
from app.models.interview import InterviewSchedule, InterviewStatus

logger = structlog.get_logger()


class InterviewService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_interviews(
        self, user_id: uuid.UUID, upcoming: Optional[bool] = None
    ) -> list:
        stmt = select(InterviewSchedule).where(InterviewSchedule.user_id == user_id)

        if upcoming:
            stmt = stmt.where(InterviewSchedule.scheduled_at >= datetime.utcnow())

        stmt = stmt.order_by(desc(InterviewSchedule.scheduled_at))
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create_interview(
        self,
        user_id: uuid.UUID,
        application_id: str,
        scheduled_at: str,
        interview_type: Optional[str] = None,
        duration_minutes: int = 60,
        location: Optional[str] = None,
        meeting_link: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> InterviewSchedule:
        from dateutil import parser

        interview = InterviewSchedule(
            application_id=application_id,
            user_id=user_id,
            interview_type=interview_type,
            scheduled_at=parser.parse(scheduled_at),
            duration_minutes=duration_minutes,
            location=location,
            meeting_link=meeting_link,
            notes=notes,
            status=InterviewStatus.SCHEDULED,
        )
        self.db.add(interview)
        await self.db.flush()
        return interview

    async def update_interview(
        self, user_id: uuid.UUID, interview_id: str, **kwargs
    ) -> InterviewSchedule:
        result = await self.db.execute(
            select(InterviewSchedule).where(
                InterviewSchedule.id == interview_id,
                InterviewSchedule.user_id == user_id,
            )
        )
        interview = result.scalar_one_or_none()
        if not interview:
            raise NotFoundException("Interview not found")

        for key, value in kwargs.items():
            if hasattr(interview, key) and value is not None:
                setattr(interview, key, value)

        await self.db.flush()
        return interview
