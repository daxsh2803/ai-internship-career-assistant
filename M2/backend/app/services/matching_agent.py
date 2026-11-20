import math
import re
from typing import Any, Dict, List, Optional, Set, Tuple
import httpx

from app.core.config import settings
from app.schemas.job import StandardJobPosting
from app.schemas.matching import (
    CandidateProfile,
    JobMatchResult,
    MatchRequest,
    MatchResponse,
    ScoreBreakdown,
)
from app.services.dataset_loader import DatasetLoaderService
from app.services.embedding_service import LocalEmbeddingService
from app.services.retrieval_service import HybridRetrievalService

SYNONYM_MAP: Dict[str, Set[str]] = {
    "python": {"python", "python3", "py"},
    "c++": {"c++", "cpp", "c++17", "c++20", "cplusplus"},
    "c": {"c", "c-lang"},
    "javascript": {"javascript", "js", "ecmascript"},
    "typescript": {"typescript", "ts"},
    "react": {"react", "react.js", "reactjs"},
    "next.js": {"next.js", "nextjs", "next"},
    "node.js": {"node.js", "nodejs", "node"},
    "fastapi": {"fastapi", "fast-api"},
    "docker": {"docker", "containerization", "containers"},
    "kubernetes": {"kubernetes", "k8s"},
    "postgresql": {"postgresql", "postgres", "psql"},
    "mysql": {"mysql"},
    "mongodb": {"mongodb", "mongo"},
    "redis": {"redis"},
    "kafka": {"kafka", "apache kafka"},
    "aws": {"aws", "amazon web services"},
    "gcp": {"gcp", "google cloud", "google cloud platform"},
    "azure": {"azure", "microsoft azure"},
    "git": {"git", "github", "gitlab"},
    "linux": {"linux", "unix", "ubuntu"},
    "bash": {"bash", "shell", "shell scripting"},
    "langchain": {"langchain", "lang-chain"},
    "pytorch": {"pytorch", "torch"},
    "tensorflow": {"tensorflow", "tf"},
    "sql": {"sql", "relational database", "postgresql", "mysql"},
    "rest": {"rest", "restful", "rest api", "restful apis"},
    "graphql": {"graphql"},
    "ci/cd": {"ci/cd", "cicd", "continuous integration", "github actions"},
    "spark": {"spark", "apache spark", "pyspark"},
}

class JobResumeMatchingAgent:
    _instance: Optional["JobResumeMatchingAgent"] = None

    def __init__(self, data_file: Optional[str] = None):
        self.retrieval_service = HybridRetrievalService.get_instance(data_file)
        self.dataset_loader = DatasetLoaderService.get_instance(data_file)
        self.embedding_service = LocalEmbeddingService.get_instance()
        self.all_jobs: Dict[str, StandardJobPosting] = {
            j.id: j for j in self.dataset_loader.get_all_postings()
        }

    @classmethod
    def get_instance(cls, data_file: Optional[str] = None) -> "JobResumeMatchingAgent":
        if cls._instance is None:
            cls._instance = cls(data_file)
        return cls._instance

    @staticmethod
    def _normalize_token(text: str) -> str:
        cleaned = re.sub(r"[^\w\+\#\.]+", " ", text.lower()).strip()
        return cleaned

    def _extract_all_candidate_skills(self, candidate: CandidateProfile) -> List[str]:
        skill_set: List[str] = []
        seen: Set[str] = set()

        for s in candidate.skills:
            name = ""
            if isinstance(s, str):
                name = s.strip()
            elif isinstance(s, dict):
                name = s.get("name") or s.get("skill") or ""
            elif hasattr(s, "name"):
                name = getattr(s, "name", "")

            if name and name.lower() not in seen:
                seen.add(name.lower())
                skill_set.append(name)

        for proj in candidate.projects:
            techs = []
            if isinstance(proj, dict):
                techs = proj.get("technologies") or proj.get("technologies_used") or []
            elif hasattr(proj, "technologies"):
                techs = getattr(proj, "technologies", [])
            elif hasattr(proj, "technologies_used"):
                techs = getattr(proj, "technologies_used", [])

            for t in techs:
                t_str = str(t).strip()
                if t_str and t_str.lower() not in seen:
                    seen.add(t_str.lower())
                    skill_set.append(t_str)

        for we in candidate.work_experiences:
            techs = []
            if isinstance(we, dict):
                techs = we.get("technologies_used") or []
            elif hasattr(we, "technologies_used"):
                techs = getattr(we, "technologies_used", [])

            for t in techs:
                t_str = str(t).strip()
                if t_str and t_str.lower() not in seen:
                    seen.add(t_str.lower())
                    skill_set.append(t_str)

        return skill_set

    def _match_skill(self, candidate_skills_norm: Set[str], target_skill: str) -> bool:
        norm_target = self._normalize_token(target_skill)
        if norm_target in candidate_skills_norm:
            return True

        target_synonyms = SYNONYM_MAP.get(norm_target, {norm_target})
        if any(syn in candidate_skills_norm for syn in target_synonyms):
            return True

        for c_skill in candidate_skills_norm:
            if c_skill in target_synonyms:
                return True
            if len(norm_target) > 3 and norm_target in c_skill:
                return True
            if len(c_skill) > 3 and c_skill in norm_target:
                return True

        return False

    def _build_search_query(self, candidate: CandidateProfile, skills: List[str]) -> str:
        major = candidate.degree_major or "Computer Science Engineering"
        uni = candidate.university_name or ""
        top_skills = ", ".join(skills[:10])

        proj_titles = []
        for p in candidate.projects[:3]:
            if isinstance(p, dict):
                proj_titles.append(p.get("title", ""))
            elif hasattr(p, "title"):
                proj_titles.append(getattr(p, "title", ""))
        proj_str = ", ".join([t for t in proj_titles if t])

        query_parts = [major, uni, f"Skills: {top_skills}"]
        if proj_str:
            query_parts.append(f"Projects: {proj_str}")
        if candidate.summary:
            query_parts.append(candidate.summary)

        return " ".join(query_parts)

    def match_jobs(self, request: MatchRequest) -> MatchResponse:
        candidate = request.candidate_profile
        candidate_skills = self._extract_all_candidate_skills(candidate)
        candidate_skills_norm: Set[str] = {self._normalize_token(s) for s in candidate_skills}

        search_query = self._build_search_query(candidate, candidate_skills)
        retrieval_limit = min(150, max(40, request.top_k * 4))

        search_response = self.retrieval_service.search(
            query=search_query,
            domain=request.domain,
            is_remote=request.is_remote,
            top_k=retrieval_limit,
            use_reranker=True,
        )

        candidate_jobs_dict: Dict[str, Tuple[StandardJobPosting, float]] = {}
        for item in search_response.results:
            candidate_jobs_dict[item.job.id] = (item.job, item.relevance_score)

        if len(candidate_jobs_dict) < request.top_k:
            for jid, job in self.all_jobs.items():
                if jid in candidate_jobs_dict:
                    continue
                if request.domain and request.domain.lower() not in job.domain.lower():
                    continue
                if request.is_remote is not None and job.is_remote != request.is_remote:
                    continue
                candidate_jobs_dict[jid] = (job, 0.45)

        evaluated_results: List[JobMatchResult] = []

        for jid, (job, semantic_score) in candidate_jobs_dict.items():
            matched_req = [s for s in job.required_skills if self._match_skill(candidate_skills_norm, s)]
            missing_req = [s for s in job.required_skills if s not in matched_req]
            req_score = (len(matched_req) / max(1, len(job.required_skills))) * 100.0

            matched_pref = [s for s in job.preferred_skills if self._match_skill(candidate_skills_norm, s)]
            missing_pref = [s for s in job.preferred_skills if s not in matched_pref]
            pref_score = (len(matched_pref) / max(1, len(job.preferred_skills))) * 100.0 if job.preferred_skills else 100.0

            proj_score = self._compute_project_score(candidate, job)
            edu_score = self._compute_education_score(candidate, job)
            sem_score = min(100.0, max(0.0, semantic_score * 100.0))

            overall_score = (
                0.35 * req_score
                + 0.25 * sem_score
                + 0.20 * proj_score
                + 0.10 * pref_score
                + 0.10 * edu_score
            )
            overall_score = round(min(100.0, max(0.0, overall_score)), 2)

            tier = self._determine_tier(overall_score)
            reasoning = self._generate_grounded_reasoning(
                candidate=candidate,
                job=job,
                matched_req=matched_req,
                missing_req=missing_req,
                matched_pref=matched_pref,
                missing_pref=missing_pref,
                use_llm=request.use_llm_reasoning,
            )

            breakdown = ScoreBreakdown(
                required_skills_score=round(req_score, 2),
                preferred_skills_score=round(pref_score, 2),
                projects_experience_score=round(proj_score, 2),
                education_qualifications_score=round(edu_score, 2),
                semantic_relevance_score=round(sem_score, 2),
            )

            all_matched = list(dict.fromkeys(matched_req + matched_pref))

            evaluated_results.append(
                JobMatchResult(
                    job=job,
                    overall_match_score=overall_score,
                    score_breakdown=breakdown,
                    matched_skills=all_matched,
                    missing_required_skills=missing_req,
                    missing_preferred_skills=missing_pref,
                    reasoning=reasoning,
                    recommendation_tier=tier,
                )
            )

        evaluated_results.sort(key=lambda x: x.overall_match_score, reverse=True)
        top_results = evaluated_results[: request.top_k]

        return MatchResponse(
            candidate_name=candidate.candidate_name,
            candidate_skills=candidate_skills,
            total_evaluated_jobs=len(candidate_jobs_dict),
            results=top_results,
        )

    def _compute_project_score(self, candidate: CandidateProfile, job: StandardJobPosting) -> float:
        if not candidate.projects and not candidate.work_experiences:
            return 40.0

        target_skills_norm = {self._normalize_token(s) for s in job.required_skills + job.preferred_skills}
        applied_skills: Set[str] = set()

        for p in candidate.projects:
            techs = []
            if isinstance(p, dict):
                techs = p.get("technologies") or p.get("technologies_used") or []
            elif hasattr(p, "technologies"):
                techs = getattr(p, "technologies", [])
            elif hasattr(p, "technologies_used"):
                techs = getattr(p, "technologies_used", [])

            for t in techs:
                t_norm = self._normalize_token(str(t))
                if t_norm in target_skills_norm:
                    applied_skills.add(t_norm)

        for we in candidate.work_experiences:
            techs = []
            if isinstance(we, dict):
                techs = we.get("technologies_used") or []
            elif hasattr(we, "technologies_used"):
                techs = getattr(we, "technologies_used", [])

            for t in techs:
                t_norm = self._normalize_token(str(t))
                if t_norm in target_skills_norm:
                    applied_skills.add(t_norm)

        ratio = len(applied_skills) / max(1, len(job.required_skills))
        base_score = 50.0 + min(50.0, ratio * 50.0)
        return min(100.0, base_score)

    @staticmethod
    def _compute_education_score(candidate: CandidateProfile, job: StandardJobPosting) -> float:
        major = (candidate.degree_major or "").lower()
        edu_req = job.education_requirements.lower()

        is_cs_related = any(kw in major for kw in ["computer", "software", "information", "data", "engineering", "b.tech", "b.e."])
        score = 80.0 if is_cs_related else 65.0

        if any(kw in edu_req for kw in ["bachelor", "master", "degree"]):
            score += 10.0

        if candidate.gpa is not None:
            if candidate.gpa >= 3.5:
                score += 10.0
            elif candidate.gpa >= 3.0:
                score += 5.0
        else:
            score += 5.0

        return min(100.0, score)

    @staticmethod
    def _determine_tier(score: float) -> str:
        if score >= 80.0:
            return "Strong Match"
        if score >= 65.0:
            return "Good Match"
        if score >= 50.0:
            return "Partial Match"
        return "Stretch Role"

    def _generate_grounded_reasoning(
        self,
        candidate: CandidateProfile,
        job: StandardJobPosting,
        matched_req: List[str],
        missing_req: List[str],
        matched_pref: List[str],
        missing_pref: List[str],
        use_llm: bool = False,
    ) -> str:
        if use_llm:
            llm_text = self._try_ollama_reasoning(candidate, job, matched_req, missing_req)
            if llm_text:
                return llm_text

        parts: List[str] = []

        if matched_req:
            parts.append(
                f"Candidate satisfies core technical requirements: {', '.join(matched_req)}."
            )
        else:
            parts.append("Candidate does not currently match direct required skill keywords.")

        relevant_projects: List[str] = []
        for p in candidate.projects:
            title = p.get("title", "") if isinstance(p, dict) else getattr(p, "title", "")
            techs = p.get("technologies", []) if isinstance(p, dict) else getattr(p, "technologies", [])
            overlap = [t for t in techs if any(self._match_skill({self._normalize_token(str(t))}, req) for req in job.required_skills)]
            if overlap and title:
                relevant_projects.append(f"'{title}' ({', '.join(overlap)})")

        if relevant_projects:
            parts.append(
                f"Practical project evidence demonstrated in {', '.join(relevant_projects[:2])}."
            )

        if matched_pref:
            parts.append(f"Bonus alignment on preferred tools: {', '.join(matched_pref)}.")

        if missing_req:
            parts.append(
                f"Identified technical gaps in required skills: {', '.join(missing_req)}."
            )
        elif missing_pref:
            parts.append(
                f"To strengthen application, consider acquiring preferred skills: {', '.join(missing_pref[:3])}."
            )
        else:
            parts.append("Complete skill coverage across all listed job qualifications.")

        return " ".join(parts)

    @staticmethod
    def _try_ollama_reasoning(
        candidate: CandidateProfile,
        job: StandardJobPosting,
        matched_req: List[str],
        missing_req: List[str],
    ) -> Optional[str]:
        try:
            prompt = (
                f"Summarize in 2 concise sentences why candidate {candidate.candidate_name} matches {job.job_title} at {job.company}. "
                f"Matched skills: {', '.join(matched_req)}. Missing skills: {', '.join(missing_req)}. "
                f"Do not hallucinate facts."
            )
            payload = {
                "model": settings.OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
            }
            with httpx.Client(timeout=2.0) as client:
                res = client.post(f"{settings.OLLAMA_BASE_URL}/api/generate", json=payload)
                if res.status_code == 200:
                    text = res.json().get("response", "").strip()
                    if text:
                        return text
        except Exception:
            pass
        return None
