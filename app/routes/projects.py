# app/routes/projects.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import ProjectCreate, ProjectRead, ProjectListRead
from app.crud import (
    create_project,
    get_project_by_id,
    get_all_projects,
    get_user_projects,
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_new_project(
    project_data: ProjectCreate,
    owner_id: int = Query(..., description="ID юзера, который создает проект"),
    session: AsyncSession = Depends(get_db),
):
    """
    Создаёт новый проект.
    
    **Request:**
    ```
    {
        "title": "Web API на Python",
        "description": "Нужно сделать REST API для управления задачами...",
        "skill_ids":
    }
    ```
    
    `skill_ids` — ID навыков, которые требуются для проекта.
    """
    db_project = await create_project(session, project_data, owner_id)
    return db_project


@router.get("/", response_model=list[ProjectListRead])
async def list_projects(
    status_filter: str = Query("open", description="Фильтр по статусу (open/closed/in_progress)"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db),
):
    """
    Получает список всех проектов с фильтром по статусу.
    Используется для ленты на главной странице.
    """
    projects = await get_all_projects(session, status=status_filter, limit=limit, offset=offset)
    return projects


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project_detail(
    project_id: int,
    session: AsyncSession = Depends(get_db),
):
    """
    Получает детали конкретного проекта.
    """
    project = await get_project_by_id(session, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return project


@router.get("/owner/{owner_id}", response_model=list[ProjectListRead])
async def get_my_projects(
    owner_id: int,
    session: AsyncSession = Depends(get_db),
):
    """
    Получает все проекты конкретного юзера.
    """
    projects = await get_user_projects(session, owner_id)
    return projects
