from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')
    op.execute('CREATE EXTENSION IF NOT EXISTS "vector";')

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), nullable=False, server_default="STUDENT"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_users_email", "users", ["email"])

    op.create_table(
        "candidates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("university_name", sa.String(255), nullable=False),
        sa.Column("degree_major", sa.String(255), nullable=False),
        sa.Column("gpa", sa.Numeric(3, 2), nullable=True),
        sa.Column("graduation_term", sa.String(20), nullable=False),
        sa.Column("graduation_year", sa.Integer(), nullable=False),
        sa.Column("requires_sponsorship", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("preferred_locations", postgresql.JSONB(), server_default="[]", nullable=False),
        sa.Column("overall_profile_vector", Vector(384), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "resumes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("candidate_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("file_name", sa.String(255), nullable=False),
        sa.Column("storage_path", sa.String(512), nullable=False),
        sa.Column("sha256_hash", sa.String(64), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=False, server_default="application/pdf"),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("parsed_json", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_resumes_candidate_id", "resumes", ["candidate_id"])

    op.create_table(
        "resume_sections",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("resume_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("section_type", sa.String(50), nullable=False),
        sa.Column("section_title", sa.String(100), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("structured_data", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("embedding", Vector(384), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_resume_sections_resume_id", "resume_sections", ["resume_id"])

    op.create_table(
        "skills",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("taxonomy_standard", sa.String(50), nullable=False, server_default="ESCO"),
        sa.Column("taxonomy_code", sa.String(100), nullable=True),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_skills_name", "skills", ["name"])

    op.create_table(
        "candidate_skills",
        sa.Column("candidate_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("candidates.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("skill_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("proficiency", sa.String(50), nullable=False, server_default="INTERMEDIATE"),
        sa.Column("years_experience", sa.Numeric(3, 1), nullable=False, server_default="1.0"),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    op.create_table(
        "educations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("candidate_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("institution_name", sa.String(255), nullable=False),
        sa.Column("degree", sa.String(255), nullable=False),
        sa.Column("major", sa.String(255), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("gpa", sa.Numeric(3, 2), nullable=True),
        sa.Column("relevant_coursework", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_educations_candidate_id", "educations", ["candidate_id"])

    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("candidate_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("role", sa.String(100), nullable=False, server_default="Developer"),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("bullets", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("technologies_used", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("repo_url", sa.String(512), nullable=True),
        sa.Column("live_url", sa.String(512), nullable=True),
        sa.Column("embedding", Vector(384), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_projects_candidate_id", "projects", ["candidate_id"])

    op.create_table(
        "work_experiences",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("candidate_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("company_name", sa.String(255), nullable=False),
        sa.Column("role_title", sa.String(255), nullable=False),
        sa.Column("location", sa.String(255), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("bullets", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("technologies_used", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("embedding", Vector(384), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_work_experiences_candidate_id", "work_experiences", ["candidate_id"])

    op.create_table(
        "jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("company_name", sa.String(255), nullable=False),
        sa.Column("location", sa.String(255), nullable=False),
        sa.Column("is_remote", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("raw_description", sa.Text(), nullable=False),
        sa.Column("cleaned_markdown", sa.Text(), nullable=False),
        sa.Column("min_gpa", sa.Numeric(3, 2), nullable=False, server_default="0.00"),
        sa.Column("required_graduation_years", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("visa_sponsorship_available", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("monthly_stipend_cents", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("deadline", sa.DateTime(timezone=True), nullable=True),
        sa.Column("embedding", Vector(384), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_jobs_active", "jobs", ["is_active"])
    op.create_index("idx_jobs_title", "jobs", ["title"])
    op.create_index("idx_jobs_company", "jobs", ["company_name"])

    op.create_table(
        "job_requirements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("requirement_type", sa.String(50), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("is_mandatory", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("embedding", Vector(384), nullable=True),
    )
    op.create_index("idx_job_reqs_job_id", "job_requirements", ["job_id"])

    op.create_table(
        "resume_tailored_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("candidate_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_label", sa.String(100), nullable=False),
        sa.Column("tailored_markdown", sa.Text(), nullable=False),
        sa.Column("tailored_bullets", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("ats_score", sa.Integer(), nullable=True),
        sa.Column("is_approved_by_student", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "applications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("candidate_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tailored_resume_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("resume_tailored_versions.id", ondelete="SET NULL"), nullable=True),
        sa.Column("current_stage", sa.String(50), nullable=False, server_default="WISHLIST"),
        sa.Column("overall_match_score", sa.Integer(), nullable=True),
        sa.Column("match_breakdown", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("skill_gap_roadmap", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("cover_letter_markdown", sa.Text(), nullable=True),
        sa.Column("applied_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("candidate_id", "job_id", name="uq_candidate_job"),
    )
    op.create_index("idx_applications_candidate_id", "applications", ["candidate_id"])
    op.create_index("idx_applications_job_id", "applications", ["job_id"])
    op.create_index("idx_applications_stage", "applications", ["current_stage"])

    op.create_table(
        "application_stage_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("application_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("applications.id", ondelete="CASCADE"), nullable=False),
        sa.Column("previous_stage", sa.String(50), nullable=True),
        sa.Column("new_stage", sa.String(50), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("transitioned_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_stage_history_app_id", "application_stage_history", ["application_id"])

    op.create_table(
        "interviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("application_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("applications.id", ondelete="CASCADE"), nullable=True),
        sa.Column("candidate_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("round_type", sa.String(50), nullable=False),
        sa.Column("dialogue_history", postgresql.JSONB(), nullable=False, server_default="[]"),
        sa.Column("final_scorecard", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("is_completed", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.execute(
        "CREATE INDEX idx_jobs_embedding ON jobs USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);"
    )
    op.execute(
        "CREATE INDEX idx_job_reqs_embedding ON job_requirements USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);"
    )
    op.execute(
        "CREATE INDEX idx_resume_sections_embedding ON resume_sections USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);"
    )
    op.execute(
        "CREATE INDEX idx_projects_embedding ON projects USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);"
    )

def downgrade() -> None:
    op.drop_table("interviews")
    op.drop_table("application_stage_history")
    op.drop_table("applications")
    op.drop_table("resume_tailored_versions")
    op.drop_table("job_requirements")
    op.drop_table("jobs")
    op.drop_table("work_experiences")
    op.drop_table("projects")
    op.drop_table("educations")
    op.drop_table("candidate_skills")
    op.drop_table("skills")
    op.drop_table("resume_sections")
    op.drop_table("resumes")
    op.drop_table("candidates")
    op.drop_table("users")
