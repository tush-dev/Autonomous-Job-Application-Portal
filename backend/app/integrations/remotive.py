"""Remotive public jobs API integration.

The public feed contains active remote roles and requires attribution through
the listing URL, which is preserved as the application URL.
"""
import html
import re
from typing import Optional

import httpx

REMOTIVE_URL = "https://remotive.com/api/remote-jobs"


async def search_jobs(query: str = "", location: Optional[str] = None) -> list[dict]:
    params: dict[str, str | int] = {"limit": 200}
    if query:
        params["search"] = query

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        response = await client.get(REMOTIVE_URL, params=params)
        response.raise_for_status()
        jobs = response.json().get("jobs", [])

    results = []
    for job in jobs:
        candidate_location = job.get("candidate_required_location") or "Worldwide"
        if location and location.lower() not in candidate_location.lower() and "worldwide" not in candidate_location.lower():
            continue
        salary_min, salary_max = _salary_range(job.get("salary") or "")
        description = html.unescape(re.sub(r"<[^>]+>", " ", job.get("description") or ""))
        results.append({
            "title": job.get("title") or "",
            "company_name": job.get("company_name") or "Unknown",
            "company_logo": job.get("company_logo"),
            "location": candidate_location,
            "description": description,
            "application_url": job.get("url") or "",
            "source": "rss_feed",
            "source_job_id": f"remotive:{job.get('id')}",
            "salary_min": salary_min,
            "salary_max": salary_max,
            "salary_currency": "USD",
            "salary_interval": "yearly",
            "remote": "remote",
            "employment_type": job.get("job_type"),
            "experience_level": None,
            "skills_required": [],
            "posted_at": job.get("publication_date"),
            "provider": "remotive",
        })
    return [job for job in results if job["title"] and job["application_url"]]


def _salary_range(value: str) -> tuple[Optional[int], Optional[int]]:
    numbers = [int(item.replace(",", "")) for item in re.findall(r"\d[\d,]*", value)]
    if len(numbers) >= 2:
        return numbers[0], numbers[1]
    return (numbers[0], numbers[0]) if numbers else (None, None)
