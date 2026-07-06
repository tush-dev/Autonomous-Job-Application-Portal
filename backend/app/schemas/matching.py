import uuid
from pydantic import BaseModel, field_serializer
from typing import Optional
from datetime import datetime


class JobMatchResponse(BaseModel):
    id: str
    job_id: str
    match_score: float
    skills_matched: list[str] = []
    missing_skills: list[str] = []
    ats_compatibility: Optional[float] = None
    interview_probability: Optional[float] = None
    salary_fit: Optional[float] = None
    experience_fit: Optional[float] = None
    location_fit: Optional[float] = None
    growth_potential: Optional[float] = None
    learning_difficulty: Optional[str] = None
    reasoning: Optional[str] = None
    is_recommended: bool = False

    class Config:
        from_attributes = True

    @field_serializer("id", "job_id")
    @classmethod
    def serialize_uuid(cls, v):
        if isinstance(v, uuid.UUID):
            return str(v)
        return v


class JobWithMatchResponse(BaseModel):
    id: str
    title: str
    company: Optional[dict] = None
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str = "USD"
    remote: str = "unspecified"
    application_url: Optional[str] = None
    source: str = ""
    employment_type: Optional[str] = None
    posted_at: datetime
    match: Optional[JobMatchResponse] = None

    class Config:
        from_attributes = True
    is_saved: bool = False
    has_applied: bool = False


class CareerInsightResponse(BaseModel):
    resume_health_score: Optional[float] = None
    ats_score: Optional[float] = None
    technical_strength: Optional[float] = None
    communication_score: Optional[float] = None
    leadership_score: Optional[float] = None
    project_quality: Optional[float] = None
    skill_coverage: Optional[float] = None
    completeness: Optional[float] = None
    readability: Optional[float] = None
    industry_alignment: Optional[str] = None
    career_level: Optional[str] = None
    suggested_skills: list[str] = []
    weak_bullet_points: list[str] = []
    missing_metrics: list[str] = []
    weak_action_verbs: list[str] = []
    formatting_suggestions: list[str] = []
    insights: dict = {}

    class Config:
        from_attributes = True


class LearningPathResponse(BaseModel):
    id: str
    skill_name: str
    category: Optional[str] = None
    difficulty: Optional[str] = None
    priority: Optional[str] = None
    resources: Optional[dict] = None
    progress: float = 0.0
    completed: bool = False
    estimated_hours: Optional[int] = None

    class Config:
        from_attributes = True


class DashboardResponse(BaseModel):
    resume_health: Optional[CareerInsightResponse] = None
    recommended_jobs: list[JobWithMatchResponse] = []
    recent_jobs: list[JobWithMatchResponse] = []
    upcoming_interviews: list[dict] = []
    application_stats: Optional[dict] = None
    learning_path: list[LearningPathResponse] = []
    career_insights: Optional[CareerInsightResponse] = None
