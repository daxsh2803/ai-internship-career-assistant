from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.job import StandardJobPosting

class CandidateProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    candidate_name: str = Field(default="Candidate")
    email: Optional[str] = None
    phone: Optional[str] = None
    university_name: Optional[str] = None
    degree_major: Optional[str] = None
    gpa: Optional[float] = None
    graduation_year: Optional[int] = None
    batch: Optional[str] = None
    skills: List[Union[str, Dict[str, Any]]] = Field(default_factory=list)
    educations: List[Dict[str, Any]] = Field(default_factory=list)
    projects: List[Dict[str, Any]] = Field(default_factory=list)
    work_experiences: List[Dict[str, Any]] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    summary: Optional[str] = None

class ScoreBreakdown(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    required_skills_score: float = Field(..., ge=0.0, le=100.0)
    preferred_skills_score: float = Field(..., ge=0.0, le=100.0)
    projects_experience_score: float = Field(..., ge=0.0, le=100.0)
    education_qualifications_score: float = Field(..., ge=0.0, le=100.0)
    semantic_relevance_score: float = Field(..., ge=0.0, le=100.0)

class JobMatchResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    job: StandardJobPosting
    overall_match_score: float = Field(..., ge=0.0, le=100.0)
    score_breakdown: ScoreBreakdown
    matched_skills: List[str] = Field(default_factory=list)
    missing_required_skills: List[str] = Field(default_factory=list)
    missing_preferred_skills: List[str] = Field(default_factory=list)
    reasoning: str
    recommendation_tier: str

class MatchRequest(BaseModel):
    candidate_profile: CandidateProfile
    top_k: int = Field(default=10, ge=1, le=50)
    domain: Optional[str] = None
    is_remote: Optional[bool] = None
    use_llm_reasoning: bool = False

class MatchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    candidate_name: str
    candidate_skills: List[str] = Field(default_factory=list)
    total_evaluated_jobs: int
    results: List[JobMatchResult] = Field(default_factory=list)
