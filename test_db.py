import asyncio
from app.database import async_session_maker
from app.crud import create_skill

async def seed_skills():
    """Заполняет БД навыками"""
    async with async_session_maker() as session:
        skills_data = [
            ("Python", "backend"),
            ("FastAPI", "backend"),
            ("PostgreSQL", "backend"),
            ("SQLAlchemy", "backend"),
            ("Docker", "devops"),
            ("Kubernetes", "devops"),
            ("React", "frontend"),
            ("TypeScript", "frontend"),
            ("Tailwind CSS", "frontend"),
            ("JavaScript", "frontend"),
            ("Vue.js", "frontend"),
            ("Figma", "design"),
            ("UI/UX Design", "design"),
            ("Git", "tools"),
            ("GitHub", "tools"),
        ]
        
        for name, category in skills_data:
            try:
                await create_skill(session, name, category)
                print(f"✅ {name}")
            except Exception as e:
                print(f"⚠️  {name}: {e}")

asyncio.run(seed_skills())
