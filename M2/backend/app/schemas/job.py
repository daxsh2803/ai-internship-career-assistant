import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field, field_validator

class JobRequirementCreate(BaseModel):
    requirement_type: str = Field(..., description="HARD_SKILL, SOFT_SKILL, EDUCATION, or PROJECT")
    description: str = Field(..., min_length=3)
    is_mandatory: bool = True

class JobRequirementResponse(BaseModel):
    id: uuid.UUID
    requirement_type: str
    description: str
    is_mandatory: bool

    model_config = ConfigDict(from_attributes=True)

class JobCreateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=255, examples=["Backend Engineering Intern"])
    company_name: str = Field(..., min_length=2, max_length=255, examples=["Tech Innovations Inc."])
    location: str = Field(..., examples=["San Francisco, CA", "Bengaluru, India", "Remote"])
    is_remote: bool = False
    raw_description: str = Field(..., min_length=20)
    cleaned_markdown: Optional[str] = None
    min_gpa: float = Field(default=0.00, ge=0.0, le=4.0)
    required_graduation_years: List[int] = Field(default_factory=list, examples=[[2025, 2026]])
    visa_sponsorship_available: bool = True
    monthly_stipend_cents: Optional[int] = Field(None, ge=0, examples=[500000])
    deadline: Optional[datetime] = None
    requirements: List[JobRequirementCreate] = Field(default_factory=list)

class JobResponse(BaseModel):
    id: uuid.UUID
    title: str
    company_name: str
    location: str
    is_remote: bool
    raw_description: str
    cleaned_markdown: str
    min_gpa: float
    required_graduation_years: List[int]
    visa_sponsorship_available: bool
    monthly_stipend_cents: Optional[int]
    is_active: bool
    deadline: Optional[datetime]
    requirements: List[JobRequirementResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class JobListResponse(BaseModel):
    items: List[JobResponse]
    total: int
    page: int = 1
    page_size: int = 20

class StandardJobPosting(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    job_title: str
    company: str
    location: str
    work_mode: str = "Remote"
    is_remote: bool = True
    job_description: str
    responsibilities: List[str] = Field(default_factory=list)
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    qualifications: List[str] = Field(default_factory=list)
    experience_requirements: Union[str, List[str]] = "0-1 years (Internship / Entry-level)"
    education_requirements: Union[str, List[str]] = "Bachelor's degree or current undergraduate in Computer Science or related STEM field"
    stipend: Optional[str] = None
    domain: str = "Software Engineering"
    tags: List[str] = Field(default_factory=list)
    posted_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    @field_validator("required_skills", "preferred_skills", "tags", mode="before")
    @classmethod
    def normalize_list_strings(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            return [s.strip() for s in v.split(",") if s.strip()]
        if isinstance(v, list):
            return [str(s).strip() for s in v if str(s).strip()]
        return []

    @field_validator("responsibilities", "qualifications", mode="before")
    @classmethod
    def normalize_text_bullets(cls, v: Any) -> List[str]:
        if isinstance(v, str):
            return [s.strip() for s in v.splitlines() if s.strip()]
        if isinstance(v, list):
            return [str(s).strip() for s in v if str(s).strip()]
        return []

    model_config = ConfigDict(from_attributes=True)

class StandardJobPostingFilter(BaseModel):
    domain: Optional[str] = None
    work_mode: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    search_query: Optional[str] = None

class StandardJobPostingList(BaseModel):
    items: List[StandardJobPosting]
    total: int
    domains: List[str] = Field(default_factory=list)

class MatchedChunkInfo(BaseModel):
    chunk_type: str
    content_snippet: str
    score: float

class SemanticSearchResultItem(BaseModel):
    job: StandardJobPosting
    relevance_score: float
    matched_chunks: List[MatchedChunkInfo] = Field(default_factory=list)

class SemanticSearchRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=500)
    domain: Optional[str] = None
    is_remote: Optional[bool] = None
    top_k: int = Field(default=5, ge=1, le=50)
    use_reranker: bool = True

class SemanticSearchResponse(BaseModel):
    total_matches: int
    query: str
    results: List[SemanticSearchResultItem]
