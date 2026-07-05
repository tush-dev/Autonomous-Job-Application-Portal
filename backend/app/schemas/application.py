from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ApplicationCreateRequest(BaseModel):
    job_id: str
    resume_id: str
    approval_required: bool = True
    notes: Optional[str] = None


class ApplicationSubmitRequest(BaseModel):
    cover_letter_id: Optional[str] = None
    generated_resume_id: Optional[str] = None
    additional_answers: Optional[dict] = None


class CoverLetterGenerateRequest(BaseModel):
    application_id: str
    tone: str = Field(default="professional", pattern="^(professional|short|custom)$")
    custom_instructions: Optional[str] = None


class CoverLetterResponse(BaseModel):
    id: str
    content: str
    tone: str
    word_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class TimelineEvent(BaseModel):
    id: str
    event_type: str
    description: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ApplicationResponse(BaseModel):
    id: str
    job: dict
    status: str
    approval_required: bool
    submitted_at: Optional[datetime] = None
    notes: Optional[str] = None
    timeline: list[TimelineEvent] = []
    cover_letter: Optional[CoverLetterResponse] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApplicationStatsResponse(BaseModel):
    total: int = 0
    applied: int = 0
    screening: int = 0
    interview: int = 0
    offer: int = 0
    rejected: int = 0
    failed: int = 0
    interview_rate: float = 0.0
    offer_rate: float = 0.0
