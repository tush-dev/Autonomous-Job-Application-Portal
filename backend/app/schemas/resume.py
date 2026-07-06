from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class ResumeUploadResponse(BaseModel):
    id: str
    file_name: str
    file_size: int
    file_type: str
    parsing_status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ResumeResponse(BaseModel):
    id: str
    file_name: str
    file_size: int
    file_type: str
    raw_text: Optional[str] = None
    parsed_data: Optional[dict] = None
    parsing_confidence: Optional[float] = None
    parsing_status: str
    parsing_error: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ResumeUpdateRequest(BaseModel):
    parsed_data: Optional[dict] = None


class SkillItem(BaseModel):
    name: str
    category: str
    proficiency: str
    years: int = 0


class ResumeAnalysisResponse(BaseModel):
    skills: list[SkillItem]
    career_level: Optional[str] = None
    industry: Optional[str] = None
    missing_skills: list[str] = []
    strengths: list[str] = []
    weaknesses: list[str] = []
    summary: Optional[str] = None
    experience_summary: Optional[str] = None
    recommended_roles: list[str] = []
    skill_graph: Optional[dict] = None


class ResumeTailorRequest(BaseModel):
    resume_id: str
    job_id: str
    format: str = Field(default="ats_friendly", pattern="^(ats_friendly|standard|detailed)$")


class ResumeTailorResponse(BaseModel):
    id: str
    ats_score: float
    version: int
    content: dict
    created_at: datetime


class ParsedResumeData(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    skills: list[str] = []
    experience: list[dict] = []
    projects: list[dict] = []
    education: list[dict] = []
    certifications: list[str] = []
    summary: str = ""
