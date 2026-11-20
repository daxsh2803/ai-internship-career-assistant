
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

class ApplicationCreateRequest(BaseModel):
    job_id: uuid.UUID
    cover_letter_markdown: Optional[str] = None

class ApplicationStageUpdateRequest(BaseModel):
    new_stage: str = Field(
        ...,
        description="WISHLIST, APPLIED, SCREENING, TECHNICAL_ASSESSMENT, INTERVIEW, OFFER, REJECTED, WITHDRAWN",
    )
    notes: Optional[str] = Field(None, max_length=1000)

class StageHistoryEntry(BaseModel):
    id: uuid.UUID
    previous_stage: Optional[str]
    new_stage: str
    notes: Optional[str]
    transitioned_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ApplicationResponse(BaseModel):
    id: uuid.UUID
    candidate_id: uuid.UUID
    job_id: uuid.UUID
    job_title: Optional[str] = None
    company_name: Optional[str] = None
    current_stage: str
    overall_match_score: Optional[int] = None
    match_breakdown: Dict[str, Any] = Field(default_factory=dict)
    skill_gap_roadmap: Dict[str, Any] = Field(default_factory=dict)
    cover_letter_markdown: Optional[str] = None
    applied_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    stage_history: List[StageHistoryEntry] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)

class KanbanBoardResponse(BaseModel):
    wishlist: List[ApplicationResponse] = Field(default_factory=list)
    applied: List[ApplicationResponse] = Field(default_factory=list)
    screening: List[ApplicationResponse] = Field(default_factory=list)
    technical_assessment: List[ApplicationResponse] = Field(default_factory=list)
    interview: List[ApplicationResponse] = Field(default_factory=list)
    offer: List[ApplicationResponse] = Field(default_factory=list)
    rejected: List[ApplicationResponse] = Field(default_factory=list)
    withdrawn: List[ApplicationResponse] = Field(default_factory=list)
