# app/crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from datetime import datetime
from app.models import User, Skill, Project, Application
from app.schemas import UserCreate, ProjectCreate


# ============ USER CRUD ============
async def create_user(session: AsyncSession, user_data: UserCreate) -> User:
    """Создаёт нового юзера"""
    db_user = User(
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        timezone=user_data.timezone,
    )
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user, ["skills"])
    return db_user


async def get_user_by_id(session: AsyncSession, user_id: int) -> User | None:
    """Получает юзера по ID с его навыками"""
    stmt = (
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.skills))
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    """Получает юзера по username"""
    stmt = select(User).where(User.username == username)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def add_skills_to_user(
    session: AsyncSession,
    user_id: int,
    skill_ids: list[int],
    favorite_skill_ids: list[int] | None = None,
) -> User:
    """Добавляет навыки юзеру"""
    if favorite_skill_ids is None:
        favorite_skill_ids = []

    user = await get_user_by_id(session, user_id)
    if not user:
        raise ValueError(f"User {user_id} not found")

    for skill_id in skill_ids:
        skill = await get_skill_by_id(session, skill_id)
        if skill and skill not in user.skills:
            user.skills.append(skill)

    await session.commit()
    await session.refresh(user, ["skills"])
    return user


# ============ SKILL CRUD ============
async def create_skill(session: AsyncSession, name: str, category: str = "backend") -> Skill:
    """Создаёт новый навык"""
    db_skill = Skill(name=name, category=category)
    session.add(db_skill)
    await session.commit()
    await session.refresh(db_skill)
    return db_skill


async def get_skill_by_id(session: AsyncSession, skill_id: int) -> Skill | None:
    """Получает навык по ID"""
    stmt = select(Skill).where(Skill.id == skill_id)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_all_skills(session: AsyncSession) -> list[Skill]:
    """Получает все навыки"""
    stmt = select(Skill).order_by(Skill.category, Skill.name)
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_skill_by_name(session: AsyncSession, name: str) -> Skill | None:
    """Получает навык по названию"""
    stmt = select(Skill).where(Skill.name == name)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


# ============ PROJECT CRUD ============
async def create_project(
    session: AsyncSession,
    project_data: ProjectCreate,
    owner_id: int,
) -> Project:
    """Создаёт новый проект"""
    db_project = Project(
        title=project_data.title,
        description=project_data.description,
        owner_id=owner_id,
    )
    session.add(db_project)
    await session.flush()

    for skill_id in project_data.skill_ids:
        skill = await get_skill_by_id(session, skill_id)
        if skill and skill not in db_project.skills:
            db_project.skills.append(skill)

    await session.commit()
    await session.refresh(db_project, ["skills", "owner"])
    return db_project


async def get_project_by_id(session: AsyncSession, project_id: int) -> Project | None:
    """Получает проект по ID"""
    stmt = (
        select(Project)
        .where(Project.id == project_id)
        .options(
            selectinload(Project.owner).selectinload(User.skills),
            selectinload(Project.skills),
            selectinload(Project.applications).selectinload(Application.applicant).selectinload(User.skills),
        )
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_all_projects(
    session: AsyncSession,
    status: str = "open",
    limit: int = 50,
    offset: int = 0,
) -> list[Project]:
    """Получает все проекты"""
    stmt = (
        select(Project)
        .where(Project.status == status)
        .options(
            selectinload(Project.owner).selectinload(User.skills),
            selectinload(Project.skills),
        )
        .order_by(Project.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_user_projects(session: AsyncSession, owner_id: int) -> list[Project]:
    """Получает все проекты конкретного юзера"""
    stmt = (
        select(Project)
        .where(Project.owner_id == owner_id)
        .options(
            selectinload(Project.skills),
            selectinload(Project.applications).selectinload(Application.applicant).selectinload(User.skills),
        )
        .order_by(Project.created_at.desc())
    )
    result = await session.execute(stmt)
    return result.scalars().all()


# ============ APPLICATION CRUD ============
async def create_application(
    session: AsyncSession,
    project_id: int,
    applicant_id: int,
    compatibility_score: float,
) -> Application:
    """Создаёт новую заявку"""
    stmt = (
        select(Application)
        .where(Application.project_id == project_id)
        .where(Application.applicant_id == applicant_id)
        .where(Application.status == "pending")
    )
    result = await session.execute(stmt)
    if result.scalar_one_or_none():
        raise ValueError("Application already exists")

    db_app = Application(
        project_id=project_id,
        applicant_id=applicant_id,
        compatibility_score=compatibility_score,
        status="pending",
    )
    session.add(db_app)
    await session.commit()
    await session.refresh(db_app, ["project", "applicant"])
    return db_app


async def get_application_by_id(session: AsyncSession, app_id: int) -> Application | None:
    """Получает заявку по ID"""
    stmt = (
        select(Application)
        .where(Application.id == app_id)
        .options(
            selectinload(Application.project).selectinload(Project.skills),
            selectinload(Application.applicant).selectinload(User.skills),
        )
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def get_project_applications(
    session: AsyncSession,
    project_id: int,
    status: str = "pending",
) -> list[Application]:
    """Получает все заявки на проект"""
    stmt = (
        select(Application)
        .where(Application.project_id == project_id)
        .where(Application.status == status)
        .options(
            selectinload(Application.applicant).selectinload(User.skills),
            selectinload(Application.project).selectinload(Project.skills),
        )
        .order_by(Application.compatibility_score.desc())
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def update_application_status(
    session: AsyncSession,
    app_id: int,
    new_status: str,
) -> Application:
    """Обновляет статус заявки"""
    app = await get_application_by_id(session, app_id)
    if not app:
        raise ValueError(f"Application {app_id} not found")

    app.status = new_status
    await session.commit()
    await session.refresh(app, ["project", "applicant"])
    return app
