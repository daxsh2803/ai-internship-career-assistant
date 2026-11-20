
from typing import List
from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_student
from app.core.database import get_db
from app.models.user import User
from app.repositories.resume_repository import ResumeRepository
from app.schemas.candidate import (
    CandidateCreateRequest,
    CandidateDetailResponse,
    CandidateUpdateRequest,
)
from app.schemas.resume import ResumeDetailResponse, ResumeUploadResponse
from app.services.candidate_service import CandidateService

router = APIRouter(prefix="/profiles", tags=["Candidate Profiles & Resumes"])

@router.post("", response_model=CandidateDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    req: CandidateCreateRequest,
    current_user: User = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
):
    candidate_service = CandidateService(db)
    await candidate_service.get_or_create_candidate_profile(current_user, req)
    return await candidate_service.get_candidate_details(current_user)

@router.get("/me", response_model=CandidateDetailResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
):
    candidate_service = CandidateService(db)
    return await candidate_service.get_candidate_details(current_user)

@router.post("/resume/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(..., description="Resume PDF file (max 10MB)"),
    current_user: User = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
):
    candidate_service = CandidateService(db)
    return await candidate_service.ingest_resume(current_user, file)

@router.get("/resumes", response_model=List[ResumeDetailResponse])
async def list_resumes(
    current_user: User = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
):
    candidate_service = CandidateService(db)
    candidate = await candidate_service.get_or_create_candidate_profile(current_user)
    resume_repo = ResumeRepository(db)
    resumes = await resume_repo.get_by_candidate_id(candidate.id)
    return [ResumeDetailResponse.model_validate(r) for r in resumes]
