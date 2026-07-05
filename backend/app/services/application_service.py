from typing import Optional
import uuid
from datetime import datetime, timezone
import structlog

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_

from app.core.exceptions import NotFoundException, ValidationException
from app.models.user import User
from app.models.application import (
    JobApplication, ApplicationStatus, ApplicationTimeline,
    CoverLetter, CoverLetterTone,
)
from app.models.job import Job
from app.schemas.application import (
    ApplicationResponse, ApplicationStatsResponse, TimelineEvent,
    CoverLetterResponse,
)

logger = structlog.get_logger()


class ApplicationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_applications(
        self, user_id: uuid.UUID, status_filter: Optional[str] = None
    ) -> list[ApplicationResponse]:
        stmt = select(JobApplication).where(JobApplication.user_id == user_id)

        if status_filter:
            stmt = stmt.where(JobApplication.status == status_filter)

        stmt = stmt.order_by(desc(JobApplication.created_at))
        result = await self.db.execute(stmt)
        applications = result.scalars().all()
        return [await self._to_response(app) for app in applications]

    async def get_application(
        self, user_id: uuid.UUID, application_id: str
    ) -> ApplicationResponse:
        result = await self.db.execute(
            select(JobApplication).where(
                JobApplication.id == application_id,
                JobApplication.user_id == user_id,
            )
        )
        app = result.scalar_one_or_none()
        if not app:
            raise NotFoundException("Application not found")
        return await self._to_response(app)

    async def create_application(
        self,
        user_id: uuid.UUID,
        job_id: str,
        resume_id: str,
        approval_required: bool = True,
        notes: Optional[str] = None,
    ) -> ApplicationResponse:
        job_result = await self.db.execute(select(Job).where(Job.id == job_id))
        job = job_result.scalar_one_or_none()
        if not job:
            raise NotFoundException("Job not found")

        application = JobApplication(
            user_id=user_id,
            job_id=job_id,
            resume_id=resume_id,
            status=ApplicationStatus.DRAFT,
            approval_required=approval_required,
            notes=notes,
        )
        self.db.add(application)

        timeline = ApplicationTimeline(
            application_id=application.id,
            event_type="created",
            description="Application draft created",
        )
        self.db.add(timeline)
        await self.db.flush()

        return await self._to_response(application)

    async def submit_application(
        self,
        user_id: uuid.UUID,
        application_id: str,
        cover_letter_id: Optional[str] = None,
        generated_resume_id: Optional[str] = None,
        additional_answers: Optional[dict] = None,
    ) -> ApplicationResponse:
        result = await self.db.execute(
            select(JobApplication).where(
                JobApplication.id == application_id,
                JobApplication.user_id == user_id,
            )
        )
        app = result.scalar_one_or_none()
        if not app:
            raise NotFoundException("Application not found")

        if app.status != ApplicationStatus.DRAFT:
            raise ValidationException("Application is not in draft status")

        if app.approval_required and not app.approved_at:
            raise ValidationException("Application needs approval before submission")

        app.status = ApplicationStatus.APPLIED
        app.applied_at = datetime.now(timezone.utc)

        timeline = ApplicationTimeline(
            application_id=app.id,
            event_type="submitted",
            description="Application submitted",
            metadata={"additional_answers": additional_answers},
        )
        self.db.add(timeline)
        await self.db.flush()

        return await self._to_response(app)

    async def retry_application(
        self, user_id: uuid.UUID, application_id: str
    ) -> ApplicationResponse:
        result = await self.db.execute(
            select(JobApplication).where(
                JobApplication.id == application_id,
                JobApplication.user_id == user_id,
            )
        )
        app = result.scalar_one_or_none()
        if not app:
            raise NotFoundException("Application not found")

        if app.status != ApplicationStatus.FAILED:
            raise ValidationException("Only failed applications can be retried")

        app.status = ApplicationStatus.APPLIED

        timeline = ApplicationTimeline(
            application_id=app.id,
            event_type="retried",
            description="Application retry initiated",
        )
        self.db.add(timeline)
        await self.db.flush()

        return await self._to_response(app)

    async def delete_application(self, user_id: uuid.UUID, application_id: str):
        result = await self.db.execute(
            select(JobApplication).where(
                JobApplication.id == application_id,
                JobApplication.user_id == user_id,
            )
        )
        app = result.scalar_one_or_none()
        if not app:
            raise NotFoundException("Application not found")
        await self.db.delete(app)
        await self.db.flush()

    async def get_timeline(
        self, user_id: uuid.UUID, application_id: str
    ) -> list[TimelineEvent]:
        result = await self.db.execute(
            select(ApplicationTimeline)
            .where(ApplicationTimeline.application_id == application_id)
            .order_by(desc(ApplicationTimeline.created_at))
        )
        events = result.scalars().all()
        return [TimelineEvent.model_validate(e) for e in events]

    async def get_stats(self, user_id: uuid.UUID) -> ApplicationStatsResponse:
        result = await self.db.execute(
            select(
                func.count(JobApplication.id),
                func.sum(
                    func.cast(JobApplication.status == ApplicationStatus.APPLIED.value, int)
                ),
            ).where(JobApplication.user_id == user_id)
        )
        row = result.one()
        total = row[0] or 0

        stats = {"total": total}
        for status in ApplicationStatus:
            count_result = await self.db.execute(
                select(func.count(JobApplication.id)).where(
                    JobApplication.user_id == user_id,
                    JobApplication.status == status,
                )
            )
            stats[status.value] = count_result.scalar() or 0

        total_applied = stats.get("applied", 0)
        total_interview = stats.get("interview", 0)
        total_offer = stats.get("offer", 0)

        return ApplicationStatsResponse(
            total=total,
            applied=stats.get("applied", 0),
            screening=stats.get("screening", 0),
            interview=total_interview,
            offer=total_offer,
            rejected=stats.get("rejected", 0),
            failed=stats.get("failed", 0),
            interview_rate=(total_interview / total_applied * 100) if total_applied > 0 else 0,
            offer_rate=(total_offer / total_applied * 100) if total_applied > 0 else 0,
        )

    async def _to_response(self, app: JobApplication) -> ApplicationResponse:
        cover_letter = None
        if app.cover_letter:
            cover_letter = CoverLetterResponse(
                id=str(app.cover_letter.id),
                content=app.cover_letter.content,
                tone=app.cover_letter.tone.value if hasattr(app.cover_letter.tone, 'value') else str(app.cover_letter.tone),
                word_count=app.cover_letter.word_count,
                created_at=app.cover_letter.created_at,
            )

        return ApplicationResponse(
            id=str(app.id),
            job={"id": str(app.job_id), "title": ""},
            status=app.status.value if hasattr(app.status, 'value') else str(app.status),
            approval_required=app.approval_required,
            submitted_at=app.applied_at,
            notes=app.notes,
            cover_letter=cover_letter,
            created_at=app.created_at,
            updated_at=app.updated_at,
        )
