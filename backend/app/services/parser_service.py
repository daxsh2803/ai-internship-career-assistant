import re
from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel, Field

from app.core.config import settings

class ParsedSkillItem(BaseModel):
    name: str
    category: str = "Technical Skills"
    proficiency: str = "INTERMEDIATE"
    years_experience: float = 1.0

class ParsedEducationItem(BaseModel):
    institution_name: str
    degree: str
    major: str
    graduation_year: int
    graduation_term: str = "Spring"
    gpa: Optional[float] = None
    coursework: List[str] = Field(default_factory=list)

class ParsedProjectItem(BaseModel):
    title: str
    role: str = "Developer"
    summary: str = ""
    bullets: List[str] = Field(default_factory=list)
    technologies_used: List[str] = Field(default_factory=list)
    repo_url: Optional[str] = None

class ParsedWorkExperienceItem(BaseModel):
    company_name: str
    role_title: str
    location: Optional[str] = None
    start_year: int = 2024
    end_year: Optional[int] = None
    bullets: List[str] = Field(default_factory=list)
    technologies_used: List[str] = Field(default_factory=list)

class ParsedResumeOutput(BaseModel):
    candidate_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    university_name: Optional[str] = None
    degree_major: Optional[str] = None
    gpa: Optional[float] = None
    graduation_year: Optional[int] = None
    batch: Optional[str] = None
    graduation_term: str = "Spring"
    requires_sponsorship: bool = False
    skills: List[ParsedSkillItem] = Field(default_factory=list)
    educations: List[ParsedEducationItem] = Field(default_factory=list)
    projects: List[ParsedProjectItem] = Field(default_factory=list)
    work_experiences: List[ParsedWorkExperienceItem] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    categorized_skills: Dict[str, List[str]] = Field(default_factory=dict)

class ResumeParserService:
    @classmethod
    async def parse_resume_text(cls, raw_text: str) -> ParsedResumeOutput:
        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
                if res.status_code == 200:
                    parsed = await cls._parse_with_ollama(raw_text)
                    if parsed:
                        return parsed
        except Exception:
            pass

        return cls._parse_heuristically(raw_text)

    @classmethod
    async def _parse_with_ollama(cls, raw_text: str) -> Optional[ParsedResumeOutput]:
        prompt = f"""Extract the candidate's structured profile from the resume text below.
Return ONLY valid JSON matching this structure:
{{
  "candidate_name": "...",
  "email": "...",
  "university_name": "...",
  "degree_major": "...",
  "gpa": 3.8,
  "graduation_year": 2026,
  "graduation_term": "Spring",
  "requires_sponsorship": false,
  "skills": [{{"name": "Python", "category": "Programming Languages", "proficiency": "ADVANCED", "years_experience": 2.0}}],
  "educations": [{{"institution_name": "...", "degree": "...", "major": "...", "graduation_year": 2026, "graduation_term": "Spring", "gpa": 3.8, "coursework": []}}],
  "projects": [{{"title": "...", "role": "Developer", "summary": "...", "bullets": ["..."], "technologies_used": ["..."], "repo_url": null}}],
  "work_experiences": [{{"company_name": "...", "role_title": "...", "location": "...", "start_year": 2024, "end_year": null, "bullets": ["..."], "technologies_used": ["..."]}}]
}}

RESUME TEXT:
{raw_text[:3500]}
"""
        payload = {
            "model": settings.OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json",
        }
        async with httpx.AsyncClient(timeout=settings.OLLAMA_TIMEOUT_SECONDS) as client:
            resp = await client.post(f"{settings.OLLAMA_BASE_URL}/api/generate", json=payload)
            if resp.status_code == 200:
                data = resp.json().get("response", "{}")
                return ParsedResumeOutput.model_validate_json(data)
        return None

    @classmethod
    def _parse_heuristically(cls, text: str) -> ParsedResumeOutput:
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        from app.services.pdf_service import PDFExtractionService
        section_list = PDFExtractionService.identify_sections(text)
        sections: Dict[str, str] = {s["section_type"]: s["raw_text"] for s in section_list}

        email_match = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", text)
        email = email_match.group(0) if email_match else None

        phone_match = re.search(r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3,5}\)?[-.\s]?\d{3,5}[-.\s]?\d{3,5}", text)
        phone = phone_match.group(0).strip() if phone_match else None

        github_match = re.search(r"(?:https?://)?(?:www\.)?github\.com/([A-Za-z0-9_.-]+)", text, re.I)
        github_url = github_match.group(0) if github_match else None

        linkedin_match = re.search(r"(?:https?://)?(?:www\.)?linkedin\.com/in/([A-Za-z0-9_.-]+)", text, re.I)
        linkedin_url = linkedin_match.group(0) if linkedin_match else None

        candidate_name = None
        for line in lines[:5]:
            cleaned = re.sub(r"(?:https?://\S+|[\w\.-]+@[\w\.-]+\.\w+|\+?\d[\d\s-]{7,}|\||·|•).*", "", line).strip()
            cleaned = re.sub(r"[\(\[].*?[\)\]]", "", cleaned).strip()
            if cleaned and not any(kw in cleaned.upper() for kw in ["RESUME", "CURRICULUM", "CV", "CONTACT", "EMAIL", "PHONE", "PAGE", "HTTP", "WWW", "GITHUB", "LINKEDIN"]):
                words = cleaned.split()
                if 1 <= len(words) <= 4 and all(re.match(r"^[A-Za-z\.'-]+$", w) for w in words):
                    candidate_name = cleaned
                    break

        if not candidate_name:
            if email:
                local_part = email.split("@")[0]
                local_cleaned = re.sub(r"[0-9_\.-]+", " ", local_part).strip().title()
                if local_cleaned:
                    candidate_name = local_cleaned
            if not candidate_name:
                candidate_name = "Candidate"

        edu_text = sections.get("EDUCATION", text)

        uni_name = None
        uni_match = re.search(
            r"([A-Z][A-Za-z0-9\s,\.'-]+\b(?:Institute of Technology|Institute of Information Technology|Institute|University|College|School of Technology|Academy)\b[A-Za-z0-9\s,\.'-]*(?:\s*\([A-Za-z0-9\s]+\))?)",
            edu_text,
        )
        if uni_match:
            uni_name = uni_match.group(1).strip().strip(",-·")
        else:
            acronym_match = re.search(r"\b(IIIT|IIT|NIT|BITS)\s+[A-Za-z]+(?:\s*\([A-Za-z\s]+\))?", edu_text)
            if acronym_match:
                uni_name = acronym_match.group(0).strip()

        degree_name = None
        degree_patterns = [
            r"\bComputer Science and Engineering undergraduate\b",
            r"\bBachelor of Technology in Computer Science and Engineering\b",
            r"\bB\.?Tech(?:\s+(?:in|of)\s+[A-Za-z\s]+)?\b",
            r"\bBachelor(?:'s)?\s*(?:of\s+Technology|of\s+Science|of\s+Engineering)?(?:\s+(?:in|of)\s+[A-Za-z\s]+)?\b",
            r"\bB\.?E\.?(?:\s+(?:in|of)\s+[A-Za-z\s]+)?\b",
            r"\bB\.?S\.?(?:\s+(?:in|of)\s+[A-Za-z\s]+)?\b",
            r"\bBSc(?:\s+(?:in|of)\s+[A-Za-z\s]+)?\b",
            r"\bM\.?Tech(?:\s+(?:in|of)\s+[A-Za-z\s]+)?\b",
            r"\bMaster(?:'s)?(?:\s+(?:in|of)\s+[A-Za-z\s]+)?\b",
            r"\bPh\.?D(?:\s+(?:in|of)\s+[A-Za-z\s]+)?\b",
        ]
        for pattern in degree_patterns:
            deg_match = re.search(pattern, edu_text, re.I)
            if deg_match:
                degree_name = deg_match.group(0).strip()
                break

        gpa = None
        gpa_match = re.search(r"(?:CGPA|GPA|cgpa|gpa)[:\s]*([0-9]\.[0-9]{1,2})", edu_text) or re.search(r"(?:CGPA|GPA|cgpa|gpa)[:\s]*([0-9]\.[0-9]{1,2})", text)
        if gpa_match:
            gpa = float(gpa_match.group(1))
        else:
            slash_match = re.search(r"\b([0-9]\.[0-9]{1,2})\s*/\s*(?:10(?:\.0)?|4(?:\.0)?)", edu_text) or re.search(r"\b([0-9]\.[0-9]{1,2})\s*/\s*(?:10(?:\.0)?|4(?:\.0)?)", text)
            if slash_match:
                gpa = float(slash_match.group(1))

        batch_str = None
        grad_year = None
        batch_match = re.search(r"(?:Batch[:\s]*)?(\b20\d{2}\s*[-–—]\s*(20\d{2})\b)", edu_text) or re.search(r"(?:Batch[:\s]*)?(\b20\d{2}\s*[-–—]\s*(20\d{2})\b)", text)
        if batch_match:
            batch_str = batch_match.group(1).replace(" ", "")
            grad_year = int(batch_match.group(2))
        else:
            year_match = re.search(r"\b(202[4-9]|203[0-5])\b", edu_text) or re.search(r"\b(202[4-9]|203[0-5])\b", text)
            if year_match:
                grad_year = int(year_match.group(1))
                batch_str = f"{grad_year - 4}–{grad_year}"

        coursework: List[str] = []
        cw_match = re.search(r"(?:Coursework|Relevant Courses|Key Coursework)[:\s]*(.+)", edu_text, re.I)
        if cw_match:
            cw_raw = cw_match.group(1).split("\n")[0]
            coursework = [c.strip() for c in re.split(r"[,;•·]", cw_raw) if len(c.strip()) > 1]

        educations = []
        if uni_name or degree_name or gpa or grad_year:
            educations.append(
                ParsedEducationItem(
                    institution_name=uni_name or "Academic Institution",
                    degree=degree_name or "Undergraduate Degree",
                    major="Computer Science and Engineering" if (degree_name and "Computer" in degree_name) else "Engineering",
                    graduation_year=grad_year or 2026,
                    graduation_term="Spring",
                    gpa=gpa,
                    coursework=coursework,
                )
            )

        skills_text = sections.get("SKILLS", "")
        search_skills_text = f"{skills_text}\n\n{text}"

        skill_catalog = [
            ("Java", "Programming"),
            ("Python", "Programming"),
            ("C++", "Programming"),
            ("C#", "Programming"),
            ("SQL", "Programming"),
            ("TypeScript", "Programming"),
            ("JavaScript", "Programming"),
            ("Go", "Programming"),
            ("Rust", "Programming"),
            ("Kotlin", "Programming"),
            ("Swift", "Programming"),
            ("Ruby", "Programming"),
            ("PHP", "Programming"),
            ("Bash", "Programming"),
            ("R", "Programming"),
            ("AWS Cloud", "Cloud"),
            ("AWS", "Cloud"),
            ("Docker", "Cloud"),
            ("Kubernetes", "Cloud"),
            ("Azure", "Cloud"),
            ("GCP", "Cloud"),
            ("Linux", "Developer Tools"),
            ("Git", "Developer Tools"),
            ("GitHub Actions", "Developer Tools"),
            ("CI/CD", "Developer Tools"),
            ("Machine Learning", "AI/ML"),
            ("Deep Learning", "AI/ML"),
            ("LLMs", "AI/ML"),
            ("Retrieval-Augmented Generation / RAG", "AI/ML"),
            ("Retrieval-Augmented Generation (RAG)", "AI/ML"),
            ("RAG", "AI/ML"),
            ("DeepSeek-R1", "AI/ML"),
            ("LangChain", "AI/ML"),
            ("LangGraph", "AI/ML"),
            ("PyTorch", "AI/ML"),
            ("TensorFlow", "AI/ML"),
            ("Ollama", "AI/ML"),
            ("Groq", "AI/ML"),
            ("Streamlit", "AI/ML"),
            ("Hugging Face", "AI/ML"),
            ("NLP", "AI/ML"),
            ("Computer Vision", "AI/ML"),
            ("Data Cleaning", "Analytical"),
            ("Exploratory Data Analysis / EDA", "Analytical"),
            ("Exploratory Data Analysis (EDA)", "Analytical"),
            ("EDA", "Analytical"),
            ("Pandas", "Analytical"),
            ("NumPy", "Analytical"),
            ("Matplotlib", "Analytical"),
            ("Seaborn", "Analytical"),
            ("Scikit-Learn", "Analytical"),
            ("FastAPI", "Frameworks & Backend"),
            ("Flask", "Frameworks & Backend"),
            ("Django", "Frameworks & Backend"),
            ("Next.js 15", "Frameworks & Backend"),
            ("Next.js", "Frameworks & Backend"),
            ("React 19", "Frameworks & Backend"),
            ("React", "Frameworks & Backend"),
            ("Node.js", "Frameworks & Backend"),
            ("PostgreSQL", "Databases"),
            ("pgvector", "Databases"),
            ("Redis", "Databases"),
            ("MongoDB", "Databases"),
            ("SQLite", "Databases"),
            ("PyMuPDF", "Developer Tools"),
        ]

        extracted_skills: List[ParsedSkillItem] = []
        seen_skills = set()

        for skill_name, category in skill_catalog:
            if not skill_name[-1].isalnum():
                pattern = rf"\b{re.escape(skill_name)}(?=[\s,;/\.\)]|$)"
            elif "/" in skill_name or "(" in skill_name:
                pattern = re.escape(skill_name)
            else:
                pattern = rf"\b{re.escape(skill_name)}\b"

            if re.search(pattern, search_skills_text, re.IGNORECASE):
                if skill_name not in seen_skills:
                    seen_skills.add(skill_name)
                    extracted_skills.append(
                        ParsedSkillItem(
                            name=skill_name,
                            category=category,
                            proficiency="ADVANCED" if category in ["Programming", "AI/ML"] else "INTERMEDIATE",
                            years_experience=2.0 if category == "Programming" else 1.0,
                        )
                    )

        prog_skills = [s.name for s in extracted_skills if s.category == "Programming"]
        cloud_skills = [s.name for s in extracted_skills if s.category in ["Cloud", "Developer Tools"]]
        aiml_skills = [s.name for s in extracted_skills if s.category == "AI/ML"]
        anal_skills = [s.name for s in extracted_skills if s.category == "Analytical"]
        fw_skills = [s.name for s in extracted_skills if s.category == "Frameworks & Backend"]
        db_skills = [s.name for s in extracted_skills if s.category == "Databases"]

        categorized_dict = {
            "programming": prog_skills,
            "cloud": [s for s in cloud_skills if s in ["AWS Cloud", "AWS", "Docker", "Kubernetes", "Azure", "GCP"]],
            "ai_ml": aiml_skills,
            "analytical": anal_skills,
            "languages": prog_skills,
            "frameworks_and_libraries": fw_skills or aiml_skills,
            "tools_and_devops": cloud_skills,
            "databases_and_vector_stores": db_skills or anal_skills,
        }

        projects: List[ParsedProjectItem] = []
        proj_text = sections.get("PROJECTS", "")
        if proj_text:
            proj_lines = [l.strip() for l in proj_text.splitlines() if l.strip()]
            current_proj: Optional[ParsedProjectItem] = None

            for line in proj_lines:
                clean_line = line.strip("#*-•· ")
                is_bullet = line.startswith(("-", "*", "•", "–")) or (line.startswith(" ") and len(line) > 10)
                is_header_candidate = not is_bullet and (
                    re.match(r"^\d+[\.\)]", line)
                    or "(" in line
                    or "|" in line
                    or len(clean_line.split()) <= 7
                )

                if is_header_candidate and not line.lower().startswith(("tech", "repository", "github", "url", "demo", "duration", "link")):
                    if current_proj and current_proj.title:
                        projects.append(current_proj)

                    title_part = clean_line
                    tech_in_title: List[str] = []
                    paren_match = re.search(r"\(([^)]+)\)", clean_line)
                    if paren_match:
                        tech_in_title = [t.strip() for t in re.split(r"[,;]", paren_match.group(1)) if t.strip()]
                        title_part = clean_line[:paren_match.start()].strip().strip("-:| ")

                    pipe_match = re.search(r"\|", clean_line)
                    if pipe_match and not tech_in_title:
                        parts = clean_line.split("|")
                        title_part = parts[0].strip()
                        tech_in_title = [t.strip() for t in re.split(r"[,;]", parts[1]) if t.strip()]

                    current_proj = ParsedProjectItem(
                        title=title_part,
                        role="Developer",
                        summary="",
                        bullets=[],
                        technologies_used=tech_in_title,
                    )
                elif current_proj:
                    if is_bullet:
                        current_proj.bullets.append(clean_line)
                    elif clean_line.lower().startswith(("tech:", "technologies:", "tools:")):
                        tech_line = re.sub(r"^(?:tech|technologies|tools)[:\s]*", "", clean_line, flags=re.I)
                        techs = [t.strip() for t in re.split(r"[,;]", tech_line) if t.strip()]
                        current_proj.technologies_used.extend(techs)
                    elif clean_line.lower().startswith(("repository:", "github:", "repo:")):
                        current_proj.repo_url = re.sub(r"^(?:repository|github|repo)[:\s]*", "", clean_line, flags=re.I).strip()
                    elif not current_proj.summary and len(clean_line) > 15:
                        current_proj.summary = clean_line
                        current_proj.bullets.append(clean_line)

            if current_proj and current_proj.title:
                projects.append(current_proj)

        cert_text = sections.get("CERTIFICATIONS", "") or sections.get("AWARDS", "")
        certifications: List[str] = []
        if cert_text:
            for line in cert_text.splitlines():
                cl = line.strip("#*-•· ")
                if cl and len(cl) > 5 and not any(kw == cl.upper() for kw in ["CERTIFICATIONS", "AWARDS", "ACHIEVEMENTS"]):
                    certifications.append(cl)
        else:
            for line in lines:
                if any(kw in line.lower() for kw in ["certified", "certificate", "bootcamp", "specialization"]):
                    cl = line.strip("#*-•· ")
                    if cl and len(cl) > 10 and not any(h in cl.upper() for h in ["EDUCATION", "EXPERIENCE", "PROJECTS"]):
                        certifications.append(cl)

        exp_text = sections.get("EXPERIENCE", "")
        work_experiences: List[ParsedWorkExperienceItem] = []
        if exp_text:
            exp_lines = [l.strip() for l in exp_text.splitlines() if l.strip()]
            current_work: Optional[ParsedWorkExperienceItem] = None

            for line in exp_lines:
                cl = line.strip("#*-•· ")
                is_bullet = line.startswith(("-", "*", "•", "–"))

                if not is_bullet and ("—" in line or "-" in line or "|" in line or len(cl.split()) <= 6):
                    if current_work and current_work.company_name:
                        work_experiences.append(current_work)
                    parts = re.split(r"[—\-\|]", cl)
                    comp = parts[0].strip() if len(parts) > 0 else cl
                    role = parts[1].strip() if len(parts) > 1 else "Engineering Intern"
                    current_work = ParsedWorkExperienceItem(
                        company_name=comp,
                        role_title=role,
                        bullets=[],
                        technologies_used=[],
                    )
                elif current_work and is_bullet:
                    current_work.bullets.append(cl)

            if current_work and current_work.company_name:
                work_experiences.append(current_work)

        return ParsedResumeOutput(
            candidate_name=candidate_name,
            email=email,
            phone=phone,
            github_url=github_url,
            linkedin_url=linkedin_url,
            university_name=uni_name,
            degree_major=degree_name,
            gpa=gpa,
            graduation_year=grad_year,
            batch=batch_str,
            graduation_term="Spring",
            requires_sponsorship=False,
            skills=extracted_skills,
            educations=educations,
            projects=projects,
            work_experiences=work_experiences,
            certifications=certifications,
            categorized_skills=categorized_dict,
        )
