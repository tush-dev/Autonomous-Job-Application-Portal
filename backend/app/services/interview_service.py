from typing import Optional
import uuid
from datetime import datetime
import structlog

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException
from app.core.notifier import create_notification
from app.models.interview import InterviewSchedule, InterviewStatus
from app.models.application import JobApplication
from app.models.job import Job, Company

logger = structlog.get_logger()


class InterviewService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_interviews(
        self, user_id: uuid.UUID, upcoming: Optional[bool] = None
    ) -> list[dict]:
        stmt = (
            select(InterviewSchedule)
            .options(
                selectinload(InterviewSchedule.application)
                .selectinload(JobApplication.job)
                .selectinload(Job.company)
            )
            .where(InterviewSchedule.user_id == user_id)
        )

        if upcoming:
            stmt = stmt.where(InterviewSchedule.scheduled_at >= datetime.utcnow())

        stmt = stmt.order_by(desc(InterviewSchedule.scheduled_at))
        result = await self.db.execute(stmt)
        interviews = result.scalars().all()
        return [self._to_dict(iv) for iv in interviews]

    def _to_dict(self, interview: InterviewSchedule) -> dict:
        job_title = ""
        company_name = ""
        if interview.application and interview.application.job:
            job_title = interview.application.job.title
            if interview.application.job.company:
                company_name = interview.application.job.company.name
        return {
            "id": str(interview.id),
            "application_id": str(interview.application_id),
            "user_id": str(interview.user_id),
            "interview_type": interview.interview_type,
            "scheduled_at": interview.scheduled_at.isoformat(),
            "duration_minutes": interview.duration_minutes,
            "location": interview.location,
            "meeting_link": interview.meeting_link,
            "notes": interview.notes,
            "reminder_sent": interview.reminder_sent,
            "status": interview.status.value if hasattr(interview.status, "value") else str(interview.status),
            "job_title": job_title,
            "company_name": company_name,
            "created_at": interview.created_at.isoformat() if hasattr(interview, "created_at") and interview.created_at else None,
            "updated_at": interview.updated_at.isoformat() if hasattr(interview, "updated_at") and interview.updated_at else None,
        }

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

        await create_notification(
            self.db, user_id, "interview_scheduled",
            f"Interview scheduled: {interview_type or 'General'}",
            body=f"Scheduled at {scheduled_at} for {duration_minutes} minutes",
            data={"interview_id": str(interview.id), "scheduled_at": scheduled_at},
        )
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
