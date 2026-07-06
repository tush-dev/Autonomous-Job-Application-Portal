from typing import Optional
import uuid
import structlog
import math

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, and_, or_
from sqlalchemy.orm import selectinload, joinedload

from app.core.exceptions import NotFoundException
from app.models.job import Job, Company, SavedJob, JobSource, RemoteType, SalaryInterval
from app.models.application import JobApplication
from app.models.matching import JobMatch
from app.schemas.job import JobSearchResponse, JobResponse, CompanyResponse, JobMatchBrief
from app.services.cache_service import CacheService
from app.integrations import jsearch, greenhouse, lever, remoteok, arbeitnow

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
        min_match_score: Optional[float] = None,
        sort_by: Optional[str] = None,
    ) -> JobSearchResponse:
        await self._fetch_external_jobs(query, location, sources)

        stmt = (
            select(Job)
            .options(selectinload(Job.company))
            .where(Job.is_active == True)
        )

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
            remote_enum = getattr(RemoteType, remote.upper(), None)
            if remote_enum:
                stmt = stmt.where(Job.remote == remote_enum)

        if salary_min is not None:
            stmt = stmt.where(
                or_(Job.salary_max >= salary_min, Job.salary_max.is_(None))
            )

        if sources:
            source_enums = [s for s in [getattr(JobSource, src.upper(), None) for src in sources] if s]
            if source_enums:
                stmt = stmt.where(Job.source.in_(source_enums))

        if min_match_score is not None:
            stmt = stmt.join(
                JobMatch,
                and_(
                    JobMatch.job_id == Job.id,
                    JobMatch.user_id == user_id,
                ),
            ).where(JobMatch.match_score >= min_match_score)

        count_stmt = stmt
        count_result = await self.db.execute(select(func.count()).select_from(count_stmt.subquery()))
        total = count_result.scalar() or 0

        offset = (page - 1) * page_size

        if sort_by == "match":
            match_subq = (
                select(JobMatch.job_id, JobMatch.match_score)
                .where(JobMatch.user_id == user_id)
                .subquery()
            )
            stmt = stmt.outerjoin(
                match_subq,
                Job.id == match_subq.c.job_id,
            ).order_by(desc(match_subq.c.match_score).nullslast(), desc(Job.created_at))
        else:
            stmt = stmt.order_by(desc(Job.created_at))

        stmt = stmt.offset(offset).limit(page_size)
        result = await self.db.execute(stmt)
        jobs = result.scalars().all()

        saved_ids: set[str] = set()
        applied_ids: set[str] = set()
        saved_result = await self.db.execute(
            select(SavedJob.job_id).where(SavedJob.user_id == user_id)
        )
        saved_ids = {str(row[0]) for row in saved_result}
        applied_result = await self.db.execute(
            select(JobApplication.job_id).where(JobApplication.user_id == user_id)
        )
        applied_ids = {str(row[0]) for row in applied_result}

        match_map: dict[str, JobMatch] = {}
        if jobs:
            match_result = await self.db.execute(
                select(JobMatch).where(
                    JobMatch.user_id == user_id,
                    JobMatch.job_id.in_([j.id for j in jobs]),
                )
            )
            for m in match_result.scalars().all():
                match_map[str(m.job_id)] = m

        job_responses = []
        for job in jobs:
            company_resp = None
            if job.company:
                company_resp = CompanyResponse(
                    id=str(job.company.id),
                    name=job.company.name,
                    logo_url=job.company.logo_url,
                    website=job.company.website,
                    industry=job.company.industry,
                )

            m = match_map.get(str(job.id))
            match_brief = None
            if m:
                match_brief = JobMatchBrief(
                    match_score=m.match_score,
                    skills_matched=m.skills_matched or [],
                    missing_skills=m.missing_skills or [],
                    ats_compatibility=m.ats_compatibility,
                    interview_probability=m.interview_probability,
                    reasoning=m.reasoning,
                    is_recommended=m.is_recommended,
                )

            job_responses.append(JobResponse(
                id=str(job.id),
                company=company_resp,
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
                posted_at=job.created_at or job.updated_at or job.created_at,
                is_saved=str(job.id) in saved_ids,
                has_applied=str(job.id) in applied_ids,
                match=match_brief,
            ))

        return JobSearchResponse(
            jobs=job_responses,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=(total + page_size - 1) // page_size if total > 0 else 0,
        )

    async def _fetch_external_jobs(
        self,
        query: str,
        location: Optional[str] = None,
        sources: Optional[list[str]] = None,
    ):
        source_list = sources or ["jsearch", "greenhouse", "lever", "remoteok", "arbeitnow"]
        all_external: list[dict] = []

        if "jsearch" in source_list:
            try:
                jsearch_jobs = await jsearch.search_jobs(query, location)
                all_external.extend(jsearch_jobs)
            except Exception as e:
                logger.error("jsearch_fetch_failed", error=str(e))

        if "greenhouse" in source_list:
            try:
                gh_jobs = await greenhouse.search_jobs(query, location)
                all_external.extend(gh_jobs)
            except Exception as e:
                logger.error("greenhouse_fetch_failed", error=str(e))

        if "lever" in source_list:
            try:
                lv_jobs = await lever.search_jobs(query, location)
                all_external.extend(lv_jobs)
            except Exception as e:
                logger.error("lever_fetch_failed", error=str(e))

        if "remoteok" in source_list:
            try:
                ro_jobs = await remoteok.search_jobs(query, location)
                all_external.extend(ro_jobs)
            except Exception as e:
                logger.error("remoteok_fetch_failed", error=str(e))

        if "arbeitnow" in source_list:
            try:
                an_jobs = await arbeitnow.search_jobs(query, location)
                all_external.extend(an_jobs)
            except Exception as e:
                logger.error("arbeitnow_fetch_failed", error=str(e))

        for ext in all_external:
            await self._store_external_job(ext)

    async def _store_external_job(self, ext: dict):
        if not ext.get("title"):
            return

        source = ext.get("source", ext.get("_provider", "manual"))
        source_enum = getattr(JobSource, source.upper(), JobSource.MANUAL)

        source_job_id = (ext.get("source_job_id") or "").strip()
        if source_job_id and len(source_job_id) > 4:
            existing = await self.db.execute(
                select(Job).where(
                    Job.source == source_enum,
                    Job.source_job_id == source_job_id,
                )
            )
            if existing.first():
                return

        company_name = ext.get("company_name", "") or "Unknown"
        company = None
        if company_name:
            comp_result = await self.db.execute(
                select(Company).where(Company.name == company_name)
            )
            company = comp_result.scalar_one_or_none()
            if not company:
                company = Company(
                    name=company_name,
                    logo_url=ext.get("company_logo"),
                    industry=ext.get("industry"),
                )
                self.db.add(company)
                await self.db.flush()

        remote_str = ext.get("remote", "unspecified")
        remote_enum = getattr(RemoteType, remote_str.upper(), RemoteType.UNSPECIFIED)

        salary_interval = ext.get("salary_interval", "yearly")
        salary_interval_enum = getattr(SalaryInterval, salary_interval.upper(), SalaryInterval.YEARLY)

        job = Job(
            company_id=company.id if company else None,
            source=source_enum,
            source_job_id=source_job_id,
            title=ext.get("title", "") or "",
            description=ext.get("description", "") or "",
            location=ext.get("location"),
            remote=remote_enum,
            salary_min=ext.get("salary_min"),
            salary_max=ext.get("salary_max"),
            salary_currency=ext.get("salary_currency", "USD"),
            salary_interval=salary_interval_enum,
            employment_type=ext.get("employment_type"),
            experience_level=ext.get("experience_level"),
            skills_required=ext.get("skills_required"),
            application_url=ext.get("application_url"),
            raw_data=ext,
        )
        self.db.add(job)
        try:
            await self.db.flush()
        except Exception:
            await self.db.rollback()

    async def get_job(self, user_id: uuid.UUID, job_id: str) -> JobResponse:
        result = await self.db.execute(select(Job).where(Job.id == job_id))
        job = result.scalar_one_or_none()
        if not job:
            raise NotFoundException("Job not found")
        m_result = await self.db.execute(
            select(JobMatch).where(JobMatch.job_id == job_id, JobMatch.user_id == user_id)
        )
        m = m_result.scalar_one_or_none()
        match_brief = None
        if m:
            match_brief = JobMatchBrief(
                match_score=m.match_score,
                skills_matched=m.skills_matched or [],
                missing_skills=m.missing_skills or [],
                ats_compatibility=m.ats_compatibility,
                interview_probability=m.interview_probability,
                reasoning=m.reasoning,
                is_recommended=m.is_recommended,
            )
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
            match=match_brief,
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
            .order_by(desc(SavedJob.created_at))
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
