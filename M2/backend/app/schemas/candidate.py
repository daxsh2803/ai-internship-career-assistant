
import uuid
from datetime import date, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

class SkillBadgeSchema(BaseModel):
    name: str = Field(..., examples=["Python", "FastAPI", "PostgreSQL"])
    category: str = Field(default="Technical Skills", examples=["Programming Languages", "Cloud & DevOps"])
    proficiency: str = Field(default="INTERMEDIATE", examples=["BEGINNER", "INTERMEDIATE", "ADVANCED", "EXPERT"])
    years_experience: float = Field(default=1.0, ge=0.0, le=20.0)
    is_verified: bool = False

    model_config = ConfigDict(from_attributes=True)

class EducationSchema(BaseModel):
    id: Optional[uuid.UUID] = None
    institution_name: str = Field(..., examples=["Stanford University"])
    degree: str = Field(..., examples=["Bachelor of Science"])
    major: str = Field(..., examples=["Computer Science"])
    start_date: date
    end_date: Optional[date] = None
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    relevant_coursework: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

class ProjectSchema(BaseModel):
    id: Optional[uuid.UUID] = None
    title: str = Field(..., examples=["Distributed Event Processing Engine"])
    role: str = Field(default="Developer")
    summary: str
    bullets: List[str] = Field(default_factory=list)
    technologies_used: List[str] = Field(default_factory=list)
    repo_url: Optional[str] = None
    live_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class WorkExperienceSchema(BaseModel):
    id: Optional[uuid.UUID] = None
    company_name: str = Field(..., examples=["Acme Corp"])
    role_title: str = Field(..., examples=["Software Engineer Intern"])
    location: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    bullets: List[str] = Field(default_factory=list)
    technologies_used: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

class CandidateCreateRequest(BaseModel):
    university_name: str = Field(..., min_length=2, max_length=255)
    degree_major: str = Field(..., min_length=2, max_length=255)
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    graduation_term: str = Field(..., examples=["Spring", "Fall", "Summer"])
    graduation_year: int = Field(..., ge=2024, le=2032)
    requires_sponsorship: bool = False
    preferred_locations: List[str] = Field(default_factory=list)

class CandidateUpdateRequest(BaseModel):
    university_name: Optional[str] = None
    degree_major: Optional[str] = None
    gpa: Optional[float] = Field(None, ge=0.0, le=4.0)
    graduation_term: Optional[str] = None
    graduation_year: Optional[int] = Field(None, ge=2024, le=2032)
    requires_sponsorship: Optional[bool] = None
    preferred_locations: Optional[List[str]] = None

class CandidateDetailResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    university_name: str
    degree_major: str
    gpa: Optional[float]
    graduation_term: str
    graduation_year: int
    requires_sponsorship: bool
    preferred_locations: List[str]
    skills: List[SkillBadgeSchema] = Field(default_factory=list)
    educations: List[EducationSchema] = Field(default_factory=list)
    projects: List[ProjectSchema] = Field(default_factory=list)
    work_experiences: List[WorkExperienceSchema] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
