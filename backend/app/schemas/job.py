from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class JobSearchRequest(BaseModel):
    query: str = ""
    location: Optional[str] = None
    remote: Optional[str] = Field(default=None, pattern="^(remote|hybrid|onsite|any)?$")
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sources: Optional[list[str]] = None
    exclude_applied: bool = False
    min_match_score: Optional[float] = Field(default=None, ge=0, le=100)
    sort_by: Optional[str] = Field(default=None, pattern="^(match|recent)?$")


class CompanyResponse(BaseModel):
    id: str
    name: str
    logo_url: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None

    class Config:
        from_attributes = True


class JobMatchBrief(BaseModel):
    match_score: float
    skills_matched: list[str] = []
    missing_skills: list[str] = []
    ats_compatibility: Optional[float] = None
    interview_probability: Optional[float] = None
    reasoning: Optional[str] = None
    is_recommended: bool = False


class JobResponse(BaseModel):
    id: str
    company: Optional[CompanyResponse] = None
    source: str
    title: str
    location: Optional[str] = None
    remote: str
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str = "USD"
    employment_type: Optional[str] = None
    experience_level: Optional[str] = None
    skills_required: list[str] = []
    application_url: Optional[str] = None
    posted_at: datetime
    is_saved: bool = False
    has_applied: bool = False
    match: Optional[JobMatchBrief] = None

    class Config:
        from_attributes = True


class JobSearchResponse(BaseModel):
    jobs: list[JobResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
