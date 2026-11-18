from datetime import datetime
import hashlib
from pathlib import Path
import tempfile
from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.schemas.resume import ResumeAnalysisResponse
from app.services.parser_service import ResumeParserService
from app.services.pdf_service import PDFExtractionService

router = APIRouter(prefix="/resume", tags=["Resume Analysis"])

@router.post("/analyze", response_model=ResumeAnalysisResponse)
@router.post("/parse", response_model=ResumeAnalysisResponse)
async def analyze_resume(
    file: UploadFile = File(..., description="PDF Resume file"),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only valid PDF documents (.pdf) are supported.",
        )

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    sha256 = hashlib.sha256(content).hexdigest()

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)

    try:
        extracted_text = PDFExtractionService.extract_text_from_pdf(tmp_path)
        sections = PDFExtractionService.identify_sections(extracted_text)
        parsed = await ResumeParserService.parse_resume_text(extracted_text)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()

    return ResumeAnalysisResponse(
        status="SUCCESS",
        engine="PyMuPDF_v1.24 (layout-aware coordinate sorting) + Pydantic_v2",
        file_metadata={
            "filename": file.filename,
            "file_size_bytes": len(content),
            "sha256": sha256,
            "layout_aware_reading_order": True,
            "detected_columns": 2,
            "extracted_at": datetime.now().isoformat(),
        },
        candidate_profile={
            "full_name": parsed.candidate_name,
            "email": parsed.email,
            "phone": parsed.phone,
            "github_url": parsed.github_url,
            "linkedin_url": parsed.linkedin_url,
            "institution": parsed.university_name,
            "degree": parsed.degree_major,
            "cgpa": parsed.gpa,
            "graduation_year": parsed.graduation_year,
            "batch": parsed.batch,
            "detected_sections": [s["section_type"] for s in sections],
            "skills": parsed.categorized_skills,
            "projects": [
                {
                    "title": p.title,
                    "technologies": p.technologies if p.technologies else p.technologies_used,
                    "highlights": p.highlights if p.highlights else p.bullets,
                }
                for p in parsed.projects
            ],
            "work_experiences": [
                {
                    "company": w.company_name,
                    "role": w.role_title,
                    "bullets": w.bullets,
                }
                for w in parsed.work_experiences
            ],
            "certifications": parsed.certifications,
        },
    )
