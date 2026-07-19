"""Greenhouse Job Board API integration.

Greenhouse has an open, public-facing job board API that doesn't require an API key:
  GET https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs
  GET https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs/{id}

Common board tokens: greenhouse, lever (powered by greenhouse), and company-specific tokens.
"""
import logging
from typing import Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

GREENHOUSE_BASE = "https://boards-api.greenhouse.io/v1/boards"

DEFAULT_BOARD_TOKENS = [
    "airbnb",
    "netflix",
    "spotify",
    "figma",
    "notion",
    "discord",
    "stripe",
    "gitlab",
    "hashicorp",
    "docker",
    "elastic",
    "grafana",
    "sentry",
    "twilio",
    "urban-outfitters",
    "warby-parker",
    "wayfair",
    "woocommerce",
    "xero",
    "zynga",
    "glossier",
    "loom",
    "mercury",
    "ramp",
    "vercel",
    "linear",
    "posthog",
    "retool",
    "supabase",
    "planetscale",
]

MAX_JOBS_PER_BOARD = 100


async def search_jobs(
    query: str,
    location: Optional[str] = None,
    board_tokens: Optional[list[str]] = None,
) -> list[dict]:
    """Search jobs across Greenhouse-powered job boards.

    Args:
        query: Search keyword (matched against title).
        location: Optional location filter.
        board_tokens: List of board tokens to search (defaults to common ones).

    Returns:
        List of job dicts normalised to a common schema:
          - title, location, description, apply_url, company, source_job_id, ...
    """
    tokens = board_tokens or DEFAULT_BOARD_TOKENS
    all_jobs: list[dict] = []

    async with httpx.AsyncClient(timeout=30) as client:
        for token in tokens:
            url = f"{GREENHOUSE_BASE}/{token}/jobs"
            params: dict = {
                "content": "true",
                "per_page": min(MAX_JOBS_PER_BOARD, 100),
            }
            if query:
                params["query"] = query

            try:
                resp = await client.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()
                jobs = data.get("jobs", [])
                logger.info("Greenhouse[%s]: %d jobs", token, len(jobs))

                for j in jobs:
                    try:
                        normalized = _normalize(j, token)
                        if _matches_query(normalized, query, location):
                            all_jobs.append(normalized)
                    except Exception as e:
                        logger.warning("Greenhouse[%s] skipping job %s: %s", token, j.get("id", "?"), e)
                        continue

            except httpx.HTTPStatusError as e:
                logger.warning("Greenhouse[%s] HTTP %s: %.200s", token, e.response.status_code, e.response.text)
            except Exception as e:
                logger.error("Greenhouse[%s] error: %s", token, e)

    logger.info("Greenhouse total: %d matching jobs", len(all_jobs))
    return all_jobs


def _normalize(job: dict, board_token: str) -> dict:
    offices = job.get("offices") or []
    office = offices[0] if offices else {}
    metadata = job.get("metadata") or []

    salary_min, salary_max, currency = None, None, "USD"
    salary_interval = "yearly"
    for m in metadata:
        if m.get("name", "").lower() in ("salary range", "compensation", "salary"):
            value = m.get("value", "")
            import re
            nums = re.findall(r"\d[\d,]*", value.replace(",", ""))
            if len(nums) >= 2:
                salary_min = int(nums[0].replace(",", ""))
                salary_max = int(nums[1].replace(",", ""))
            if "USD" in value or "$" in value:
                currency = "USD"
            if "hour" in value.lower():
                salary_interval = "hourly"

    location_parts = [office.get("name", ""), office.get("location", "")]
    location_str = ", ".join(filter(None, location_parts)) if any(location_parts) else job.get("location", {}).get("name", "")

    skills_required = []
    description = job.get("content", "") or ""
    common_tech = [
        "python", "javascript", "typescript", "java", "c++", "c#", "go", "golang", "rust",
        "react", "angular", "vue", "vuejs", "node", "nodejs", "django", "flask", "fastapi",
        "spring", "rails", "ruby", "php", "swift", "kotlin",
        "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch",
        "aws", "gcp", "azure", "docker", "kubernetes", "terraform", "jenkins", "ci/cd",
        "machine learning", "ml", "ai", "data science", "tensorflow", "pytorch",
        "html", "css", "sass", "graphql", "rest", "api", "git",
        "agile", "scrum", "jira", "linux", "bash",
    ]
    desc_lower = description.lower()
    for tech in common_tech:
        if tech in desc_lower:
            skills_required.append(tech)

    return {
        "title": job.get("title", ""),
        "location": location_str,
        "description": job.get("content", "") or "",
        "application_url": job.get("absolute_url", ""),
        "company_name": board_token.capitalize(),
        "source": "greenhouse",
        "source_job_id": str(job.get("id", "")),
        "salary_min": salary_min,
        "salary_max": salary_max,
        "salary_currency": currency,
        "salary_interval": salary_interval,
        "remote": "unspecified",
        "employment_type": next((m.get("value") for m in metadata if "employment" in m.get("name", "").lower()), None),
        "experience_level": next((m.get("value") for m in metadata if "experience" in m.get("name", "").lower()), None),
        "skills_required": skills_required if skills_required else None,
    }


def _matches_query(job: dict, query: str, location: Optional[str]) -> bool:
    lowered = (job.get("title") or "").lower()
    if query:
        terms = query.lower().split()
        if not any(t in lowered for t in terms):
            return False
    if location:
        loc = (job.get("location") or "").lower()
        if location.lower() not in loc:
            return False
    return True
