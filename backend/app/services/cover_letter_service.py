from typing import Optional
import uuid
import structlog

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.exceptions import NotFoundException, ValidationException
from app.models.application import JobApplication, CoverLetter, CoverLetterTone
from app.schemas.application import CoverLetterResponse

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
            select(JobApplication).where(
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

        content = (
            f"Dear Hiring Manager,\n\n"
            f"I am excited to apply for this position. With my background in software engineering, "
            f"I believe I would be a great addition to your team.\n\n"
            f"My experience includes building scalable systems, working with cross-functional teams, "
            f"and delivering high-quality software products.\n\n"
            f"I would welcome the opportunity to discuss how my skills align with your needs.\n\n"
            f"Best regards,\nApplicant"
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

    async def get_cover_letter(
        self, user_id: uuid.UUID, cover_letter_id: str
    ) -> CoverLetterResponse:
        result = await self.db.execute(select(CoverLetter).where(CoverLetter.id == cover_letter_id))
        cl = result.scalar_one_or_none()
        if not cl:
            raise NotFoundException("Cover letter not found")
        return CoverLetterResponse.model_validate(cl)

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
