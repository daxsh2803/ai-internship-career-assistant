
import uuid
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.candidate import Candidate
from app.models.skill import CandidateSkill, Education, Project, Skill, WorkExperience
from app.repositories.base import BaseRepository

class CandidateRepository(BaseRepository[Candidate]):
    def __init__(self, db: AsyncSession):
        super().__init__(Candidate, db)

    async def get_by_user_id(self, user_id: uuid.UUID) -> Optional[Candidate]:
        stmt = (
            select(Candidate)
            .where(Candidate.user_id == user_id)
            .options(
                selectinload(Candidate.educations),
                selectinload(Candidate.work_experiences),
                selectinload(Candidate.projects),
                selectinload(Candidate.skills).selectinload(CandidateSkill.skill),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_details(self, candidate_id: uuid.UUID) -> Optional[Candidate]:
        stmt = (
            select(Candidate)
            .where(Candidate.id == candidate_id)
            .options(
                selectinload(Candidate.educations),
                selectinload(Candidate.work_experiences),
                selectinload(Candidate.projects),
                selectinload(Candidate.skills).selectinload(CandidateSkill.skill),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def add_education(self, education: Education) -> Education:
        self.db.add(education)
        await self.db.flush()
        return education

    async def add_project(self, project: Project) -> Project:
        self.db.add(project)
        await self.db.flush()
        return project

    async def add_work_experience(self, exp: WorkExperience) -> WorkExperience:
        self.db.add(exp)
        await self.db.flush()
        return exp

    async def get_or_create_skill(self, name: str, category: str = "Technical Skills") -> Skill:
        stmt = select(Skill).where(Skill.name == name.strip())
        result = await self.db.execute(stmt)
        skill = result.scalar_one_or_none()
        if not skill:
            skill = Skill(name=name.strip(), category=category)
            self.db.add(skill)
            await self.db.flush()
        return skill

    async def attach_skill(
        self,
        candidate_id: uuid.UUID,
        skill_id: uuid.UUID,
        proficiency: str = "INTERMEDIATE",
        years_experience: float = 1.0,
    ) -> CandidateSkill:
        stmt = select(CandidateSkill).where(
            CandidateSkill.candidate_id == candidate_id,
            CandidateSkill.skill_id == skill_id,
        )
        result = await self.db.execute(stmt)
        link = result.scalar_one_or_none()
        if not link:
            link = CandidateSkill(
                candidate_id=candidate_id,
                skill_id=skill_id,
                proficiency=proficiency,
                years_experience=years_experience,
            )
            self.db.add(link)
            await self.db.flush()
        return link
