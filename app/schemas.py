# app/schemas.py
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List


# ============ SKILL SCHEMAS ============
class SkillCreate(BaseModel):
    """Схема для создания навыка (только админ)"""
    name: str = Field(..., min_length=1, max_length=100)
    category: str = Field(default="backend", max_length=50)


class SkillRead(BaseModel):
    """Схема для чтения навыка из БД"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    category: str


# ============ USER SCHEMAS ============
class UserCreate(BaseModel):
    """Схема для регистрации"""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=5, max_length=100)
    full_name: str = Field(..., min_length=1, max_length=100)
    timezone: str = Field(default="UTC", max_length=50)


class UserSkillUpdate(BaseModel):
    """Схема для добавления навыков к юзеру"""
    skill_ids: List[int] = Field(..., min_items=1)
    favorite_skill_ids: List[int] = Field(default_factory=list)  # Топ-3 навыка


class UserRead(BaseModel):
    """Схема для чтения профиля юзера"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str
    email: str
    full_name: str
    bio: Optional[str] = None
    timezone: str
    skills: List[SkillRead] = []


class UserProfileRead(UserRead):
    """Расширенная схема для профиля (с топ-3 и остальными навыками)"""
    # Этот класс развернет навыки на топ-3 + остальные на фронте
    pass


# ============ PROJECT SCHEMAS ============
class ProjectCreate(BaseModel):
    """Схема для создания проекта"""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10, max_length=2000)
    skill_ids: List[int] = Field(..., min_items=1)  # Какие навыки нужны для проекта


class ProjectRead(BaseModel):
    """Схема для чтения проекта"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    description: str
    status: str
    created_at: datetime
    updated_at: datetime
    owner: UserRead  # Кто создал проект
    skills: List[SkillRead] = []


class ProjectListRead(BaseModel):
    """Схема для списка проектов (без расширенных связей)"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    description: str
    status: str
    owner: UserRead
    skills: List[SkillRead] = []


# ============ APPLICATION SCHEMAS ============
class ApplicationCreate(BaseModel):
    """Схема для подачи заявки на проект"""
    project_id: int


class ApplicationRead(BaseModel):
    """Схема для чтения заявки"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    project_id: int
    applicant_id: int
    compatibility_score: float = Field(..., ge=0.0, le=1.0)  # От 0 до 1
    status: str
    created_at: datetime
    applicant: UserRead  # Кто подал заявку


class ApplicationDetailRead(ApplicationRead):
    """Расширенная схема для детального просмотра заявки"""
    project: ProjectRead  # Проект, на который подал заявку
    applicant: UserRead  # Человек, который подал заявку
