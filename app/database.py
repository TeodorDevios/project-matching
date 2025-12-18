from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
import os

# SQLite async URL
DATABASE_URL = "sqlite+aiosqlite:///./project_matching.db"

# Создаём асинхронный движок
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Поставь True если хочешь видеть SQL запросы в консоли
    future=True,
)

# Фабрика сессий (async)
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# Базовый класс для всех моделей
class Base(DeclarativeBase):
    pass


# Функция для инициализации БД (создаст все таблицы)
async def init_db():
    """Создаёт все таблицы при запуске приложения"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ БД инициализирована!")


# Dependency для FastAPI (будут использовать в роутах позже)
async def get_db():
    """Возвращает сессию для использования в эндпоинтах"""
    async with async_session_maker() as session:
        yield session
