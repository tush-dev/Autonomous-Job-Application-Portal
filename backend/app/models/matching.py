import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Boolean, Integer, Float, Text, ForeignKey, Enum as SAEnum, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.models.base import Base, BaseModelMixin


class MatchDifficulty(str, enum.Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class JobMatch(Base, BaseModelMixin):
    __tablename__ = "job_matches"
    __table_args__ = (
        UniqueConstraint("resume_id", "job_id", "user_id", name="uq_job_match_resume_job_user"),
    )

    resume_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    match_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    skills_matched: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    missing_skills: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    ats_compatibility: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    interview_probability: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    salary_fit: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    experience_fit: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    location_fit: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    growth_potential: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    learning_difficulty: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_recommended: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    resume: Mapped["Resume"] = relationship()
    job: Mapped["Job"] = relationship()
    user: Mapped["User"] = relationship()


class CareerInsight(Base, BaseModelMixin):
    __tablename__ = "career_insights"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, unique=True)

    resume_health_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ats_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    technical_strength: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    communication_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    leadership_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    project_quality: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    skill_coverage: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    completeness: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    readability: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    industry_alignment: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    career_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    suggested_skills: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    weak_bullet_points: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    missing_metrics: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    weak_action_verbs: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    formatting_suggestions: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    insights: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    user: Mapped["User"] = relationship()


class LearningPath(Base, BaseModelMixin):
    __tablename__ = "learning_paths"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_name: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    difficulty: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    priority: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    resources: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    progress: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    estimated_hours: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    user: Mapped["User"] = relationship()
