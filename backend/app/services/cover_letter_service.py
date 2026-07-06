from typing import Optional
import uuid
import json
import structlog

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from app.core.exceptions import NotFoundException, ValidationException
from app.models.application import JobApplication, CoverLetter, CoverLetterTone
from app.models.job import Job, Company
from app.schemas.application import CoverLetterResponse
from app.core.ai.gateway import get_gateway

logger = structlog.get_logger()


class CoverLetterService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_cover_letter(
        self,
        user_id: uuid.UUID,
        application_id: str,
        tone: str = "professional",
        custom_instructions: Optional[str] = None,
    ) -> CoverLetterResponse:
        result = await self.db.execute(
            select(JobApplication)
            .options(
                selectinload(JobApplication.job).selectinload(Job.company),
                selectinload(JobApplication.cover_letter),
            )
            .where(
                JobApplication.id == application_id,
                JobApplication.user_id == user_id,
            )
        )
        app = result.scalar_one_or_none()
        if not app:
            raise NotFoundException("Application not found")

        tone_enum = CoverLetterTone.PROFESSIONAL
        if tone == "short":
            tone_enum = CoverLetterTone.SHORT
        elif tone == "custom":
            tone_enum = CoverLetterTone.CUSTOM

        job = app.job
        job_title = job.title if job else ""
        company_name = job.company.name if job and job.company else ""
        job_description = job.description or ""

        resume_text = "Not provided"
        if app.resume_id:
            from app.models.resume import Resume
            r_result = await self.db.execute(select(Resume).where(Resume.id == app.resume_id))
            resume = r_result.scalar_one_or_none()
            if resume and resume.parsed_data:
                resume_text = json.dumps(resume.parsed_data, indent=2)

        gateway = get_gateway()
        content = await gateway.generate_cover_letter(
            resume_text=resume_text,
            job_title=job_title,
            company_name=company_name,
            job_description=job_description,
            tone=tone,
        )

        if app.cover_letter:
            app.cover_letter.content = content
            app.cover_letter.tone = tone_enum
            app.cover_letter.word_count = len(content.split())
            app.cover_letter.version += 1
            app.cover_letter.ai_generated = True
            app.cover_letter.user_edited = False
        else:
            cover_letter = CoverLetter(
                application_id=app.id,
                content=content,
                tone=tone_enum,
                word_count=len(content.split()),
                ai_generated=True,
            )
            self.db.add(cover_letter)

        await self.db.flush()

        return CoverLetterResponse(
            id=str(app.cover_letter.id) if app.cover_letter else "",
            content=content,
            tone=tone,
            word_count=len(content.split()),
            created_at=app.cover_letter.created_at if app.cover_letter else None,
        )

    async def list_cover_letters(self, user_id: uuid.UUID) -> list[dict]:
        result = await self.db.execute(
            select(CoverLetter)
            .join(JobApplication, CoverLetter.application_id == JobApplication.id)
            .where(JobApplication.user_id == user_id)
            .options(
                selectinload(CoverLetter.application)
                .selectinload(JobApplication.job)
                .selectinload(Job.company)
            )
            .order_by(desc(CoverLetter.created_at))
        )
        cover_letters = result.scalars().all()
        return [
            {
                "id": str(cl.id),
                "application_id": str(cl.application_id),
                "content": cl.content,
                "tone": cl.tone.value if hasattr(cl.tone, "value") else str(cl.tone),
                "word_count": cl.word_count,
                "ai_generated": cl.ai_generated,
                "user_edited": cl.user_edited,
                "version": cl.version,
                "job_title": cl.application.job.title if cl.application and cl.application.job else "",
                "company_name": cl.application.job.company.name if cl.application and cl.application.job and cl.application.job.company else "",
                "created_at": cl.created_at.isoformat(),
                "updated_at": cl.updated_at.isoformat() if cl.updated_at else None,
            }
            for cl in cover_letters
        ]

    async def get_cover_letter(
        self, user_id: uuid.UUID, cover_letter_id: str
    ) -> CoverLetterResponse:
        result = await self.db.execute(select(CoverLetter).where(CoverLetter.id == cover_letter_id))
        cl = result.scalar_one_or_none()
        if not cl:
            raise NotFoundException("Cover letter not found")
        return CoverLetterResponse.model_validate(cl)

    async def delete_cover_letter(self, user_id: uuid.UUID, cover_letter_id: str):
        result = await self.db.execute(
            select(CoverLetter)
            .join(JobApplication, CoverLetter.application_id == JobApplication.id)
            .where(CoverLetter.id == cover_letter_id, JobApplication.user_id == user_id)
        )
        cl = result.scalar_one_or_none()
        if not cl:
            raise NotFoundException("Cover letter not found")
        await self.db.delete(cl)
        await self.db.flush()

    async def update_cover_letter(
        self, user_id: uuid.UUID, cover_letter_id: str, content: str
    ) -> CoverLetterResponse:
        result = await self.db.execute(select(CoverLetter).where(CoverLetter.id == cover_letter_id))
        cl = result.scalar_one_or_none()
        if not cl:
            raise NotFoundException("Cover letter not found")

        cl.content = content
        cl.word_count = len(content.split())
        cl.user_edited = True
        cl.version += 1
        await self.db.flush()

        return CoverLetterResponse.model_validate(cl)
