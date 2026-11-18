
from typing import Optional
import uuid
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.job import (
    JobCreateRequest,
    JobListResponse,
    JobResponse,
)
from app.services.job_service import JobService

router = APIRouter(prefix="/jobs", tags=["Job Postings & Discovery"])

@router.get("", response_model=JobListResponse)
async def list_jobs(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    is_remote: Optional[bool] = Query(None, description="Filter for remote roles"),
    max_gpa: Optional[float] = Query(None, ge=0.0, le=4.0, description="Filter by candidate GPA eligibility"),
    q: Optional[str] = Query(None, description="Keyword search query"),
    db: AsyncSession = Depends(get_db),
):
    job_service = JobService(db)
    return await job_service.list_jobs(
        page=page,
        page_size=page_size,
        is_remote=is_remote,
        max_gpa_requirement=max_gpa,
        search_query=q,
    )

@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    req: JobCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    job_service = JobService(db)
    return await job_service.create_job(req)

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    job_service = JobService(db)
    return await job_service.get_job_by_id(job_id)
