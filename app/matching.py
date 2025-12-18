import math
from app.models import User, Project
from sqlalchemy.ext.asyncio import AsyncSession


async def calculate_compatibility(
    session: AsyncSession,
    user: User,
    project: Project,
) -> float:
    """
    Считает совместимость юзера с проектом используя Cosine Similarity.
    
    Формула: similarity = (A · B) / (||A|| * ||B||)
    
    Где:
    - A = вектор навыков юзера (1 если есть, 0 если нет)
    - B = вектор требуемых навыков проекта (1 если требуется, 0 если нет)
    
    Возвращает: число от 0 до 1 (0 = ничего общего, 1 = идеальное совпадение)
    """
    
    # Получаем ID навыков юзера
    user_skill_ids = {skill.id for skill in user.skills}
    
    # Получаем ID навыков проекта
    project_skill_ids = {skill.id for skill in project.skills}
    
    # Если у проекта нет требований или у юзера нет навыков
    if not project_skill_ids or not user_skill_ids:
        return 0.0
    
    # Считаем пересечение (точки произведения)
    intersection = len(user_skill_ids & project_skill_ids)
    
    # Считаем длины векторов (||A|| и ||B||)
    user_magnitude = math.sqrt(len(user_skill_ids))
    project_magnitude = math.sqrt(len(project_skill_ids))
    
    # Cosine Similarity
    if user_magnitude == 0 or project_magnitude == 0:
        return 0.0
    
    similarity = intersection / (user_magnitude * project_magnitude)
    
    # Нормализуем от 0 до 1
    return round(similarity, 2)


# Альтернативная версия: Jaccard Similarity (если будешь хотеть пересчитать)
async def calculate_compatibility_jaccard(
    session: AsyncSession,
    user: User,
    project: Project,
) -> float:
    """
    Jaccard Similarity = intersection / union
    Более строгая метрика.
    """
    user_skill_ids = {skill.id for skill in user.skills}
    project_skill_ids = {skill.id for skill in project.skills}
    
    if not project_skill_ids and not user_skill_ids:
        return 1.0
    
    if not project_skill_ids or not user_skill_ids:
        return 0.0
    
    intersection = len(user_skill_ids & project_skill_ids)
    union = len(user_skill_ids | project_skill_ids)
    
    similarity = intersection / union if union > 0 else 0.0
    return round(similarity, 2)
