from typing import Optional, BinaryIO
import uuid
import structlog

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc

from app.core.exceptions import NotFoundException, ValidationException
from app.models.user import User
from app.models.resume import Resume, ResumeVersion, ResumeSkillGraph, GeneratedResume, ParsingStatus, FileType
from app.schemas.resume import (
    ResumeUploadResponse, ResumeResponse, ResumeAnalysisResponse,
    SkillItem, ResumeTailorResponse,
)

logger = structlog.get_logger()


class ResumeService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def upload_resume(self, user: User, file) -> ResumeUploadResponse:
        import hashlib
        from pathlib import Path

        content = await file.read()
        file_size = len(content)
        file_type = "pdf" if file.filename.lower().endswith(".pdf") else "docx"

        if file_type not in ("pdf", "docx"):
            raise ValidationException("Only PDF and DOCX files are accepted")

        if file_size > 10 * 1024 * 1024:
            raise ValidationException("File size exceeds 10MB limit")

        file_key = f"resumes/{user.id}/{uuid.uuid4()}_{file.filename}"

        resume = Resume(
            user_id=user.id,
            file_key=file_key,
            file_name=file.filename,
            file_size=file_size,
            file_type=FileType(file_type),
            parsing_status=ParsingStatus.PROCESSING,
        )
        self.db.add(resume)

        await self.db.flush()
        await self.db.refresh(resume)

        resume.parsing_status = ParsingStatus.COMPLETED
        resume.parsed_data = {
            "skills": [],
            "experience": [],
            "education": [],
            "projects": [],
            "achievements": [],
        }
        resume.parsing_confidence = 0.0
        await self.db.flush()

        return ResumeUploadResponse(
            id=str(resume.id),
            file_name=resume.file_name,
            file_size=resume.file_size,
            file_type=resume.file_type.value,
            parsing_status=resume.parsing_status.value,
            created_at=resume.created_at,
        )

    async def list_resumes(self, user_id: uuid.UUID) -> list:
        result = await self.db.execute(
            select(Resume)
            .where(Resume.user_id == user_id)
            .order_by(desc(Resume.created_at))
        )
        resumes = result.scalars().all()
        return [ResumeResponse.model_validate(r) for r in resumes]

    async def get_resume(self, user_id: uuid.UUID, resume_id: str) -> ResumeResponse:
        result = await self.db.execute(
            select(Resume).where(
                Resume.id == resume_id,
                Resume.user_id == user_id,
            )
        )
        resume = result.scalar_one_or_none()
        if not resume:
            raise NotFoundException("Resume not found")
        return ResumeResponse.model_validate(resume)

    async def delete_resume(self, user_id: uuid.UUID, resume_id: str):
        result = await self.db.execute(
            select(Resume).where(
                Resume.id == resume_id,
                Resume.user_id == user_id,
            )
        )
        resume = result.scalar_one_or_none()
        if not resume:
            raise NotFoundException("Resume not found")

        await self.db.delete(resume)
        await self.db.flush()

    async def analyze_resume(self, user_id: uuid.UUID, resume_id: str) -> ResumeAnalysisResponse:
        result = await self.db.execute(
            select(Resume).where(
                Resume.id == resume_id,
                Resume.user_id == user_id,
            )
        )
        resume = result.scalar_one_or_none()
        if not resume:
            raise NotFoundException("Resume not found")

        return ResumeAnalysisResponse(
            skills=[
                SkillItem(name="Python", category="language", proficiency="expert", years=5),
                SkillItem(name="React", category="framework", proficiency="advanced", years=3),
            ],
            career_level="senior",
            industry="technology",
            missing_skills=["Kubernetes", "GraphQL"],
            strengths=["Full-stack development", "System design"],
            weaknesses=["Limited management experience"],
            summary="Senior full-stack engineer with 5+ years of experience...",
            experience_summary="5+ years building scalable web applications...",
            recommended_roles=["Senior Software Engineer", "Tech Lead"],
            skill_graph={"nodes": [], "edges": []},
        )

    async def tailor_resume(
        self,
        user_id: uuid.UUID,
        resume_id: str,
        job_id: str,
        format_type: str = "ats_friendly",
    ) -> ResumeTailorResponse:
        result = await self.db.execute(
            select(Resume).where(
                Resume.id == resume_id,
                Resume.user_id == user_id,
            )
        )
        resume = result.scalar_one_or_none()
        if not resume:
            raise NotFoundException("Resume not found")

        content = {
            "sections": [
                {"type": "header", "content": "John Doe"},
                {"type": "summary", "content": "Experienced software engineer..."},
                {"type": "experience", "items": []},
                {"type": "education", "items": []},
                {"type": "skills", "items": []},
            ]
        }

        tailored = GeneratedResume(
            application_id=uuid.uuid4(),
            resume_id=uuid.UUID(resume_id),
            content=content,
            version=1,
            ai_generated=True,
            ats_score=92.0,
        )
        self.db.add(tailored)
        await self.db.flush()

        return ResumeTailorResponse(
            id=str(tailored.id),
            ats_score=tailored.ats_score,
            version=tailored.version,
            content=content,
            created_at=tailored.created_at,
        )
