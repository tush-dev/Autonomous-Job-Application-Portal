import logging
from datetime import datetime, timedelta, timezone

from celery import chain, group
from sqlalchemy import select, delete, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.workers.celery_app import celery_app
from app.core.database import async_session_factory
from app.models.job import Job, Company, JobSource
from app.integrations import jsearch, greenhouse, lever, remoteok, arbeitnow, remotive, jobicy
from app.services.workplace import classify_workplace

logger = logging.getLogger(__name__)

PROVIDERS = {
    "jsearch": jsearch.search_jobs,
    "greenhouse": greenhouse.search_jobs,
    "lever": lever.search_jobs,
    "remoteok": remoteok.search_jobs,
    "arbeitnow": arbeitnow.search_jobs,
    "remotive": remotive.search_jobs,
    "jobicy": jobicy.search_jobs,
}

SEARCH_QUERIES = [
    "software engineer",
    "full stack developer",
    "data scientist",
    "product manager",
    "devops engineer",
    "frontend developer",
    "backend developer",
    "machine learning engineer",
    "site reliability engineer",
    "security engineer",
]


@celery_app.task(bind=True, max_retries=3, default_retry_delay=120)
def refresh_job_cache(self):
    """Refresh all job data from every provider in the background."""
    tasks = [crawl_job_source.s(source) for source in PROVIDERS.keys()]
    job = group(tasks)
    result = job.apply_async()
    logger.info("refresh_job_cache started with %d providers", len(PROVIDERS))
    return result.id


@celery_app.task(bind=True, max_retries=3, default_retry_delay=120)
def crawl_job_source(self, source: str):
    """Fetch jobs from a specific source and store in database."""
    import asyncio

    async def _run():
        provider = PROVIDERS.get(source)
        if not provider:
            logger.warning("Unknown provider: %s", source)
            return

        all_jobs = []
        # Arbeitnow exposes the complete feed through pagination, so querying it
        # once avoids duplicate calls and provider rate limits.
        provider_queries = [""] if source == "arbeitnow" else SEARCH_QUERIES
        for query in provider_queries:
            try:
                jobs = await provider(query, None)
                all_jobs.extend(jobs)
                logger.info("crawl[%s] query=%s got=%d", source, query, len(jobs))
            except Exception as e:
                logger.error("crawl[%s] query=%s failed: %s", source, query, e)

        seen_ids = set()
        deduped = []
        for j in all_jobs:
            sid = j.get("source_job_id") or j.get("title", "")
            key = f"{source}_{sid}"
            if key not in seen_ids:
                seen_ids.add(key)
                deduped.append(j)

        logger.info("crawl[%s] total=%d deduped=%d", source, len(all_jobs), len(deduped))

        async with async_session_factory() as db:
            stored = 0
            for job_data in deduped:
                try:
                    await _store_job(db, job_data, source)
                    stored += 1
                except Exception as e:
                    logger.error("crawl[%s] store failed: %s", source, e)
            await db.commit()
            logger.info("crawl[%s] stored=%d", source, stored)

    try:
        asyncio.run(_run())
    except Exception as exc:
        raise self.retry(exc=exc)


async def _store_job(db: AsyncSession, ext: dict, provider: str):
    from sqlalchemy import select
    from app.models.job import Job, Company
    from app.models.job import JobSource, RemoteType, SalaryInterval

    if not ext.get("title"):
        return

    source = ext.get("source", provider)
    source_enum = getattr(JobSource, source.upper(), JobSource.MANUAL)
    source_job_id = ext.get("source_job_id") or ""

    if source_job_id:
        existing = await db.execute(
            select(Job).where(
                Job.source == source_enum,
                Job.source_job_id == source_job_id,
            )
        )
        if existing.scalar_one_or_none():
            return

    company_name = ext.get("company_name", "") or "Unknown"
    company = None
    if company_name:
        comp_result = await db.execute(
            select(Company).where(Company.name == company_name).order_by(Company.created_at).limit(1)
        )
        company = comp_result.scalars().first()
        if not company:
            company = Company(name=company_name, logo_url=ext.get("company_logo"))
            db.add(company)
            await db.flush()

    remote_str = classify_workplace(
        ext.get("remote"), ext.get("location"), ext.get("description")
    )
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
    db.add(job)


@celery_app.task
def expire_old_jobs():
    """Mark jobs older than 90 days as inactive."""
    import asyncio

    async def _run():
        cutoff = datetime.now(timezone.utc) - timedelta(days=90)
        async with async_session_factory() as db:
            result = await db.execute(
                select(Job).where(
                    Job.created_at < cutoff,
                    Job.is_active == True,
                )
            )
            jobs = result.scalars().all()
            for job in jobs:
                job.is_active = False
            await db.commit()
            logger.info("expired %d old jobs", len(jobs))

    asyncio.run(_run())


@celery_app.task(bind=True, max_retries=2, default_retry_delay=300)
def score_all_user_resumes(self):
    """Periodically score all active resumes against all active jobs."""
    import asyncio

    async def _run():
        from app.models.user import User
        from app.models.resume import Resume
        from app.services.matching_service import MatchingService

        async with async_session_factory() as db:
            users_result = await db.execute(
                select(User.id, User.active_resume_id)
            )
            users = users_result.all()
            total_scored = 0

            for user_id, active_resume_id in users:
                resume_id = active_resume_id
                if not resume_id:
                    resume_result = await db.execute(
                        select(Resume.id)
                        .where(Resume.user_id == user_id, Resume.parsing_status == "COMPLETED")
                        .order_by(desc(Resume.created_at))
                        .limit(1)
                    )
                    resume_id = resume_result.scalar_one_or_none()

                if not resume_id:
                    continue

                try:
                    matching = MatchingService(db)
                    scored = await matching.score_jobs_for_resume(user_id, resume_id)
                    total_scored += scored
                except Exception as e:
                    logger.error("score_user_failed", user_id=str(user_id), error=str(e))

            await db.commit()
            logger.info("score_all_complete", total_users=len(users), total_scored=total_scored)

    asyncio.run(_run())
