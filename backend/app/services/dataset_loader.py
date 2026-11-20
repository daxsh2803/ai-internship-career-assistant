import csv
import json
from pathlib import Path
from typing import Dict, List, Optional, Set
from app.schemas.job import StandardJobPosting, StandardJobPostingFilter, StandardJobPostingList

class DatasetLoaderService:
    _instance: Optional["DatasetLoaderService"] = None

    def __init__(self, data_path: Optional[Path] = None):
        if data_path:
            self.data_path = Path(data_path)
        else:
            root_dir = Path(__file__).resolve().parent.parent.parent
            candidate_paths = [
                root_dir / "data" / "jobs" / "internships_curated.json",
                root_dir.parent / "data" / "jobs" / "internships_curated.json",
                Path("data/jobs/internships_curated.json"),
                Path("M2/data/jobs/internships_curated.json"),
            ]
            self.data_path = next((p for p in candidate_paths if p.exists()), candidate_paths[0])

        self._cached_postings: List[StandardJobPosting] = []
        self._load_data()

    @classmethod
    def get_instance(cls, data_path: Optional[Path] = None) -> "DatasetLoaderService":
        if cls._instance is None:
            cls._instance = cls(data_path)
        return cls._instance

    def _load_data(self):
        if not self.data_path.exists():
            self._cached_postings = []
            return

        with open(self.data_path, "r", encoding="utf-8") as f:
            raw_items = json.load(f)

        self._cached_postings = [StandardJobPosting.model_validate(item) for item in raw_items]

    def reload(self):
        self._load_data()

    def get_all_postings(self) -> List[StandardJobPosting]:
        return list(self._cached_postings)

    def get_total_count(self) -> int:
        return len(self._cached_postings)

    def get_posting_by_id(self, job_id: str) -> Optional[StandardJobPosting]:
        for p in self._cached_postings:
            if p.id == job_id:
                return p
        return None

    def get_domains(self) -> List[str]:
        domains = sorted(list({p.domain for p in self._cached_postings if p.domain}))
        return domains

    def get_all_unique_skills(self) -> List[str]:
        skills_set: Set[str] = set()
        for p in self._cached_postings:
            skills_set.update(p.required_skills)
            skills_set.update(p.preferred_skills)
        return sorted(list(skills_set))

    def filter_postings(
        self,
        domain: Optional[str] = None,
        work_mode: Optional[str] = None,
        skills: Optional[List[str]] = None,
        search_query: Optional[str] = None,
    ) -> List[StandardJobPosting]:
        results = self._cached_postings

        if domain:
            dom_lower = domain.lower()
            results = [p for p in results if dom_lower in p.domain.lower()]

        if work_mode:
            wm_lower = work_mode.lower()
            results = [p for p in results if wm_lower == p.work_mode.lower()]

        if skills:
            skills_lower = {s.lower() for s in skills}
            results = [
                p for p in results
                if any(s.lower() in skills_lower for s in p.required_skills + p.preferred_skills)
            ]

        if search_query:
            q = search_query.lower()
            results = [
                p for p in results
                if q in p.job_title.lower()
                or q in p.company.lower()
                or q in p.job_description.lower()
                or any(q in t.lower() for t in p.tags)
            ]

        return results

    def get_paginated_list(
        self,
        filters: Optional[StandardJobPostingFilter] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> StandardJobPostingList:
        if filters:
            items = self.filter_postings(
                domain=filters.domain,
                work_mode=filters.work_mode,
                skills=filters.skills,
                search_query=filters.search_query,
            )
        else:
            items = self._cached_postings

        start = (page - 1) * page_size
        end = start + page_size
        paginated_items = items[start:end]

        return StandardJobPostingList(
            items=paginated_items,
            total=len(items),
            domains=self.get_domains(),
        )
