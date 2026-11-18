
import uuid
from typing import Dict, List, Optional
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.application import (
    Application,
    ApplicationStage,
    ApplicationStageHistory,
)
from app.repositories.base import BaseRepository

class ApplicationRepository(BaseRepository[Application]):
    def __init__(self, db: AsyncSession):
        super().__init__(Application, db)

    async def get_by_candidate_and_job(
        self, candidate_id: uuid.UUID, job_id: uuid.UUID
    ) -> Optional[Application]:
        stmt = (
            select(Application)
            .where(
                Application.candidate_id == candidate_id,
                Application.job_id == job_id,
            )
            .options(
                selectinload(Application.job),
                selectinload(Application.stage_history),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_details(self, application_id: uuid.UUID) -> Optional[Application]:
        stmt = (
            select(Application)
            .where(Application.id == application_id)
            .options(
                selectinload(Application.job),
                selectinload(Application.stage_history),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_candidate(self, candidate_id: uuid.UUID) -> List[Application]:
        stmt = (
            select(Application)
            .where(Application.candidate_id == candidate_id)
            .options(
                selectinload(Application.job),
                selectinload(Application.stage_history),
            )
            .order_by(Application.updated_at.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def create_application(
        self,
        candidate_id: uuid.UUID,
        job_id: uuid.UUID,
        cover_letter_markdown: Optional[str] = None,
        initial_stage: str = ApplicationStage.WISHLIST.value,
    ) -> Application:
        application = Application(
            candidate_id=candidate_id,
            job_id=job_id,
            cover_letter_markdown=cover_letter_markdown,
            current_stage=initial_stage,
            applied_at=func.now() if initial_stage != ApplicationStage.WISHLIST.value else None,
        )
        self.db.add(application)
        await self.db.flush()

        history = ApplicationStageHistory(
            application_id=application.id,
            previous_stage=None,
            new_stage=initial_stage,
            notes="Application initial stage entry.",
        )
        self.db.add(history)
        await self.db.flush()

        return await self.get_with_details(application.id)

    async def update_stage(
        self,
        application: Application,
        new_stage: str,
        notes: Optional[str] = None,
    ) -> Application:
        old_stage = application.current_stage
        application.current_stage = new_stage
        if new_stage == ApplicationStage.APPLIED.value and not application.applied_at:
            application.applied_at = func.now()

        history = ApplicationStageHistory(
            application_id=application.id,
            previous_stage=old_stage,
            new_stage=new_stage,
            notes=notes,
        )
        self.db.add(history)
        await self.db.flush()
        return await self.get_with_details(application.id)
