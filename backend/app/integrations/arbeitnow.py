"""Arbeitnow public API integration.

Arbeitnow provides a free, no-key-required API for job listings.
  GET https://www.arbeitnow.com/api/job-board-api — returns job listings
"""
import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

ARBEITNOW_URL = "https://www.arbeitnow.com/api/job-board-api"


async def search_jobs(
    query: str,
    location: Optional[str] = None,
) -> list[dict]:
    params = {"per_page": 50}
    if query:
        params["search"] = query

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(ARBEITNOW_URL, params=params)
            resp.raise_for_status()
            data = resp.json()
    except Exception as e:
        logger.error("Arbeitnow error: %s", e)
        return []

    raw_jobs = data.get("data", []) if isinstance(data, dict) else data
    if not isinstance(raw_jobs, list):
        return []

    logger.info("Arbeitnow: %d total jobs", len(raw_jobs))

    results = []
    query_lower = query.lower() if query else ""
    query_terms = query_lower.split() if query_lower else []

    for j in raw_jobs:
        title = (j.get("title") or "").lower()
        desc = (j.get("description") or "").lower()
        tags = " ".join(j.get("tags") or []).lower()

        if query_terms:
            combined = f"{title} {desc} {tags}"
            if not any(t in combined for t in query_terms):
                continue

        if location:
            locs = [c.lower() for c in j.get("location", "").split(",")] if j.get("location") else []
            if not any(location.lower() in l for l in locs):
                continue

        normalized = _normalize(j)
        if normalized:
            results.append(normalized)

    logger.info("Arbeitnow matching: %d jobs", len(results))
    return results


def _normalize(job: dict) -> Optional[dict]:
    if not job.get("title"):
        return None

    location_parts = [p.strip() for p in (job.get("location") or "").split(",") if p.strip()]
    city = location_parts[0] if location_parts else ""
    country = location_parts[-1] if len(location_parts) > 1 else ""
    location = f"{city}, {country}" if city and country else (city or country or "")

    tags = job.get("tags") or []

    return {
        "title": job.get("title", ""),
        "company_name": job.get("company_name", "") or "Unknown",
        "company_logo": job.get("company_logo"),
        "location": location,
        "description": job.get("description", "") or "",
        "application_url": job.get("url", ""),
        "source": "arbeitnow",
        "source_job_id": str(job.get("slug", "")),
        "salary_min": None,
        "salary_max": None,
        "salary_currency": "EUR",
        "salary_interval": "yearly",
        "remote": "remote" if job.get("remote") else "unspecified",
        "employment_type": job.get("job_type"),
        "experience_level": None,
        "skills_required": tags,
        "posted_at": job.get("created_at"),
    }
