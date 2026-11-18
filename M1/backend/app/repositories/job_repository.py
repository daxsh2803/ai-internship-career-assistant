
import uuid
from typing import List, Optional, Tuple
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.job import Job, JobRequirement
from app.repositories.base import BaseRepository

class JobRepository(BaseRepository[Job]):
    def __init__(self, db: AsyncSession):
        super().__init__(Job, db)

    async def get_with_requirements(self, job_id: uuid.UUID) -> Optional[Job]:
        stmt = (
            select(Job)
            .where(Job.id == job_id)
            .options(selectinload(Job.requirements))
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_jobs(
        self,
        skip: int = 0,
        limit: int = 20,
        is_remote: Optional[bool] = None,
        max_gpa_requirement: Optional[float] = None,
        search_query: Optional[str] = None,
    ) -> Tuple[List[Job], int]:
        stmt = select(Job).where(Job.is_active == True).options(selectinload(Job.requirements))

        if is_remote is not None:
            stmt = stmt.where(Job.is_remote == is_remote)
        if max_gpa_requirement is not None:
            stmt = stmt.where(Job.min_gpa <= max_gpa_requirement)
        if search_query:
            term = f"%{search_query.strip()}%"
            stmt = stmt.where(
                (Job.title.ilike(term)) | (Job.company_name.ilike(term)) | (Job.location.ilike(term))
            )

        count_stmt = select(func.count()).select_from(stmt.subquery())
        count_res = await self.db.execute(count_stmt)
        total = count_res.scalar() or 0

        stmt = stmt.order_by(Job.created_at.desc()).offset(skip).limit(limit)
        items_res = await self.db.execute(stmt)
        items = list(items_res.scalars().all())

        return items, total

    async def add_requirements(self, requirements: List[JobRequirement]) -> None:
        self.db.add_all(requirements)
        await self.db.flush()
