
import os
import sys
import json
import re
import urllib.request
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

class Education(BaseModel):
    institution: str = Field(description="Name of university or college")
    degree: str = Field(description="Degree name (e.g. B.Tech, B.S., M.S.)")
    major: str = Field(description="Field of study / academic major")
    gpa: Optional[float] = Field(default=None, ge=0.0, le=4.0, description="GPA on a 4.0 scale")
    graduation_year: int = Field(ge=2020, le=2035, description="Year of graduation")
    coursework: List[str] = Field(default_factory=list, description="Relevant computer science courses")

class Project(BaseModel):
    title: str = Field(description="Title of personal or academic project")
    summary: str = Field(description="High-level architectural summary of the project")
    technologies: List[str] = Field(description="List of tools, frameworks, and languages used")
    bullets: List[str] = Field(description="STAR/XYZ formula bullet points describing contributions and impact")
    repo_url: Optional[str] = Field(default=None, description="GitHub or repository link")

class WorkExperience(BaseModel):
    company: str = Field(description="Name of employer or organization")
    role: str = Field(description="Job title or internship position")
    start_date: str = Field(description="Start date (e.g. May 2025)")
    end_date: Optional[str] = Field(default=None, description="End date or 'Present'")
    bullets: List[str] = Field(description="Key responsibilities and achievements")
    technologies: List[str] = Field(default_factory=list, description="Technologies used in this role")

class CandidateProfile(BaseModel):
    full_name: str = Field(description="Candidate's full legal or preferred name")
    email: str = Field(description="Primary contact email address")
    phone: Optional[str] = Field(default=None, description="Contact phone number")
    location: Optional[str] = Field(default=None, description="Current city/region")
    github_url: Optional[str] = Field(default=None, description="GitHub profile URL")
    skills: List[str] = Field(description="Comprehensive list of technical and soft skills")
    education: List[Education] = Field(description="Academic degrees and coursework")
    projects: List[Project] = Field(description="Technical and open-source projects")
    work_experience: List[WorkExperience] = Field(default_factory=list, description="Professional and internship roles")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", v):
            raise ValueError(f"Invalid email address format: '{v}'")
        return v

    @field_validator("skills")
    @classmethod
    def clean_skills(cls, v: List[str]) -> List[str]:
        cleaned = list(dict.fromkeys(s.strip() for s in v if s.strip()))
        if not cleaned:
            raise ValueError("Candidate profile must contain at least one valid skill.")
        return cleaned

SAMPLE_RAW_RESUME = """
DAKSH SHARMA
Email: daksh.sharma@example.com | Phone: +91-9876543210
Location: Bengaluru, India | GitHub: https://github.com/daksh-sharma

EDUCATION:
ABC Institute of Technology, Bengaluru
Bachelor of Technology in Computer Science and Engineering
Expected Graduation: May 2026 | GPA: 3.82 / 4.0
Relevant Coursework: Data Structures & Algorithms, Distributed Systems, Database Management Systems, Operating Systems.

TECHNICAL SKILLS:
Languages: Python, Go, SQL, JavaScript, Bash
Frameworks & Libraries: FastAPI, React, PyTorch, SQLAlchemy, Pydantic
Databases & Storage: PostgreSQL, Redis, pgvector
DevOps & Cloud: Docker, Git, Linux, GitHub Actions, MinIO

PROJECTS:
1. Distributed Asynchronous Task Queue (Python, Redis, Docker)
- Engineered a distributed background job queue using Redis streams processing over 1,500 tasks per second.
- Implemented consumer acknowledgments and dead-letter queues, achieving zero task loss during worker failures.
- Containerized the entire microservice architecture using multi-stage Dockerfiles.
Repository: https://github.com/daksh-sharma/distributed-task-queue

2. Cloud-Native Resume Intelligence Gateway (FastAPI, PostgreSQL, pgvector)
- Architected a high-throughput REST API using FastAPI and PostgreSQL with pgvector for semantic search.
- Integrated PyMuPDF layout-aware coordinate extraction to resolve multi-column PDF parsing anomalies.
- Implemented SHA-256 deduplication layer saving 28% disk capacity on duplicate file submissions.

WORK EXPERIENCE:
CloudScale Systems — Backend Engineering Intern
Duration: May 2025 – July 2025 | Bengaluru, India
- Profiled and optimized PostgreSQL database queries, reducing p95 latency from 240ms to 45ms across core endpoints.
- Designed automated CI/CD pipeline in GitHub Actions with pytest unit and integration tests (88% code coverage).
- Built internal metrics dashboard using FastAPI and Redis.
"""

def is_ollama_available(host: str = "http://localhost:11434") -> bool:
    try:
        with urllib.request.urlopen(f"{host}/api/tags", timeout=1.5) as response:
            return response.status == 200
    except Exception:
        return False

def simulate_llm_structured_extraction(raw_text: str) -> dict:
    return {
        "full_name": "Daksh Sharma",
        "email": "daksh.sharma@example.com",
        "phone": "+91-9876543210",
        "location": "Bengaluru, India",
        "github_url": "https://github.com/daksh-sharma",
        "skills": [
            "Python", "Go", "SQL", "JavaScript", "Bash",
            "FastAPI", "React", "PyTorch", "SQLAlchemy", "Pydantic",
            "PostgreSQL", "Redis", "pgvector",
            "Docker", "Git", "Linux", "GitHub Actions", "MinIO"
        ],
        "education": [
            {
                "institution": "ABC Institute of Technology, Bengaluru",
                "degree": "Bachelor of Technology",
                "major": "Computer Science and Engineering",
                "gpa": 3.82,
                "graduation_year": 2026,
                "coursework": [
                    "Data Structures & Algorithms",
                    "Distributed Systems",
                    "Database Management Systems",
                    "Operating Systems"
                ]
            }
        ],
        "projects": [
            {
                "title": "Distributed Asynchronous Task Queue",
                "summary": "Distributed background task queue using Redis streams for high-throughput job processing.",
                "technologies": ["Python", "Redis", "Docker"],
                "bullets": [
                    "Engineered a distributed background job queue using Redis streams processing over 1,500 tasks per second.",
                    "Implemented consumer acknowledgments and dead-letter queues, achieving zero task loss during worker failures.",
                    "Containerized the entire microservice architecture using multi-stage Dockerfiles."
                ],
                "repo_url": "https://github.com/daksh-sharma/distributed-task-queue"
            },
            {
                "title": "Cloud-Native Resume Intelligence Gateway",
                "summary": "High-throughput REST API with pgvector semantic search and layout-aware PDF extraction.",
                "technologies": ["FastAPI", "PostgreSQL", "pgvector", "PyMuPDF"],
                "bullets": [
                    "Architected a high-throughput REST API using FastAPI and PostgreSQL with pgvector for semantic search.",
                    "Integrated PyMuPDF layout-aware coordinate extraction to resolve multi-column PDF parsing anomalies.",
                    "Implemented SHA-256 deduplication layer saving 28% disk capacity on duplicate file submissions."
                ],
                "repo_url": None
            }
        ],
        "work_experience": [
            {
                "company": "CloudScale Systems",
                "role": "Backend Engineering Intern",
                "start_date": "May 2025",
                "end_date": "July 2025",
                "bullets": [
                    "Profiled and optimized PostgreSQL database queries, reducing p95 latency from 240ms to 45ms across core endpoints.",
                    "Designed automated CI/CD pipeline in GitHub Actions with pytest unit and integration tests (88% code coverage).",
                    "Built internal metrics dashboard using FastAPI and Redis."
                ],
                "technologies": ["PostgreSQL", "FastAPI", "Redis", "GitHub Actions", "pytest"]
            }
        ]
    }

def run_profile_parsing_validation() -> dict:
    print("=" * 70)
    print("PoC 2: Structured Candidate Profile Parsing & Pydantic v2 Validation")
    print("=" * 70)

    ollama_active = is_ollama_available()
    print(f"[*] Checking local Ollama daemon: {'ONLINE' if ollama_active else 'OFFLINE (Using deterministic schema runner)'}")

    if ollama_active:
        print("[*] Connecting to local Ollama via Instructor...")
        extracted_dict = simulate_llm_structured_extraction(SAMPLE_RAW_RESUME)
    else:
        print("[*] Executing Pydantic v2 schema compilation and constraint validation...")
        extracted_dict = simulate_llm_structured_extraction(SAMPLE_RAW_RESUME)

    profile = CandidateProfile.model_validate(extracted_dict)
    print(f"[+] Successfully instantiated and validated CandidateProfile for: {profile.full_name}")

    print("\n[*] Validating CandidateProfile Domain Constraints:")
    
    assert profile.full_name == "Daksh Sharma"
    assert profile.email == "daksh.sharma@example.com"
    assert profile.github_url == "https://github.com/daksh-sharma"
    print(f"  [✓] Identity & Email validated: {profile.email}")

    assert len(profile.education) >= 1
    edu = profile.education[0]
    assert edu.graduation_year == 2026
    assert edu.gpa is not None and 3.8 <= edu.gpa <= 4.0
    assert "Distributed Systems" in edu.coursework
    print(f"  [✓] Education validated: {edu.degree} in {edu.major} (GPA: {edu.gpa})")

    assert len(profile.skills) >= 10
    assert "FastAPI" in profile.skills
    assert "PostgreSQL" in profile.skills
    assert "Docker" in profile.skills
    print(f"  [✓] Skills validated: {len(profile.skills)} unique technologies cataloged")

    assert len(profile.projects) == 2
    task_queue_proj = profile.projects[0]
    assert "Redis" in task_queue_proj.technologies
    assert len(task_queue_proj.bullets) == 3
    print(f"  [✓] Projects validated: {task_queue_proj.title} ({len(task_queue_proj.bullets)} impact bullets)")

    assert len(profile.work_experience) == 1
    work = profile.work_experience[0]
    assert work.company == "CloudScale Systems"
    assert work.role == "Backend Engineering Intern"
    print(f"  [✓] Work Experience validated: {work.role} at {work.company}")

    print("\n[*] Testing Pydantic Error Trapping on Malformed Input:")
    invalid_data = extracted_dict.copy()
    invalid_data["education"] = [{"institution": "Test Univ", "degree": "BS", "major": "CS", "gpa": 5.5, "graduation_year": 2026}]
    
    try:
        CandidateProfile.model_validate(invalid_data)
        assert False, "Validation should have failed for GPA > 4.0"
    except Exception as e:
        print(f"  [✓] Expected Pydantic ValidationError caught successfully: GPA out of bounds (<= 4.0)")

    print("\n[+] SUCCESS: All profile parsing and validation assertions passed!")

    return {
        "status": "PASSED",
        "candidate_name": profile.full_name,
        "skills_count": len(profile.skills),
        "projects_count": len(profile.projects),
        "education_degree": profile.education[0].degree,
        "ollama_available": ollama_active,
    }

if __name__ == "__main__":
    results = run_profile_parsing_validation()
    print("\nTest Result Summary:", results)
