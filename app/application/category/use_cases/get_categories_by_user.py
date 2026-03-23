from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.modules.category.CategoryModel import Category, UserCategory


class GetCategoriesByUserUseCase:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute(self, user_id: str):
        stmt = (
            select(Category)
            .join(UserCategory)
            .where(UserCategory.user_id == user_id)
        )

        result = await self.db.execute(stmt)
        return result.scalars().unique().all()
