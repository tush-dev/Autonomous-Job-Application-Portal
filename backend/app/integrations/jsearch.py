"""JSearch API v2 integration for real-time job search from multiple boards.

Auth: x-rapidapi-key + x-rapidapi-host headers via RapidAPI.
"""
import logging
from typing import Optional
from datetime import datetime

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

JSEARCH_BASE_URL = "https://jsearch.p.rapidapi.com"
SEARCH_ENDPOINT = "/search-v2"


def _headers() -> dict[str, str]:
    return {
        "x-rapidapi-key": settings.JSEARCH_API_KEY,
        "x-rapidapi-host": "jsearch.p.rapidapi.com",
    }


async def search_jobs(
    query: str,
    location: Optional[str] = None,
    num_pages: int = 1,
    country: str = "us",
) -> list[dict]:
    if not settings.JSEARCH_API_KEY:
        logger.warning("JSEARCH_API_KEY not configured")
        return []

    params: dict[str, str | int] = {
        "query": f"{query} in {location}" if location else query,
        "num_pages": num_pages,
        "country": country,
    }

    async with httpx.AsyncClient(timeout=60) as client:
        try:
            resp = await client.get(
                f"{JSEARCH_BASE_URL}{SEARCH_ENDPOINT}",
                params=params,
                headers=_headers(),
            )
            resp.raise_for_status()
            data = resp.json()
            raw_jobs = data.get("data", {}).get("jobs", [])
            logger.info("JSearch result: %d jobs", len(raw_jobs))

            normalized = []
            for j in raw_jobs:
                nj = _normalize(j)
                if nj:
                    normalized.append(nj)
            return normalized

        except httpx.TimeoutException:
            logger.error("JSearch request timed out")
            return []
        except httpx.HTTPStatusError as e:
            logger.error("JSearch HTTP error %s: %.300s", e.response.status_code, e.response.text)
            return []
        except Exception as e:
            logger.error("JSearch API error: %s", e)
            return []


def _normalize(job: dict) -> Optional[dict]:
    if not job.get("job_title"):
        return None

    salary_min, salary_max, currency = None, None, "USD"
    salary_period = job.get("job_salary_period") or ""
    raw_salary = job.get("job_salary") or ""
    min_s = job.get("job_min_salary")
    max_s = job.get("job_max_salary")

    if min_s and max_s:
        salary_min = int(min_s)
        salary_max = int(max_s)
    elif raw_salary and "-" in raw_salary:
        import re
        nums = re.findall(r"\d[\d,]*", raw_salary.replace(",", ""))
        if len(nums) >= 2:
            salary_min = int(nums[0])
            salary_max = int(nums[1])

    salary_interval = "yearly"
    if "hour" in salary_period.lower():
        salary_interval = "hourly"
    elif "month" in salary_period.lower():
        salary_interval = "monthly"

    remote = "unspecified"
    if job.get("job_is_remote") is True:
        remote = "remote"
    elif job.get("job_is_remote") == "true":
        remote = "remote"

    location = job.get("job_location") or ""
    employment_type = job.get("job_employment_type") or ""
    skills = job.get("job_required_skills") or []

    return {
        "title": job.get("job_title", ""),
        "company_name": job.get("employer_name", ""),
        "company_logo": job.get("employer_logo"),
        "location": location,
        "description": job.get("job_description", "") or "",
        "application_url": job.get("job_apply_link", ""),
        "source": "jsearch",
        "source_job_id": str(job.get("job_id", "")),
        "salary_min": salary_min,
        "salary_max": salary_max,
        "salary_currency": currency,
        "salary_interval": salary_interval,
        "remote": remote,
        "employment_type": employment_type,
        "experience_level": None,
        "skills_required": skills,
        "posted_at": job.get("job_posted_at_datetime_utc"),
    }
