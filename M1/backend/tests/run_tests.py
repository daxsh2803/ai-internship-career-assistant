
from datetime import datetime
from pathlib import Path
import sys
import uuid

backend_root = str(Path(__file__).resolve().parent.parent)
if backend_root not in sys.path:
    sys.path.insert(0, backend_root)

from app.core.config import settings
from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    verify_password,
)
from app.main import health_check
from app.models import (
    Application,
    ApplicationStage,
    Candidate,
    Job,
    Resume,
    User,
    UserRole,
)
from app.schemas.application import (
    ApplicationCreateRequest,
    ApplicationResponse,
    ApplicationStageUpdateRequest,
    KanbanBoardResponse,
)
from app.schemas.auth import TokenResponse, UserLoginRequest, UserRegisterRequest, UserResponse
from app.schemas.candidate import (
    CandidateCreateRequest,
    CandidateDetailResponse,
    EducationSchema,
    ProjectSchema,
    SkillBadgeSchema,
)
from app.schemas.job import JobCreateRequest, JobListResponse, JobRequirementCreate, JobResponse
from app.schemas.resume import ResumeUploadResponse
from app.services.embedding_service import LocalEmbeddingService
from app.services.parser_service import ResumeParserService
from app.services.pdf_service import PDFExtractionService

def run_coroutine_sync(coro):
    try:
        coro.send(None)
    except StopIteration as e:
        return e.value

def test_health_check_service():
    print("[1/6] Testing System Health Check Endpoint Logic...", flush=True)
    data = run_coroutine_sync(health_check())
    assert data["status"] == "ok"
    assert data["service"] == settings.PROJECT_NAME
    assert data["version"] == settings.VERSION
    assert data["environment"] == "development"
    print(f"  --> Health check passed: status={data['status']}, version={data['version']}", flush=True)

def test_security_and_jwt():
    print("[2/6] Testing Password Hashing & HS256 JWT Token Lifecycle...", flush=True)
    password = "SuperSecretSecurePassword123!"
    pw_hash = get_password_hash(password)
    assert verify_password(password, pw_hash)
    assert not verify_password("WrongPassword!", pw_hash)
    assert len(pw_hash) == 64

    user_id = uuid.uuid4()
    token = create_access_token(
        subject=str(user_id),
        extra_claims={"email": "student@stanford.edu", "role": "STUDENT"},
    )
    assert token.count(".") == 2

    payload = decode_access_token(token)
    assert payload["sub"] == str(user_id)
    assert payload["email"] == "student@stanford.edu"
    assert payload["role"] == "STUDENT"
    assert payload["exp"] > payload["iat"]
    print("  --> Password hashing & JWT verification passed.", flush=True)

def test_pydantic_schemas_validation():
    print("[3/6] Testing Pydantic v2 Domain Schemas...", flush=True)
    candidate_req = CandidateCreateRequest(
        university_name="Stanford University",
        degree_major="Computer Science",
        gpa=3.85,
        graduation_term="Spring",
        graduation_year=2026,
        requires_sponsorship=False,
        preferred_locations=["San Francisco, CA", "Remote"],
    )
    assert candidate_req.gpa == 3.85
    assert candidate_req.graduation_year == 2026

    job_req = JobCreateRequest(
        title="Backend Engineering Intern",
        company_name="CloudScale Systems",
        location="Remote",
        is_remote=True,
        raw_description="Build async microservices using FastAPI and PostgreSQL with vector embeddings.",
        min_gpa=3.0,
        required_graduation_years=[2025, 2026],
        requirements=[
            JobRequirementCreate(
                requirement_type="HARD_SKILL",
                description="Python and FastAPI async development.",
                is_mandatory=True,
            )
        ],
    )
    assert job_req.is_remote is True
    assert len(job_req.requirements) == 1

    app_update = ApplicationStageUpdateRequest(new_stage="TECHNICAL_ASSESSMENT", notes="Passed phone screen.")
    assert app_update.new_stage == "TECHNICAL_ASSESSMENT"
    print("  --> Domain schemas validated with strict type integrity.", flush=True)

def test_pdf_extraction_service():
    print("[4/6] Testing PyMuPDF Layout-Aware Extraction Service...", flush=True)
    sample_pdf = Path("./tests/poc/sample_multicolumn_resume.pdf")
    if sample_pdf.exists():
        extracted_text = PDFExtractionService.extract_text_from_pdf(sample_pdf)
        assert len(extracted_text) > 100
        sections = PDFExtractionService.identify_sections(extracted_text)
        assert len(sections) >= 2
        print(f"  --> Extracted {len(extracted_text)} chars across {len(sections)} sections from PDF.", flush=True)
    else:
        print("  --> (Skipped sample PDF check: sample file not present)", flush=True)

def test_dense_embedding_service():
    print("[5/6] Testing Local Embedding Generation & Cosine Similarity...", flush=True)
    embedder = LocalEmbeddingService.get_instance()
    text_a = "Backend engineer with Python, FastAPI, and PostgreSQL experience."
    text_b = "Python backend developer proficient in databases and async APIs."
    text_c = "UI/UX Graphic Designer specializing in Figma and Canva illustration."

    vec_a = embedder.get_embedding(text_a)
    vec_b = embedder.get_embedding(text_b)
    vec_c = embedder.get_embedding(text_c)

    assert len(vec_a) == 384
    assert len(vec_b) == 384
    assert len(vec_c) == 384

    sim_related = LocalEmbeddingService.cosine_similarity(vec_a, vec_b)
    sim_unrelated = LocalEmbeddingService.cosine_similarity(vec_a, vec_c)

    print(f"  --> Cosine similarity (Backend vs Backend): {sim_related:.4f}", flush=True)
    print(f"  --> Cosine similarity (Backend vs Graphic Design): {sim_unrelated:.4f}", flush=True)
    assert sim_related > sim_unrelated, f"Expected {sim_related} > {sim_unrelated}"
    print("  --> Semantic vector embedding passed.", flush=True)

def test_parser_service():
    print("[6/6] Testing Structured Resume Parser Service...", flush=True)
    raw_sample = """
    ALEX MORGAN
    alex.morgan@stanford.edu | (555) 019-2834
    Stanford University, B.S. Computer Science | GPA: 3.88 | Expected: 2026

    SKILLS
    Python, FastAPI, PostgreSQL, Docker, Redis, Git, Linux

    PROJECTS
    Distributed Task Queue
    Architected asynchronous worker pool using Python and Redis.
    """
    parsed = ResumeParserService._parse_heuristically(raw_sample)
    assert parsed.email == "alex.morgan@stanford.edu"
    assert parsed.gpa == 3.88
    assert parsed.graduation_year == 2026
    skill_names = [s.name for s in parsed.skills]
    assert "Python" in skill_names
    assert "FastAPI" in skill_names
    assert "PostgreSQL" in skill_names
    print(f"  --> Parsed profile: {parsed.candidate_name}, GPA={parsed.gpa}, Skills={skill_names[:5]}", flush=True)

if __name__ == "__main__":
    print("=" * 70, flush=True)
    print("RUNNING BACKEND SERVICE & CLEAN ARCHITECTURE VALIDATION SUITE", flush=True)
    print("=" * 70, flush=True)
    test_health_check_service()
    test_security_and_jwt()
    test_pydantic_schemas_validation()
    test_pdf_extraction_service()
    test_dense_embedding_service()
    test_parser_service()
    print("=" * 70, flush=True)
    print("ALL BACKEND ARCHITECTURE TESTS PASSED WITH 100% ASSERTIONS OK!", flush=True)
    print("=" * 70, flush=True)
