"""Lever Job Board API integration.

Lever has a public-facing job board API that doesn't require an API key:
  GET https://api.lever.co/v0/postings/{board_token}?mode=json
  GET https://api.lever.co/v0/postings/{board_token}/{id}?mode=json

The board token is typically the company's Lever subdomain.
"""
import logging
from typing import Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

LEVER_BASE = "https://api.lever.co/v0/postings"

DEFAULT_BOARD_TOKENS = [
    "lever",
]

MAX_JOBS_PER_BOARD = 100


async def search_jobs(
    query: str,
    location: Optional[str] = None,
    board_tokens: Optional[list[str]] = None,
) -> list[dict]:
    """Search jobs across Lever-powered job boards.

    Args:
        query: Search keyword.
        location: Optional location filter.
        board_tokens: List of Lever board tokens (subdomains).

    Returns:
        List of job dicts normalised to a common schema.
    """
    tokens = board_tokens or DEFAULT_BOARD_TOKENS
    all_jobs: list[dict] = []

    async with httpx.AsyncClient(timeout=30) as client:
        for token in tokens:
            url = f"{LEVER_BASE}/{token}?mode=json"
            try:
                resp = await client.get(url)
                resp.raise_for_status()
                data = resp.json()
                jobs = data if isinstance(data, list) else []
                logger.info("Lever[%s]: %d jobs", token, len(jobs))

                for j in jobs:
                    normalized = _normalize(j, token)
                    if _matches_query(normalized, query, location):
                        all_jobs.append(normalized)

            except httpx.HTTPStatusError as e:
                logger.warning("Lever[%s] HTTP %s: %.200s", token, e.response.status_code, e.response.text)
            except Exception as e:
                logger.error("Lever[%s] error: %s", token, e)

    logger.info("Lever total: %d matching jobs", len(all_jobs))
    return all_jobs


def _normalize(job: dict, board_token: str) -> dict:
    categories = job.get("categories", {}) or {}
    lists = job.get("lists", [])
    apply_url = job.get("applyUrl") or job.get("hostedUrl", "")

    salary_data = {}
    for lst in lists:
        if lst.get("text", "").lower() in ("salary range", "compensation"):
            for item in lst.get("contentItems", []):
                salary_data["value"] = item.get("text", "")

    salary_min, salary_max, currency = None, None, "USD"
    salary_interval = "yearly"
    if salary_data.get("value"):
        import re
        nums = re.findall(r"\d[\d,]*", salary_data["value"].replace(",", ""))
        if len(nums) >= 2:
            salary_min = int(nums[0].replace(",", ""))
            salary_max = int(nums[1].replace(",", ""))
        if "USD" in salary_data["value"] or "$" in salary_data["value"]:
            currency = "USD"
        if "hour" in salary_data["value"].lower():
            salary_interval = "hourly"

    workplace_type = categories.get("workplaceType", "")
    remote = "unspecified"
    if workplace_type:
        wt = workplace_type.lower()
        if "remote" in wt:
            remote = "remote"
        elif "hybrid" in wt:
            remote = "hybrid"
        elif "onsite" in wt or "in-office" in wt:
            remote = "onsite"

    description = job.get("description", "") or ""
    description_text = description
    if description.startswith("<"):
        import html
        import re as _re
        description_text = _re.sub(r"<[^>]+>", " ", description)
        description_text = html.unescape(description_text)

    return {
        "title": job.get("text", "") or "",
        "location": categories.get("location", "") or "",
        "description": description_text,
        "application_url": apply_url,
        "company_name": categories.get("team", "").strip() or board_token.capitalize(),
        "source": "lever",
        "source_job_id": job.get("id", "") or "",
        "salary_min": salary_min,
        "salary_max": salary_max,
        "salary_currency": currency,
        "salary_interval": salary_interval,
        "remote": remote,
        "employment_type": categories.get("commitment", ""),
        "experience_level": categories.get("level", ""),
    }


def _matches_query(job: dict, query: str, location: Optional[str]) -> bool:
    lowered = job.get("title", "").lower()
    if query:
        terms = query.lower().split()
        if not any(t in lowered for t in terms):
            return False
    if location:
        loc = job.get("location", "").lower()
        if location.lower() not in loc:
            return False
    return True
