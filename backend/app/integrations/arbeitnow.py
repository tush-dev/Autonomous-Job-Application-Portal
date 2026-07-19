"""Arbeitnow public API integration.

Arbeitnow provides a free, no-key-required API for job listings.
  GET https://www.arbeitnow.com/api/job-board-api — returns job listings
"""
import logging
import asyncio
from typing import Optional

import httpx

logger = logging.getLogger(__name__)

ARBEITNOW_URL = "https://www.arbeitnow.com/api/job-board-api"


async def search_jobs(
    query: str,
    location: Optional[str] = None,
    max_pages: int = 10,
) -> list[dict]:
    params = {"per_page": 100}
    if query:
        params["search"] = query

    raw_jobs: list[dict] = []
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            next_url: Optional[str] = ARBEITNOW_URL
            page = 1
            while next_url and page <= max(1, min(max_pages, 20)):
                request_params = {**params, "page": page} if next_url == ARBEITNOW_URL else None
                resp = await client.get(next_url, params=request_params)
                resp.raise_for_status()
                data = resp.json()
                page_jobs = data.get("data", []) if isinstance(data, dict) else []
                if not isinstance(page_jobs, list) or not page_jobs:
                    break
                raw_jobs.extend(page_jobs)
                next_url = (data.get("links") or {}).get("next")
                page += 1
                if next_url:
                    # The feed is free and explicitly asks clients not to abuse it.
                    await asyncio.sleep(0.5)
    except Exception as e:
        logger.error("Arbeitnow error: %s", e)
        return []

    logger.info("Arbeitnow: %d jobs across %d page(s)", len(raw_jobs), max(0, page - 1))

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
        "remote": "remote" if job.get("remote") else "onsite",
        "employment_type": job.get("job_type"),
        "experience_level": None,
        "skills_required": tags,
        "posted_at": job.get("created_at"),
    }
