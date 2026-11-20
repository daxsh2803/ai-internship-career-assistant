
import enum
import uuid
from typing import Optional
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON

from app.models.base import Base

class ApplicationStage(str, enum.Enum):
    WISHLIST = "WISHLIST"
    APPLIED = "APPLIED"
    SCREENING = "SCREENING"
    TECHNICAL_ASSESSMENT = "TECHNICAL_ASSESSMENT"
    INTERVIEW = "INTERVIEW"
    OFFER = "OFFER"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"

class ResumeTailoredVersion(Base):
    __tablename__ = "resume_tailored_versions"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
    )
    version_label: Mapped[str] = mapped_column(String(100), nullable=False)
    tailored_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    tailored_bullets: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    ats_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    is_approved_by_student: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

class Application(Base):
    __tablename__ = "applications"
    __table_args__ = (UniqueConstraint("candidate_id", "job_id", name="uq_candidate_job"),)

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    tailored_resume_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("resume_tailored_versions.id", ondelete="SET NULL"),
        nullable=True,
    )
    current_stage: Mapped[str] = mapped_column(
        String(50),
        default=ApplicationStage.WISHLIST.value,
        nullable=False,
        index=True,
    )
    overall_match_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    match_breakdown: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    skill_gap_roadmap: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    cover_letter_markdown: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    applied_at: Mapped[Optional[DateTime]] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    candidate = relationship("Candidate", back_populates="applications")
    job = relationship("Job", back_populates="applications")
    tailored_resume = relationship("ResumeTailoredVersion")
    stage_history = relationship(
        "ApplicationStageHistory",
        back_populates="application",
        cascade="all, delete-orphan",
        order_by="ApplicationStageHistory.transitioned_at",
    )
    interviews = relationship(
        "Interview",
        back_populates="application",
        cascade="all, delete-orphan",
    )

class ApplicationStageHistory(Base):
    __tablename__ = "application_stage_history"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    application_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    previous_stage: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    new_stage: Mapped[str] = mapped_column(String(50), nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    transitioned_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    application = relationship("Application", back_populates="stage_history")

class Interview(Base):
    __tablename__ = "interviews"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    application_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("applications.id", ondelete="CASCADE"),
        nullable=True,
    )
    candidate_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
    )
    round_type: Mapped[str] = mapped_column(String(50), nullable=False)
    dialogue_history: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    final_scorecard: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    application = relationship("Application", back_populates="interviews")
