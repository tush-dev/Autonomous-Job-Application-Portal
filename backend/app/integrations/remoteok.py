"""RemoteOK public API integration.

RemoteOK provides a free, no-key-required API for remote jobs.
  GET https://remoteok.com/api — returns all active listings
"""
import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

REMOTEOK_URL = "https://remoteok.com/api"


async def search_jobs(
    query: str,
    location: Optional[str] = None,
) -> list[dict]:
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(REMOTEOK_URL)
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        logger.error("RemoteOK error: %s", e)
        return []

    if not isinstance(data, list):
        return []

    raw_jobs = data[1:] if data and isinstance(data[0], dict) and "success" in data[0] else data
    logger.info("RemoteOK: %d total jobs", len(raw_jobs))

    results = []
    query_lower = query.lower() if query else ""
    query_terms = query_lower.split() if query_lower else []

    for j in raw_jobs:
        title = (j.get("position") or "").lower()
        desc = (j.get("description") or "").lower()
        tags = " ".join(j.get("tags") or []).lower()

        if query_terms:
            combined = f"{title} {desc} {tags}"
            if not any(t in combined for t in query_terms):
                continue

        if location:
            loc = (j.get("location") or "").lower()
            if location.lower() not in loc:
                continue

        normalized = _normalize(j)
        if normalized:
            results.append(normalized)

    logger.info("RemoteOK matching: %d jobs", len(results))
    return results


def _normalize(job: dict) -> Optional[dict]:
    if not job.get("position"):
        return None

    salary_min, salary_max = None, None
    salary_str = job.get("salary") or ""
    if salary_str:
        import re
        nums = re.findall(r"\d[\d,]*", salary_str.replace(",", ""))
        if len(nums) >= 2:
            salary_min = int(nums[0])
            salary_max = int(nums[1])
        elif len(nums) == 1:
            salary_min = int(nums[0])
            salary_max = int(nums[0])

    return {
        "title": job.get("position", ""),
        "company_name": job.get("company", "") or "Unknown",
        "company_logo": job.get("company_logo"),
        "location": job.get("location") or "Remote",
        "description": job.get("description", "") or "",
        "application_url": job.get("url", ""),
        "source": "remoteok",
        "source_job_id": str(job.get("id", "")),
        "salary_min": salary_min,
        "salary_max": salary_max,
        "salary_currency": "USD",
        "salary_interval": "yearly",
        "remote": "remote",
        "employment_type": "Full-time",
        "experience_level": None,
        "skills_required": job.get("tags") or [],
        "posted_at": job.get("date"),
    }
