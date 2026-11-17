
from typing import List
import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_student
from app.core.database import get_db
from app.models.user import User
from app.schemas.application import (
    ApplicationCreateRequest,
    ApplicationResponse,
    ApplicationStageUpdateRequest,
    KanbanBoardResponse,
)
from app.services.application_service import ApplicationService

router = APIRouter(prefix="/applications", tags=["Application Tracking & Pipeline"])

@router.get("/kanban", response_model=KanbanBoardResponse)
async def get_kanban_board(
    current_user: User = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
):
    app_service = ApplicationService(db)
    return await app_service.get_kanban_board(current_user)

@router.post("", response_model=ApplicationResponse, status_code=status.HTTP_201_CREATED)
async def create_application(
    req: ApplicationCreateRequest,
    current_user: User = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
):
    app_service = ApplicationService(db)
    return await app_service.create_application(current_user, req)

@router.get("/{application_id}", response_model=ApplicationResponse)
async def get_application(
    application_id: uuid.UUID,
    current_user: User = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
):
    app_service = ApplicationService(db)
    return await app_service.get_application_by_id(current_user, application_id)

@router.patch("/{application_id}/stage", response_model=ApplicationResponse)
async def update_application_stage(
    application_id: uuid.UUID,
    req: ApplicationStageUpdateRequest,
    current_user: User = Depends(get_current_student),
    db: AsyncSession = Depends(get_db),
):
    app_service = ApplicationService(db)
    return await app_service.update_application_stage(current_user, application_id, req)
