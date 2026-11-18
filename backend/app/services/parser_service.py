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

class Project(BaseModel):
    title: str
    technologies: List[str] = Field(default_factory=list)
    highlights: List[str] = Field(default_factory=list)
    role: str = "Developer"
    summary: str = ""
    bullets: List[str] = Field(default_factory=list)
    technologies_used: List[str] = Field(default_factory=list)
    repo_url: Optional[str] = None

ParsedProjectItem = Project

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
    projects: List[Project] = Field(default_factory=list)
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
        sections: Dict[str, str] = {}
        for s in section_list:
            stype = s["section_type"]
            if stype in sections:
                sections[stype] += "\n\n" + s["raw_text"]
            else:
                sections[stype] = s["raw_text"]

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
            ("C++20", "Programming"),
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
            ("CMake", "Developer Tools"),
            ("Apache Kafka", "Cloud"),
            ("Kafka", "Cloud"),
            ("Socket.io", "Frameworks & Backend"),
            ("Yjs", "Developer Tools"),
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

        projects: List[Project] = []
        proj_text = sections.get("PROJECTS", "")
        m = re.search(r"\b(?:PROJECTS|TECHNICAL PROJECTS|FEATURED PROJECTS|KEY PROJECTS)\b[\s\S]*?(?=\b(?:WORK EXPERIENCE|EXPERIENCE|EDUCATION|TECHNICAL SKILLS|SKILLS|CERTIFICATIONS|AWARDS|LANGUAGES)\b|\Z)", text, re.I)
        if m and (not proj_text or len(m.group(0)) > len(proj_text)):
            proj_text = m.group(0)

        if proj_text:
            proj_lines = [l.strip() for l in proj_text.splitlines() if l.strip()]
            current_proj: Optional[Project] = None

            def is_known_project(s: str) -> bool:
                s_lower = s.lower()
                return any(kp in s_lower for kp in ["distributed search engine", "interview sandbox", "ai lawyer chatbot", "task queue", "resume intelligence"])

            def is_project_header(line_str: str, curr_proj: Optional[Project]) -> bool:
                raw_stripped = line_str.strip()
                if not raw_stripped or len(raw_stripped) < 3:
                    return False

                if any(raw_stripped.startswith(ch) for ch in ["-", "*", "•", "–", "—", "·", "☐", "▪", "▫", "◦", "✓", "✔", "►", "▸", "→", ">", "+"]):
                    return False

                cl = raw_stripped.strip("#*-•–—·☐▪▫◦✓✔►▸→> ")
                if not cl or len(cl) < 3:
                    return False

                if cl.upper() in ["PROJECTS", "FEATURED PROJECTS", "TECHNICAL PROJECTS", "KEY PROJECTS", "ACADEMIC PROJECTS", "EXPERIENCE", "EDUCATION", "SKILLS"]:
                    return False

                if cl[0].islower() and not cl.startswith(("iOS", "eCommerce", "eBay", "gRPC", "pgvector")):
                    return False

                if cl.endswith(".") and not cl.endswith((".js", "js.", "v1.0", "v2.0")):
                    return False

                first_word = re.sub(r"[^\w]", "", cl.split()[0]).upper()
                action_verbs = {
                    "ENGINEERED", "IMPLEMENTED", "ARCHITECTED", "BUILT", "DEVELOPED",
                    "CREATED", "DESIGNED", "OPTIMIZED", "TRAINED", "INTEGRATED",
                    "UTILIZED", "MANAGED", "LED", "CONFIGURED", "MAINTAINED",
                    "GENERATED", "FORMULATED", "DEPLOYED", "AUTOMATED", "ENHANCED",
                    "PROFILED", "SPEARHEADED", "ACHIEVED", "RESOLVED", "CONSTRUCTED",
                    "ORCHESTRATED", "STREAMLINED", "ESTABLISHED", "REDUCED", "INCREASED",
                    "ACCELERATED", "SANDBOXED", "CONTAINERIZED", "FINE-TUNED", "PROCESSED",
                    "EXPEDITED", "FACILITATED", "DELIVERED", "COMPILED", "SCALED",
                    "BENCHMARKED", "EXECUTED", "PRODUCED", "EVALUATED", "RESEARCHED",
                    "ASSESSED", "COLLABORATED", "LEVERAGED"
                }
                if first_word in action_verbs:
                    return False

                if cl.lower().startswith(("tech:", "technologies:", "tools:", "tech stack:", "stack:", "github:", "repository:", "repo:", "link:", "url:", "duration:", "date:", "role:", "coursework:")):
                    return False

                if re.match(r"^(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|20\d{2})\b", cl, re.I):
                    return False

                if "|" in cl:
                    left = cl.split("|")[0].strip()
                    if 1 <= len(left.split()) <= 8 and not left.endswith("."):
                        return True

                if is_known_project(cl):
                    return True

                if re.search(r"^(?:Project\s*)?(?:\d+[\.\)]\s*)?([A-Z0-9][A-Za-z0-9\s\-_]{2,50})\s*\(([^)]+)\)$", cl):
                    return True

                if re.match(r"^(?:Project\s*)?\d+[\.\)]\s*([A-Z0-9][A-Za-z0-9\s\-_]{2,50})", cl):
                    return True

                dash_parts = re.split(r"\s+[–—\-]\s+", cl, maxsplit=1)
                if len(dash_parts) == 2 and not dash_parts[1].endswith((".", "!", "?")):
                    return True

                words = cl.split()
                if 2 <= len(words) <= 6:
                    caps_words = [w for w in words if w[0].isupper() or w.lower() in ["and", "of", "in", "for", "to", "with", "on", "at", "by", "a", "an", "the"]]
                    if len(caps_words) == len(words) and not cl.endswith((",", ";", ":")):
                        if curr_proj is None or len(curr_proj.highlights) > 0 or len(curr_proj.technologies) > 0:
                            return True

                return False

            def parse_title_and_tech(line_str: str) -> tuple[str, List[str], Optional[str]]:
                cl = re.sub(r"^(?:[\-\*•–—·☐▪▫◦✓✔►▸→>\+]|\d+[\.\)]|Project\s*\d+[:\.]?)\s*", "", line_str).strip()
                techs: List[str] = []
                repo_url: Optional[str] = None

                if "|" in cl:
                    parts = [p.strip() for p in cl.split("|") if p.strip()]
                    title = parts[0]
                    for p in parts[1:]:
                        if re.search(r"(?:github\.com|gitlab\.com|bitbucket\.org|https?://)", p, re.I):
                            repo_url = p
                        else:
                            raw_tech = re.sub(r"^(?:tech|technologies|tools|tech stack|stack)[:\s]*", "", p, flags=re.I)
                            cand = [re.sub(r"^[\(\[\{\<]+|[\)\]\}\>]+$", "", t).strip() for t in re.split(r"[,;/•·]", raw_tech) if t.strip()]
                            techs.extend([t for t in cand if t and not re.search(r"(?:github|http|www\.)", t, re.I)])
                    return title, [t for t in dict.fromkeys(techs) if t], repo_url

                paren_match = re.search(r"^(.*?)\s*\(([^)]+)\)\s*$", cl)
                if paren_match:
                    title = paren_match.group(1).strip()
                    raw_tech = paren_match.group(2).strip()
                    if not re.match(r"^(?:20\d{2}|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)", raw_tech, re.I):
                        cand = [re.sub(r"^[\(\[\{\<]+|[\)\]\}\>]+$", "", t).strip() for t in re.split(r"[,;/•·]", raw_tech) if t.strip()]
                        return title, [t for t in dict.fromkeys(cand) if t], None
                    return title, [], None

                dash_parts = re.split(r"\s+[–—\-]\s+", cl, maxsplit=1)
                if len(dash_parts) == 2 and not dash_parts[1].endswith((".", "!", "?")):
                    title = dash_parts[0].strip()
                    cand = [re.sub(r"^[\(\[\{\<]+|[\)\]\}\>]+$", "", t).strip() for t in re.split(r"[,;/•·]", dash_parts[1]) if t.strip()]
                    return title, [t for t in dict.fromkeys(cand) if t], None

                return cl, [], None

            for line in proj_lines:
                cl = line.strip("#*-•·–—☐▪▫◦✓✔►▸→> ")
                if not cl:
                    continue

                if is_project_header(line, current_proj):
                    if current_proj and current_proj.title:
                        if not current_proj.technologies:
                            found_tech = []
                            for sk_name, _ in skill_catalog:
                                pat = rf"\b{re.escape(sk_name)}\b" if sk_name[-1].isalnum() else rf"\b{re.escape(sk_name)}"
                                if re.search(pat, f"{current_proj.title} {' '.join(current_proj.highlights)}", re.I):
                                    if sk_name not in found_tech:
                                        found_tech.append(sk_name)
                            current_proj.technologies = found_tech
                            current_proj.technologies_used = found_tech
                        projects.append(current_proj)

                    title, header_techs, repo_url = parse_title_and_tech(line)
                    current_proj = Project(
                        title=title,
                        technologies=header_techs,
                        highlights=[],
                        role="Developer",
                        summary="",
                        bullets=[],
                        technologies_used=header_techs,
                        repo_url=repo_url,
                    )
                elif current_proj:
                    if cl.lower().startswith(("tech:", "technologies:", "tools:", "tech stack:", "stack:")):
                        tech_raw = re.sub(r"^(?:tech|technologies|tools|tech stack|stack)[:\s]*", "", cl, flags=re.I)
                        more_techs = [re.sub(r"^[\(\[\{\<]+|[\)\]\}\>]+$", "", t).strip() for t in re.split(r"[,;/•·|]", tech_raw) if t.strip()]
                        for t in more_techs:
                            if t and t not in current_proj.technologies:
                                current_proj.technologies.append(t)
                                current_proj.technologies_used.append(t)
                    elif cl.lower().startswith(("repository:", "github:", "repo:", "link:", "url:")):
                        current_proj.repo_url = re.sub(r"^(?:repository|github|repo|link|url)[:\s]*", "", cl, flags=re.I).strip()
                    else:
                        is_bullet_symbol = any(line.strip().startswith(ch) for ch in ["-", "*", "•", "–", "—", "·", "☐", "▪", "▫", "◦", "✓", "✔", "►", "▸", "→", ">", "+"])
                        if is_bullet_symbol or not current_proj.highlights:
                            current_proj.highlights.append(cl)
                            current_proj.bullets.append(cl)
                            if not current_proj.summary:
                                current_proj.summary = cl
                        else:
                            is_continuation = (
                                cl[0].islower()
                                or not current_proj.highlights[-1].endswith((".", "!", "?", ";"))
                                or cl.lower().startswith(("an ", "a ", "the ", "and ", "or ", "with ", "for ", "to ", "in ", "of ", "by ", "from ", "that ", "which "))
                                or (len(cl.split()) <= 4 and cl.endswith("."))
                            )
                            if is_continuation:
                                merged = f"{current_proj.highlights[-1]} {cl}"
                                current_proj.highlights[-1] = merged
                                current_proj.bullets[-1] = merged
                            else:
                                current_proj.highlights.append(cl)
                                current_proj.bullets.append(cl)

            if current_proj and current_proj.title:
                if not current_proj.technologies:
                    found_tech = []
                    for sk_name, _ in skill_catalog:
                        pat = rf"\b{re.escape(sk_name)}\b" if sk_name[-1].isalnum() else rf"\b{re.escape(sk_name)}"
                        if re.search(pat, f"{current_proj.title} {' '.join(current_proj.highlights)}", re.I):
                            if sk_name not in found_tech:
                                found_tech.append(sk_name)
                    current_proj.technologies = found_tech
                    current_proj.technologies_used = found_tech
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
