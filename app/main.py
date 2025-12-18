# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from app.database import init_db  # ← ПРАВИЛЬНО
  # ← Относительный импорт
from app.routes import auth, projects, applications  # ← Относительный импорт


# Создаём FastAPI приложение
app = FastAPI(
    title="Project Partner Matching API",
    description="Платформа для поиска партнеров на проекты",
    version="1.0.0",
)


# ============ CORS ============
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ LIFESPAN (Инициализация при запуске) ============
@app.on_event("startup")
async def startup_event():
    """Вызывается при запуске приложения"""
    print("🚀 Инициализируем БД...")
    await init_db()
    print("✅ БД готова!")


# ============ МАРШРУТЫ ============
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(applications.router)


# ============ ROOT ENDPOINT ============
@app.get("/", tags=["root"])
async def root():
    """Проверка, что API живой"""
    return {
        "message": "🎉 Project Partner Matching API работает!",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["health"])
async def health_check():
    """Health check для мониторинга"""
    return {"status": "ok"}


# ============ ЗАПУСК ============
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
