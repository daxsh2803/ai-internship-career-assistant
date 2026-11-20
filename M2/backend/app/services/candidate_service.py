
from datetime import date
from pathlib import Path
from typing import List, Optional
import uuid
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.candidate import Candidate
from app.models.resume import Resume, ResumeSection
from app.models.skill import CandidateSkill, Education, Project, WorkExperience
from app.models.user import User
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.resume_repository import ResumeRepository
from app.schemas.candidate import (
    CandidateCreateRequest,
    CandidateDetailResponse,
    CandidateUpdateRequest,
    EducationSchema,
    ProjectSchema,
    SkillBadgeSchema,
    WorkExperienceSchema,
)
from app.schemas.resume import ResumeUploadResponse
from app.services.embedding_service import LocalEmbeddingService
from app.services.parser_service import ResumeParserService
from app.services.pdf_service import PDFExtractionService
from app.services.storage_service import LocalStorageService

class CandidateService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.candidate_repo = CandidateRepository(db)
        self.resume_repo = ResumeRepository(db)
        self.storage_service = LocalStorageService()
        self.embedder = LocalEmbeddingService.get_instance()

    async def get_or_create_candidate_profile(
        self, user: User, create_req: Optional[CandidateCreateRequest] = None
    ) -> Candidate:
        candidate = await self.candidate_repo.get_by_user_id(user.id)
        if candidate:
            return candidate

        if create_req is None:
            candidate = Candidate(
                user_id=user.id,
                university_name="University",
                degree_major="Computer Science",
                gpa=3.5,
                graduation_term="Spring",
                graduation_year=2026,
                requires_sponsorship=False,
                preferred_locations=[],
            )
        else:
            candidate = Candidate(
                user_id=user.id,
                university_name=create_req.university_name,
                degree_major=create_req.degree_major,
                gpa=create_req.gpa,
                graduation_term=create_req.graduation_term,
                graduation_year=create_req.graduation_year,
                requires_sponsorship=create_req.requires_sponsorship,
                preferred_locations=create_req.preferred_locations,
            )

        return await self.candidate_repo.create(candidate)

    async def get_candidate_details(self, user: User) -> CandidateDetailResponse:
        candidate = await self.candidate_repo.get_by_user_id(user.id)
        if not candidate:
            candidate = await self.get_or_create_candidate_profile(user)
            candidate = await self.candidate_repo.get_with_details(candidate.id)

        skills_schema = [
            SkillBadgeSchema(
                name=cs.skill.name,
                category=cs.skill.category,
                proficiency=cs.proficiency,
                years_experience=float(cs.years_experience or 1.0),
                is_verified=cs.is_verified,
            )
            for cs in candidate.skills
            if cs.skill
        ]

        educations_schema = [
            EducationSchema(
                id=edu.id,
                institution_name=edu.institution_name,
                degree=edu.degree,
                major=edu.major,
                start_date=edu.start_date,
                end_date=edu.end_date,
                gpa=float(edu.gpa) if edu.gpa is not None else None,
                relevant_coursework=edu.relevant_coursework or [],
            )
            for edu in candidate.educations
        ]

        projects_schema = [
            ProjectSchema(
                id=proj.id,
                title=proj.title,
                role=proj.role,
                summary=proj.summary,
                bullets=proj.bullets or [],
                technologies_used=proj.technologies_used or [],
                repo_url=proj.repo_url,
                live_url=proj.live_url,
            )
            for proj in candidate.projects
        ]

        work_schema = [
            WorkExperienceSchema(
                id=work.id,
                company_name=work.company_name,
                role_title=work.role_title,
                location=work.location,
                start_date=work.start_date,
                end_date=work.end_date,
                bullets=work.bullets or [],
                technologies_used=work.technologies_used or [],
            )
            for work in candidate.work_experiences
        ]

        return CandidateDetailResponse(
            id=candidate.id,
            user_id=candidate.user_id,
            university_name=candidate.university_name,
            degree_major=candidate.degree_major,
            gpa=float(candidate.gpa) if candidate.gpa is not None else None,
            graduation_term=candidate.graduation_term,
            graduation_year=candidate.graduation_year,
            requires_sponsorship=candidate.requires_sponsorship,
            preferred_locations=candidate.preferred_locations or [],
            skills=skills_schema,
            educations=educations_schema,
            projects=projects_schema,
            work_experiences=work_schema,
            created_at=candidate.created_at,
            updated_at=candidate.updated_at,
        )

    async def ingest_resume(
        self, user: User, file: UploadFile
    ) -> ResumeUploadResponse:
        candidate = await self.candidate_repo.get_by_user_id(user.id)
        if not candidate:
            candidate = await self.get_or_create_candidate_profile(user)

        storage_path_str, sha256_hash, file_size = await self.storage_service.save_resume_file(
            candidate_id=candidate.id, file=file
        )

        local_file_path = Path(storage_path_str)
        extracted_text = PDFExtractionService.extract_text_from_pdf(local_file_path)
        sections = PDFExtractionService.identify_sections(extracted_text)

        parsed_output = await ResumeParserService.parse_resume_text(extracted_text)

        profile_summary = f"{parsed_output.degree_major} at {parsed_output.university_name}. Skills: {', '.join([s.name for s in parsed_output.skills])}"
        overall_vector = self.embedder.get_embedding(profile_summary)
        candidate.overall_profile_vector = overall_vector

        await self.resume_repo.unset_primary_flags(candidate.id)

        resume = Resume(
            candidate_id=candidate.id,
            file_name=file.filename or "resume.pdf",
            storage_path=storage_path_str,
            sha256_hash=sha256_hash,
            file_size_bytes=file_size,
            is_primary=True,
            parsed_json=parsed_output.model_dump(),
        )
        self.db.add(resume)
        await self.db.flush()

        db_sections = []
        for s in sections:
            sec_embedding = self.embedder.get_embedding(s["raw_text"])
            db_sec = ResumeSection(
                resume_id=resume.id,
                section_type=s["section_type"],
                section_title=s["section_title"],
                raw_text=s["raw_text"],
                embedding=sec_embedding,
            )
            db_sections.append(db_sec)
        await self.resume_repo.add_sections(db_sections)

        for sk in parsed_output.skills:
            skill_record = await self.candidate_repo.get_or_create_skill(sk.name, sk.category)
            await self.candidate_repo.attach_skill(
                candidate_id=candidate.id,
                skill_id=skill_record.id,
                proficiency=sk.proficiency,
                years_experience=sk.years_experience,
            )

        for prj in parsed_output.projects:
            prj_embedding = self.embedder.get_embedding(f"{prj.title} {prj.summary}")
            p_obj = Project(
                candidate_id=candidate.id,
                title=prj.title,
                role=prj.role,
                summary=prj.summary,
                bullets=prj.bullets,
                technologies_used=prj.technologies_used,
                repo_url=prj.repo_url,
                embedding=prj_embedding,
            )
            await self.candidate_repo.add_project(p_obj)

        if not candidate.educations:
            for edu in parsed_output.educations:
                edu_obj = Education(
                    candidate_id=candidate.id,
                    institution_name=edu.institution_name,
                    degree=edu.degree,
                    major=edu.major,
                    start_date=date(edu.graduation_year - 4, 9, 1),
                    end_date=date(edu.graduation_year, 5, 30),
                    gpa=edu.gpa,
                    relevant_coursework=edu.coursework,
                )
                await self.candidate_repo.add_education(edu_obj)

        await self.db.flush()

        return ResumeUploadResponse(
            resume_id=resume.id,
            candidate_id=candidate.id,
            file_name=resume.file_name,
            file_size_bytes=resume.file_size_bytes,
            sha256_hash=resume.sha256_hash,
            is_primary=resume.is_primary,
            sections_extracted_count=len(db_sections),
            parsed_skills_count=len(parsed_output.skills),
            parsed_projects_count=len(parsed_output.projects),
            uploaded_at=resume.uploaded_at,
        )
