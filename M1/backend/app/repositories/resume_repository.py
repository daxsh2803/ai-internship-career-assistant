
import uuid
from typing import List, Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.resume import Resume, ResumeSection
from app.repositories.base import BaseRepository

class ResumeRepository(BaseRepository[Resume]):
    def __init__(self, db: AsyncSession):
        super().__init__(Resume, db)

    async def get_by_candidate_id(self, candidate_id: uuid.UUID) -> List[Resume]:
        stmt = (
            select(Resume)
            .where(Resume.candidate_id == candidate_id)
            .options(selectinload(Resume.sections))
            .order_by(Resume.uploaded_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_primary(self, candidate_id: uuid.UUID) -> Optional[Resume]:
        stmt = (
            select(Resume)
            .where(Resume.candidate_id == candidate_id, Resume.is_primary == True)
            .options(selectinload(Resume.sections))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def unset_primary_flags(self, candidate_id: uuid.UUID) -> None:
        stmt = (
            update(Resume)
            .where(Resume.candidate_id == candidate_id)
            .values(is_primary=False)
        )
        await self.db.execute(stmt)
        await self.db.flush()

    async def add_sections(self, sections: List[ResumeSection]) -> None:
        self.db.add_all(sections)
        await self.db.flush()
