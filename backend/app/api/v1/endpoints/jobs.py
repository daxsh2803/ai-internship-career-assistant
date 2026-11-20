
import tempfile
from pathlib import Path
from typing import Optional
import uuid
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.job import (
    JobCreateRequest,
    JobListResponse,
    JobResponse,
    SemanticSearchRequest,
    SemanticSearchResponse,
)
from app.schemas.matching import (
    CandidateProfile,
    MatchRequest,
    MatchResponse,
)
from app.services.job_service import JobService
from app.services.matching_agent import JobResumeMatchingAgent
from app.services.parser_service import ResumeParserService
from app.services.pdf_service import PdfService
from app.services.retrieval_service import HybridRetrievalService

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

@router.post("/semantic-search", response_model=SemanticSearchResponse)
def semantic_search(req: SemanticSearchRequest):
    retrieval_service = HybridRetrievalService.get_instance()
    return retrieval_service.search(
        query=req.query,
        domain=req.domain,
        is_remote=req.is_remote,
        top_k=req.top_k,
        use_reranker=req.use_reranker,
    )

@router.post("/match", response_model=MatchResponse)
def match_jobs(req: MatchRequest):
    agent = JobResumeMatchingAgent.get_instance()
    return agent.match_jobs(req)

@router.post("/match-resume", response_model=MatchResponse)
async def match_resume(
    file: UploadFile = File(...),
    top_k: int = Form(10),
    domain: Optional[str] = Form(None),
    is_remote: Optional[bool] = Form(None),
    use_llm_reasoning: bool = Form(False),
):
    content = await file.read()
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        raw_text = PdfService.extract_text_from_pdf(tmp_path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()

    parsed = await ResumeParserService.parse_resume_text(raw_text)

    candidate_profile = CandidateProfile(
        candidate_name=parsed.candidate_name,
        email=parsed.email,
        phone=parsed.phone,
        university_name=parsed.university_name,
        degree_major=parsed.degree_major,
        gpa=parsed.gpa,
        graduation_year=parsed.graduation_year,
        batch=parsed.batch,
        skills=[{"name": s.name, "category": s.category, "proficiency": s.proficiency} for s in parsed.skills],
        educations=[e.model_dump() for e in parsed.educations],
        projects=[p.model_dump() for p in parsed.projects],
        work_experiences=[w.model_dump() for w in parsed.work_experiences],
        certifications=parsed.certifications,
    )

    req = MatchRequest(
        candidate_profile=candidate_profile,
        top_k=top_k,
        domain=domain,
        is_remote=is_remote,
        use_llm_reasoning=use_llm_reasoning,
    )
    agent = JobResumeMatchingAgent.get_instance()
    return agent.match_jobs(req)
