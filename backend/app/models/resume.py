import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Boolean, Integer, Float, Text, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.models.base import Base, BaseModelMixin


class ParsingStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class FileType(str, enum.Enum):
    PDF = "pdf"
    DOCX = "docx"


class Resume(Base, BaseModelMixin):
    __tablename__ = "resumes"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    file_key: Mapped[str] = mapped_column(String(512), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    file_type: Mapped[FileType] = mapped_column(SAEnum(FileType, name="file_type", create_type=False), nullable=False)
    parsed_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    parsing_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    parsing_status: Mapped[ParsingStatus] = mapped_column(
        SAEnum(ParsingStatus, name="parsing_status", create_type=False),
        default=ParsingStatus.PENDING,
        nullable=False,
    )
    parsing_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user: Mapped["User"] = relationship(back_populates="resumes")
    versions: Mapped[list["ResumeVersion"]] = relationship(back_populates="resume", cascade="all, delete-orphan")
    skill_graph: Mapped[Optional["ResumeSkillGraph"]] = relationship(back_populates="resume", uselist=False, cascade="all, delete-orphan")


class ResumeVersion(Base, BaseModelMixin):
    __tablename__ = "resume_versions"

    resume_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    parsed_data: Mapped[dict] = mapped_column(JSONB, nullable=False)
    change_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    resume: Mapped["Resume"] = relationship(back_populates="versions")


class ResumeSkillGraph(Base, BaseModelMixin):
    __tablename__ = "resume_skill_graph"

    resume_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, unique=True)
    skills: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    career_level: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    missing_skills: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    strengths: Mapped[Optional[list]] = mapped_column(ARRAY(String), nullable=True)
    weaknesses: Mapped[Optional[list]] = mapped_column(ARRAY(String), nullable=True)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    embedding: Mapped[Optional[list]] = mapped_column(nullable=True)

    resume: Mapped["Resume"] = relationship(back_populates="skill_graph")


class GeneratedResume(Base, BaseModelMixin):
    __tablename__ = "generated_resumes"

    application_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("job_applications.id", ondelete="CASCADE"), nullable=False)
    resume_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=False)
    content: Mapped[dict] = mapped_column(JSONB, nullable=False)
    file_key: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    version: Mapped[int] = mapped_column(default=1, nullable=False)
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    user_edited: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ats_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
