# app/routes/applications.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import ApplicationCreate, ApplicationRead, ApplicationDetailRead
from app.crud import (
    get_user_by_id,
    get_project_by_id,
    create_application,
    get_application_by_id,
    get_project_applications,
    update_application_status,
)

from app.matching import calculate_compatibility

router = APIRouter(prefix="/applications", tags=["applications"])


@router.post("/", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
async def submit_application(
    app_data: ApplicationCreate,
    applicant_id: int = Query(...),
    session: AsyncSession = Depends(get_db),
):
    """
    Подаёт заявку на проект с автоматическим расчётом совместимости.
    """
    user = await get_user_by_id(session, applicant_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    project = await get_project_by_id(session, app_data.project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if project.owner_id == applicant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot apply to your own project",
        )

    # ГЛАВНОЕ: считаем совместимость
    compatibility_score = await calculate_compatibility(session, user, project)

    # Создаём заявку
    db_app = await create_application(
        session,
        app_data.project_id,
        applicant_id,
        compatibility_score,
    )

    return db_app


@router.get("/{app_id}", response_model=ApplicationDetailRead)
async def get_application_detail(
    app_id: int,
    session: AsyncSession = Depends(get_db),
):
    """
    Получает детали заявки с информацией о юзере и проекте.
    """
    app = await get_application_by_id(session, app_id)
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found",
        )
    return app


@router.get("/project/{project_id}", response_model=list[ApplicationDetailRead])
async def list_project_applications(
    project_id: int,
    session: AsyncSession = Depends(get_db),
):
    """
    Получает все заявки на конкретный проект (отсортированы по совместимости).
    """
    applications = await get_project_applications(session, project_id)
    return applications


@router.patch("/{app_id}/accept", response_model=ApplicationRead)
async def accept_application(
    app_id: int,
    session: AsyncSession = Depends(get_db),
):
    """
    Принимает заявку (статус: pending → accepted).
    """
    updated_app = await update_application_status(session, app_id, "accepted")
    return updated_app


@router.patch("/{app_id}/reject", response_model=ApplicationRead)
async def reject_application(
    app_id: int,
    session: AsyncSession = Depends(get_db),
):
    """
    Отклоняет заявку (статус: pending → rejected).
    """
    updated_app = await update_application_status(session, app_id, "rejected")
    return updated_app
