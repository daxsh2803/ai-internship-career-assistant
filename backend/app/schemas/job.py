
import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

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
