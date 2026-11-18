
import uuid
from typing import List, Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job, JobRequirement
from app.repositories.job_repository import JobRepository
from app.schemas.job import (
    JobCreateRequest,
    JobListResponse,
    JobRequirementResponse,
    JobResponse,
)
from app.services.embedding_service import LocalEmbeddingService

class JobService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.job_repo = JobRepository(db)
        self.embedder = LocalEmbeddingService.get_instance()

    async def create_job(self, req: JobCreateRequest) -> JobResponse:
        cleaned_markdown = req.cleaned_markdown or req.raw_description

        semantic_text = f"{req.title} at {req.company_name}. Location: {req.location}. {cleaned_markdown}"
        job_vector = self.embedder.get_embedding(semantic_text)

        job = Job(
            title=req.title.strip(),
            company_name=req.company_name.strip(),
            location=req.location.strip(),
            is_remote=req.is_remote,
            raw_description=req.raw_description.strip(),
            cleaned_markdown=cleaned_markdown.strip(),
            min_gpa=req.min_gpa,
            required_graduation_years=req.required_graduation_years,
            visa_sponsorship_available=req.visa_sponsorship_available,
            monthly_stipend_cents=req.monthly_stipend_cents,
            is_active=True,
            deadline=req.deadline,
            embedding=job_vector,
        )
        await self.job_repo.create(job)

        requirements_to_add = []
        for r in req.requirements:
            r_vector = self.embedder.get_embedding(r.description)
            r_obj = JobRequirement(
                job_id=job.id,
                requirement_type=r.requirement_type,
                description=r.description.strip(),
                is_mandatory=r.is_mandatory,
                embedding=r_vector,
            )
            requirements_to_add.append(r_obj)

        if requirements_to_add:
            await self.job_repo.add_requirements(requirements_to_add)

        job_full = await self.job_repo.get_with_requirements(job.id)
        return self._map_to_response(job_full)

    async def get_job_by_id(self, job_id: uuid.UUID) -> JobResponse:
        job = await self.job_repo.get_with_requirements(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job posting with ID {job_id} not found.",
            )
        return self._map_to_response(job)

    async def list_jobs(
        self,
        page: int = 1,
        page_size: int = 20,
        is_remote: Optional[bool] = None,
        max_gpa_requirement: Optional[float] = None,
        search_query: Optional[str] = None,
    ) -> JobListResponse:
        skip = (page - 1) * page_size
        items, total = await self.job_repo.list_jobs(
            skip=skip,
            limit=page_size,
            is_remote=is_remote,
            max_gpa_requirement=max_gpa_requirement,
            search_query=search_query,
        )

        response_items = [self._map_to_response(j) for j in items]
        return JobListResponse(
            items=response_items,
            total=total,
            page=page,
            page_size=page_size,
        )

    @staticmethod
    def _map_to_response(job: Job) -> JobResponse:
        req_schemas = [
            JobRequirementResponse(
                id=r.id,
                requirement_type=r.requirement_type,
                description=r.description,
                is_mandatory=r.is_mandatory,
            )
            for r in job.requirements
        ]
        return JobResponse(
            id=job.id,
            title=job.title,
            company_name=job.company_name,
            location=job.location,
            is_remote=job.is_remote,
            raw_description=job.raw_description,
            cleaned_markdown=job.cleaned_markdown,
            min_gpa=float(job.min_gpa or 0.0),
            required_graduation_years=job.required_graduation_years or [],
            visa_sponsorship_available=job.visa_sponsorship_available,
            monthly_stipend_cents=job.monthly_stipend_cents,
            is_active=job.is_active,
            deadline=job.deadline,
            requirements=req_schemas,
            created_at=job.created_at,
            updated_at=job.updated_at,
        )
