import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Boolean, Integer, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.models.base import Base, BaseModelMixin


class ApplicationStatus(str, enum.Enum):
    DRAFT = "draft"
    SAVED = "saved"
    APPLIED = "applied"
    SCREENING = "screening"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    FAILED = "failed"


class CoverLetterTone(str, enum.Enum):
    PROFESSIONAL = "professional"
    SHORT = "short"
    CUSTOM = "custom"


class JobApplication(Base, BaseModelMixin):
    __tablename__ = "job_applications"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    job_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    resume_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=True)
    status: Mapped[ApplicationStatus] = mapped_column(
        SAEnum(ApplicationStatus, name="application_status", create_type=False),
        default=ApplicationStatus.DRAFT,
        nullable=False,
        index=True,
    )
    submission_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    submission_result: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    approval_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    approved_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    applied_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    source_application_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship(back_populates="applications")
    job: Mapped["Job"] = relationship(back_populates="applications")
    timeline: Mapped[list["ApplicationTimeline"]] = relationship(back_populates="application", cascade="all, delete-orphan")
    cover_letter: Mapped[Optional["CoverLetter"]] = relationship(back_populates="application", uselist=False, cascade="all, delete-orphan")


class ApplicationTimeline(Base, BaseModelMixin):
    __tablename__ = "application_timeline"

    application_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("job_applications.id", ondelete="CASCADE"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    application: Mapped["JobApplication"] = relationship(back_populates="timeline")


class CoverLetter(Base, BaseModelMixin):
    __tablename__ = "cover_letters"

    application_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("job_applications.id", ondelete="CASCADE"), nullable=False, unique=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tone: Mapped[CoverLetterTone] = mapped_column(
        SAEnum(CoverLetterTone, name="cover_letter_tone", create_type=False),
        nullable=False,
    )
    word_count: Mapped[int] = mapped_column(Integer, nullable=False)
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    user_edited: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    version: Mapped[int] = mapped_column(default=1, nullable=False)

    application: Mapped["JobApplication"] = relationship(back_populates="cover_letter")
