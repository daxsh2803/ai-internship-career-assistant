from typing import Any, Dict, List, Union
from pydantic import BaseModel, Field

from app.schemas.job import StandardJobPosting

class JobChunk(BaseModel):
    chunk_id: str = Field(...)
    job_id: str = Field(...)
    chunk_type: str = Field(...)
    content: str = Field(...)
    metadata: Dict[str, Union[str, int, float, bool]] = Field(default_factory=dict)

class ChunkingService:
    @staticmethod
    def chunk_job(job: StandardJobPosting) -> List[JobChunk]:
        chunks: List[JobChunk] = []
        work_mode_str = job.work_mode.value if hasattr(job.work_mode, "value") else str(job.work_mode)
        remote_str = "Yes" if job.is_remote else "No"
        skills_str = ", ".join(job.required_skills) if job.required_skills else ""
        stipend_str = str(job.stipend) if job.stipend else "Not specified"

        overview_text = (
            f"Title: {job.job_title}\n"
            f"Company: {job.company}\n"
            f"Domain: {job.domain}\n"
            f"Location: {job.location} ({work_mode_str})\n"
            f"Remote Available: {remote_str}\n"
            f"Overview: {job.job_description}"
        )
        chunks.append(
            JobChunk(
                chunk_id=f"{job.id}#overview",
                job_id=job.id,
                chunk_type="overview",
                content=overview_text,
                metadata={
                    "job_id": job.id,
                    "chunk_id": f"{job.id}#overview",
                    "chunk_type": "overview",
                    "job_title": job.job_title,
                    "company": job.company,
                    "domain": job.domain,
                    "location": job.location,
                    "work_mode": work_mode_str,
                    "is_remote": bool(job.is_remote),
                    "required_skills": skills_str,
                    "stipend": stipend_str,
                },
            )
        )

        resp_items = [f"- {r}" for r in job.responsibilities] if job.responsibilities else ["- General engineering duties"]
        resp_text = (
            f"Job: {job.job_title} at {job.company}\n"
            f"Domain: {job.domain}\n"
            f"Key Responsibilities:\n"
            + "\n".join(resp_items)
        )
        chunks.append(
            JobChunk(
                chunk_id=f"{job.id}#responsibilities",
                job_id=job.id,
                chunk_type="responsibilities",
                content=resp_text,
                metadata={
                    "job_id": job.id,
                    "chunk_id": f"{job.id}#responsibilities",
                    "chunk_type": "responsibilities",
                    "job_title": job.job_title,
                    "company": job.company,
                    "domain": job.domain,
                    "location": job.location,
                    "work_mode": work_mode_str,
                    "is_remote": bool(job.is_remote),
                    "required_skills": skills_str,
                    "stipend": stipend_str,
                },
            )
        )

        qual_items = [f"- {q}" for q in job.qualifications] if job.qualifications else ["- Technical degree or relevant experience"]
        exp_req = str(job.experience_requirements) if job.experience_requirements else "Entry-level / Internship"
        req_text = (
            f"Job: {job.job_title} at {job.company}\n"
            f"Domain: {job.domain}\n"
            f"Required Skills: {skills_str}\n"
            f"Minimum Qualifications:\n"
            + "\n".join(qual_items)
            + f"\nExperience Requirements: {exp_req}"
        )
        chunks.append(
            JobChunk(
                chunk_id=f"{job.id}#required_skills",
                job_id=job.id,
                chunk_type="required_skills",
                content=req_text,
                metadata={
                    "job_id": job.id,
                    "chunk_id": f"{job.id}#required_skills",
                    "chunk_type": "required_skills",
                    "job_title": job.job_title,
                    "company": job.company,
                    "domain": job.domain,
                    "location": job.location,
                    "work_mode": work_mode_str,
                    "is_remote": bool(job.is_remote),
                    "required_skills": skills_str,
                    "stipend": stipend_str,
                },
            )
        )

        pref_skills_str = ", ".join(job.preferred_skills) if job.preferred_skills else "None specified"
        edu_req = str(job.education_requirements) if job.education_requirements else "Pursuing Bachelor's or Master's in Computer Science or related"
        tags_str = ", ".join(job.tags) if job.tags else ""
        pref_text = (
            f"Job: {job.job_title} at {job.company}\n"
            f"Domain: {job.domain}\n"
            f"Preferred Skills: {pref_skills_str}\n"
            f"Education Requirements: {edu_req}\n"
            f"Domain Tags: {tags_str}"
        )
        chunks.append(
            JobChunk(
                chunk_id=f"{job.id}#preferred_skills",
                job_id=job.id,
                chunk_type="preferred_skills",
                content=pref_text,
                metadata={
                    "job_id": job.id,
                    "chunk_id": f"{job.id}#preferred_skills",
                    "chunk_type": "preferred_skills",
                    "job_title": job.job_title,
                    "company": job.company,
                    "domain": job.domain,
                    "location": job.location,
                    "work_mode": work_mode_str,
                    "is_remote": bool(job.is_remote),
                    "required_skills": skills_str,
                    "stipend": stipend_str,
                },
            )
        )

        return chunks

    @classmethod
    def chunk_all_jobs(cls, jobs: List[StandardJobPosting]) -> List[JobChunk]:
        all_chunks: List[JobChunk] = []
        for job in jobs:
            all_chunks.extend(cls.chunk_job(job))
        return all_chunks
