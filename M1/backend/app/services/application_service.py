
import uuid
from typing import Dict, List, Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.application import Application, ApplicationStage
from app.models.user import User
from app.repositories.application_repository import ApplicationRepository
from app.repositories.candidate_repository import CandidateRepository
from app.repositories.job_repository import JobRepository
from app.schemas.application import (
    ApplicationCreateRequest,
    ApplicationResponse,
    ApplicationStageUpdateRequest,
    KanbanBoardResponse,
    StageHistoryEntry,
)

class ApplicationService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.app_repo = ApplicationRepository(db)
        self.candidate_repo = CandidateRepository(db)
        self.job_repo = JobRepository(db)

    async def create_application(
        self, user: User, req: ApplicationCreateRequest
    ) -> ApplicationResponse:
        candidate = await self.candidate_repo.get_by_user_id(user.id)
        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Candidate profile does not exist. Please complete your profile first.",
            )

        job = await self.job_repo.get_by_id(req.job_id)
        if not job or not job.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="The requested job posting is inactive or does not exist.",
            )

        existing = await self.app_repo.get_by_candidate_and_job(candidate.id, req.job_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An application for this job already exists in your pipeline.",
            )

        app_obj = await self.app_repo.create_application(
            candidate_id=candidate.id,
            job_id=req.job_id,
            cover_letter_markdown=req.cover_letter_markdown,
            initial_stage=ApplicationStage.WISHLIST.value,
        )
        return self._map_to_response(app_obj)

    async def update_application_stage(
        self, user: User, application_id: uuid.UUID, req: ApplicationStageUpdateRequest
    ) -> ApplicationResponse:
        candidate = await self.candidate_repo.get_by_user_id(user.id)
        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Candidate profile not found.",
            )

        app_obj = await self.app_repo.get_with_details(application_id)
        if not app_obj or app_obj.candidate_id != candidate.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found or unauthorized.",
            )

        valid_stages = [s.value for s in ApplicationStage]
        if req.new_stage not in valid_stages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid stage '{req.new_stage}'. Must be one of: {valid_stages}",
            )

        updated = await self.app_repo.update_stage(
            application=app_obj,
            new_stage=req.new_stage,
            notes=req.notes,
        )
        return self._map_to_response(updated)

    async def get_application_by_id(
        self, user: User, application_id: uuid.UUID
    ) -> ApplicationResponse:
        candidate = await self.candidate_repo.get_by_user_id(user.id)
        if not candidate:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Candidate not found.")

        app_obj = await self.app_repo.get_with_details(application_id)
        if not app_obj or app_obj.candidate_id != candidate.id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found.")

        return self._map_to_response(app_obj)

    async def get_kanban_board(self, user: User) -> KanbanBoardResponse:
        candidate = await self.candidate_repo.get_by_user_id(user.id)
        if not candidate:
            return KanbanBoardResponse()

        apps = await self.app_repo.list_by_candidate(candidate.id)
        board = KanbanBoardResponse()

        for a in apps:
            resp = self._map_to_response(a)
            stage = a.current_stage.upper()
            if stage == ApplicationStage.WISHLIST.value:
                board.wishlist.append(resp)
            elif stage == ApplicationStage.APPLIED.value:
                board.applied.append(resp)
            elif stage == ApplicationStage.SCREENING.value:
                board.screening.append(resp)
            elif stage == ApplicationStage.TECHNICAL_ASSESSMENT.value:
                board.technical_assessment.append(resp)
            elif stage == ApplicationStage.INTERVIEW.value:
                board.interview.append(resp)
            elif stage == ApplicationStage.OFFER.value:
                board.offer.append(resp)
            elif stage == ApplicationStage.REJECTED.value:
                board.rejected.append(resp)
            elif stage == ApplicationStage.WITHDRAWN.value:
                board.withdrawn.append(resp)

        return board

    @staticmethod
    def _map_to_response(app_obj: Application) -> ApplicationResponse:
        history_entries = [
            StageHistoryEntry(
                id=h.id,
                previous_stage=h.previous_stage,
                new_stage=h.new_stage,
                notes=h.notes,
                transitioned_at=h.transitioned_at,
            )
            for h in (app_obj.stage_history or [])
        ]

        return ApplicationResponse(
            id=app_obj.id,
            candidate_id=app_obj.candidate_id,
            job_id=app_obj.job_id,
            job_title=app_obj.job.title if app_obj.job else "Target Role",
            company_name=app_obj.job.company_name if app_obj.job else "Company",
            current_stage=app_obj.current_stage,
            overall_match_score=app_obj.overall_match_score,
            match_breakdown=app_obj.match_breakdown or {},
            skill_gap_roadmap=app_obj.skill_gap_roadmap or {},
            cover_letter_markdown=app_obj.cover_letter_markdown,
            applied_at=app_obj.applied_at,
            created_at=app_obj.created_at,
            updated_at=app_obj.updated_at,
            stage_history=history_entries,
        )
