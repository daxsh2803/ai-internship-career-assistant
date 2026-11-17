
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

class ResumeSectionSchema(BaseModel):
    id: Optional[uuid.UUID] = None
    section_type: str
    section_title: str
    raw_text: str
    structured_data: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)

class ResumeUploadResponse(BaseModel):
    resume_id: uuid.UUID
    candidate_id: uuid.UUID
    file_name: str
    file_size_bytes: int
    sha256_hash: str
    is_primary: bool
    sections_extracted_count: int
    parsed_skills_count: int
    parsed_projects_count: int
    message: str = "Resume successfully uploaded, extracted, and indexed."
    uploaded_at: datetime

class ResumeDetailResponse(BaseModel):
    id: uuid.UUID
    candidate_id: uuid.UUID
    file_name: str
    file_size_bytes: int
    sha256_hash: str
    is_primary: bool
    parsed_json: Dict[str, Any]
    sections: List[ResumeSectionSchema] = Field(default_factory=list)
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ResumeAnalysisResponse(BaseModel):
    status: str = "SUCCESS"
    engine: str = "PyMuPDF_v1.24 (layout-aware coordinate sorting) + Pydantic_v2"
    file_metadata: Dict[str, Any]
    candidate_profile: Dict[str, Any]
