"""Jobicy public remote-jobs API integration."""
import html
import re
from typing import Optional

import httpx

JOBICY_URL = "https://jobicy.com/api/v2/remote-jobs"


async def search_jobs(query: str = "", location: Optional[str] = None) -> list[dict]:
    params: dict[str, str | int] = {"count": 100}
    if query:
        params["tag"] = query

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        response = await client.get(JOBICY_URL, params=params)
        response.raise_for_status()
        payload = response.json()
        jobs = payload.get("jobs", payload.get("data", [])) if isinstance(payload, dict) else []

    results = []
    for job in jobs:
        job_location = job.get("jobGeo") or "Anywhere"
        if location and location.lower() not in job_location.lower() and job_location.lower() not in {"anywhere", "worldwide"}:
            continue
        description = html.unescape(re.sub(r"<[^>]+>", " ", job.get("jobDescription") or job.get("jobExcerpt") or ""))
        results.append({
            "title": job.get("jobTitle") or "",
            "company_name": job.get("companyName") or "Unknown",
            "company_logo": job.get("companyLogo"),
            "location": job_location,
            "description": description,
            "application_url": job.get("url") or "",
            "source": "rss_feed",
            "source_job_id": f"jobicy:{job.get('id')}",
            "salary_min": _number(job.get("salaryMin")),
            "salary_max": _number(job.get("salaryMax")),
            "salary_currency": job.get("salaryCurrency") or "USD",
            "salary_interval": _salary_interval(job.get("salaryPeriod") or ""),
            "remote": "remote",
            "employment_type": _text_value(job.get("jobType")),
            "experience_level": _text_value(job.get("jobLevel")),
            "skills_required": job.get("jobIndustry") if isinstance(job.get("jobIndustry"), list) else [],
            "posted_at": job.get("pubDate"),
            "provider": "jobicy",
        })
    return [job for job in results if job["title"] and job["application_url"]]


def _number(value) -> Optional[int]:
    try:
        return int(float(value)) if value not in (None, "") else None
    except (TypeError, ValueError):
        return None


def _text_value(value) -> Optional[str]:
    if isinstance(value, list):
        return ", ".join(str(item) for item in value if item) or None
    return str(value) if value not in (None, "") else None


def _salary_interval(value: str) -> str:
    lowered = value.lower()
    if "hour" in lowered:
        return "hourly"
    if "month" in lowered:
        return "monthly"
    return "yearly"
