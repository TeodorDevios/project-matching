from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas import UserCreate, UserRead, SkillRead, UserSkillUpdate
from app.crud import (
    create_user,
    get_user_by_id,
    get_user_by_username,
    add_skills_to_user,
    get_all_skills,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, session: AsyncSession = Depends(get_db)):
    """
    Регистрирует нового юзера.
    
    **Request:**
    ```
    {
        "username": "john_dev",
        "email": "john@example.com",
        "full_name": "John Developer",
        "timezone": "UTC"
    }
    ```
    """
    # Проверяем, не существует ли уже такой юзер
    existing_user = await get_user_by_username(session, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    db_user = await create_user(session, user_data)
    return db_user


@router.get("/profile/{user_id}", response_model=UserRead)
async def get_profile(user_id: int, session: AsyncSession = Depends(get_db)):
    """
    Получает профиль юзера со всеми его навыками.
    """
    user = await get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.post("/profile/{user_id}/skills", response_model=UserRead)
async def add_skills(
    user_id: int,
    skills_data: UserSkillUpdate,
    session: AsyncSession = Depends(get_db),
):
    """
    Добавляет навыки к юзеру.
    
    **Request:**
    ```
    {
        "skill_ids":,
        "favorite_skill_ids":
    }
    ```
    
    `favorite_skill_ids` — это топ-3 навыка, которые выводятся первыми на профиле.
    """
    user = await get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Валидация: не больше 3 favorite навыков
    if len(skills_data.favorite_skill_ids) > 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot have more than 3 favorite skills",
        )

    updated_user = await add_skills_to_user(
        session,
        user_id,
        skills_data.skill_ids,
        skills_data.favorite_skill_ids,
    )
    return updated_user


@router.get("/skills", response_model=list[SkillRead])
async def list_skills(session: AsyncSession = Depends(get_db)):
    """
    Получает список всех доступных навыков.
    Используется в выпадающем списке на фронте.
    """
    skills = await get_all_skills(session)
    return skills
