import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Boolean, Integer, Text, Float, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.models.base import Base, BaseModelMixin


class JobSource(str, enum.Enum):
    GREENHOUSE = "greenhouse"
    LEVER = "lever"
    WELLFOUND = "wellfound"
    LINKEDIN = "linkedin"
    REMOTEOK = "remoteok"
    YC_JOBS = "yc_jobs"
    COMPANY_CAREERS = "company_careers"
    RSS_FEED = "rss_feed"
    MANUAL = "manual"


class RemoteType(str, enum.Enum):
    REMOTE = "remote"
    HYBRID = "hybrid"
    ONSITE = "onsite"
    UNSPECIFIED = "unspecified"


class SalaryInterval(str, enum.Enum):
    HOURLY = "hourly"
    YEARLY = "yearly"
    MONTHLY = "monthly"


class ApplicationType(str, enum.Enum):
    URL = "url"
    FORM = "form"
    EMAIL = "email"
    API = "api"
    UNKNOWN = "unknown"


class Company(Base, BaseModelMixin):
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    website: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    size: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    headquarters: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    careers_page_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    ats_provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    embedding: Mapped[Optional[list]] = mapped_column(nullable=True)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    jobs: Mapped[list["Job"]] = relationship(back_populates="company", cascade="all, delete-orphan")


class Job(Base, BaseModelMixin):
    __tablename__ = "jobs"

    company_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True)
    source: Mapped[JobSource] = mapped_column(SAEnum(JobSource, name="job_source", create_type=False), nullable=False)
    source_job_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    description_embedding: Mapped[Optional[list]] = mapped_column(nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    remote: Mapped[RemoteType] = mapped_column(
        SAEnum(RemoteType, name="remote_type", create_type=False),
        default=RemoteType.UNSPECIFIED,
    )
    salary_min: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    salary_max: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    salary_currency: Mapped[str] = mapped_column(String(3), default="USD")
    salary_interval: Mapped[SalaryInterval] = mapped_column(
        SAEnum(SalaryInterval, name="salary_interval", create_type=False),
        default=SalaryInterval.YEARLY,
    )
    employment_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    experience_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    skills_required: Mapped[Optional[list]] = mapped_column(ARRAY(String), nullable=True)
    application_url: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    application_type: Mapped[ApplicationType] = mapped_column(
        SAEnum(ApplicationType, name="application_type", create_type=False),
        default=ApplicationType.UNKNOWN,
    )
    expires_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    raw_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    company: Mapped[Optional["Company"]] = relationship(back_populates="jobs")
    applications: Mapped[list["JobApplication"]] = relationship(back_populates="job")


class SavedJob(Base, BaseModelMixin):
    __tablename__ = "saved_jobs"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    match_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    match_reasons: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    missing_skills: Mapped[Optional[list]] = mapped_column(ARRAY(String), nullable=True)
