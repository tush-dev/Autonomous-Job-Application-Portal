from abc import ABC, abstractmethod
from typing import Optional
import structlog

logger = structlog.get_logger()


class BaseCrawler(ABC):
    def __init__(self):
        self.source_name = self.__class__.__name__.lower().replace("crawler", "")
        self.logger = logger.bind(source=self.source_name)

    @abstractmethod
    async def crawl(self, **kwargs) -> list[dict]:
        pass

    @abstractmethod
    def normalize(self, raw_job: dict) -> dict:
        pass

    def normalize_common(self, raw: dict) -> dict:
        return {
            "source": self.source_name,
            "source_job_id": raw.get("id") or raw.get("external_id"),
            "title": raw.get("title", ""),
            "description": raw.get("description", raw.get("content", "")),
            "location": raw.get("location", raw.get("office_location")),
            "remote": self._parse_remote(raw),
            "salary_min": raw.get("salary_min"),
            "salary_max": raw.get("salary_max"),
            "salary_currency": raw.get("salary_currency", "USD"),
            "employment_type": raw.get("employment_type"),
            "experience_level": raw.get("experience_level"),
            "skills_required": raw.get("skills", []),
            "application_url": raw.get("application_url") or raw.get("url"),
            "company_name": raw.get("company_name") or raw.get("company"),
            "company_website": raw.get("company_website"),
            "company_logo": raw.get("company_logo"),
            "posted_at": raw.get("posted_at") or raw.get("created_at"),
        }

    def _parse_remote(self, raw: dict) -> str:
        remote = str(raw.get("remote", "")).lower()
        if remote in ("true", "yes", "remote", "fully remote"):
            return "remote"
        if remote in ("hybrid", "partial"):
            return "hybrid"
        if remote in ("false", "no", "onsite", "on-site"):
            return "onsite"
        return "unspecified"
