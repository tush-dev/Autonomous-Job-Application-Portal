from typing import Optional
import uuid
import structlog

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_, or_

from app.core.exceptions import NotFoundException
from app.models.job import Job, Company, SavedJob
from app.models.application import JobApplication
from app.schemas.job import JobSearchResponse, JobResponse, CompanyResponse
from app.services.cache_service import CacheService

logger = structlog.get_logger()


class JobService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.cache = CacheService()

    async def search_jobs(
        self,
        user_id: uuid.UUID,
        query: str = "",
        location: Optional[str] = None,
        remote: Optional[str] = None,
        salary_min: Optional[int] = None,
        salary_max: Optional[int] = None,
        sources: Optional[list[str]] = None,
        exclude_applied: bool = False,
        page: int = 1,
        page_size: int = 20,
    ) -> JobSearchResponse:
        stmt = select(Job).where(Job.is_active == True)

        if query:
            stmt = stmt.where(
                or_(
                    Job.title.ilike(f"%{query}%"),
                    Job.description.ilike(f"%{query}%"),
                )
            )

        if location:
            stmt = stmt.where(Job.location.ilike(f"%{location}%"))

        if remote and remote != "any":
            stmt = stmt.where(Job.remote == remote)

        if salary_min is not None:
            stmt = stmt.where(
                or_(Job.salary_max >= salary_min, Job.salary_max.is_(None))
            )

        if sources:
            stmt = stmt.where(Job.source.in_(sources))

        count_stmt = stmt
        count_result = await self.db.execute(select(func.count()).select_from(count_stmt.subquery()))
        total = count_result.scalar() or 0

        offset = (page - 1) * page_size
        stmt = stmt.order_by(desc(Job.created_at)).offset(offset).limit(page_size)
        result = await self.db.execute(stmt)
        jobs = result.scalars().all()

        job_responses = []
        for job in jobs:
            company = None
            if job.company_id:
                company_result = await self.db.execute(
                    select(Company).where(Company.id == job.company_id)
                )
                company_model = company_result.scalar_one_or_none()
                if company_model:
                    company = CompanyResponse(
                        id=str(company_model.id),
                        name=company_model.name,
                        logo_url=company_model.logo_url,
                        website=company_model.website,
                        industry=company_model.industry,
                    )

            job_responses.append(JobResponse(
                id=str(job.id),
                company=company,
                source=job.source.value if hasattr(job.source, 'value') else str(job.source),
                title=job.title,
                location=job.location,
                remote=job.remote.value if hasattr(job.remote, 'value') else str(job.remote),
                salary_min=job.salary_min,
                salary_max=job.salary_max,
                salary_currency=job.salary_currency,
                employment_type=job.employment_type,
                experience_level=job.experience_level,
                skills_required=job.skills_required or [],
                application_url=job.application_url,
                posted_at=job.created_at,
                match_score=85.0,
                match_reasons=["Skills match: Python, React", "Experience level matches"],
                missing_skills=[],
                estimated_interview_chance="high",
            ))

        return JobSearchResponse(
            jobs=job_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size if total > 0 else 0,
        )

    async def get_job(self, user_id: uuid.UUID, job_id: str) -> JobResponse:
        result = await self.db.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        if not job:
            raise NotFoundException("Job not found")
        return JobResponse(
            id=str(job.id),
            title=job.title,
            source=job.source.value if hasattr(job.source, 'value') else str(job.source),
            location=job.location,
            remote=job.remote.value if hasattr(job.remote, 'value') else str(job.remote),
            salary_min=job.salary_min,
            salary_max=job.salary_max,
            salary_currency=job.salary_currency,
            employment_type=job.employment_type,
            skills_required=job.skills_required or [],
            posted_at=job.created_at,
        )

    async def save_job(self, user_id: uuid.UUID, job_id: str):
        existing = await self.db.execute(
            select(SavedJob).where(
                SavedJob.user_id == user_id,
                SavedJob.job_id == job_id,
            )
        )
        if existing.scalar_one_or_none():
            return

        saved = SavedJob(user_id=user_id, job_id=job_id)
        self.db.add(saved)
        await self.db.flush()

    async def unsave_job(self, user_id: uuid.UUID, job_id: str):
        result = await self.db.execute(
            select(SavedJob).where(
                SavedJob.user_id == user_id,
                SavedJob.job_id == job_id,
            )
        )
        saved = result.scalar_one_or_none()
        if saved:
            await self.db.delete(saved)
            await self.db.flush()

    async def list_saved_jobs(self, user_id: uuid.UUID) -> list:
        result = await self.db.execute(
            select(Job)
            .join(SavedJob, SavedJob.job_id == Job.id)
            .where(SavedJob.user_id == user_id)
            .order_by(desc(SavedJob.saved_at))
        )
        jobs = result.scalars().all()
        return [
            JobResponse(
                id=str(job.id),
                title=job.title,
                source=job.source.value if hasattr(job.source, 'value') else str(job.source),
                location=job.location,
                remote=job.remote.value if hasattr(job.remote, 'value') else str(job.remote),
                posted_at=job.created_at,
            )
            for job in jobs
        ]
