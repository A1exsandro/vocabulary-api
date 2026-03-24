from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from app.modules.category.CategoryModel import Category, UserCategory
from app.modules.word.WordModel import WordCategory


class CategoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_category(self, name):
        category = Category(name=name)
        self.db.add(category)
        await self.db.flush()
        return category

    async def link_user_category(self, user_id, category_id):
        user_category = UserCategory(
            user_id=user_id,
            category_id=category_id
        )
        self.db.add(user_category)

    async def get_category_by_name(self, name: str):
        normalized = name.lower()
        stmt = select(Category).where(func.lower(Category.name) == normalized)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def exists_user_category(self, user_id, category_id):
        stmt = select(UserCategory).where(
            UserCategory.user_id == user_id,
            UserCategory.category_id == category_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_by_id(self, category_id):
        stmt = select(Category).where(Category.id == category_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def count_user_links(self, category_id):
        stmt = select(UserCategory).where(UserCategory.category_id == category_id)
        result = await self.db.execute(stmt)
        return len(result.scalars().all())

    async def update_category_name(self, category: Category, name: str):
        category.name = name
        self.db.add(category)
        return category

    async def count_word_links(self, category_id):
        stmt = select(WordCategory).where(WordCategory.category_id == category_id)
        result = await self.db.execute(stmt)
        return len(result.scalars().all())

    async def unlink_user_category(self, user_id, category_id):
        stmt = select(UserCategory).where(
            UserCategory.user_id == user_id,
            UserCategory.category_id == category_id
        )
        result = await self.db.execute(stmt)
        user_category = result.scalar_one_or_none()

        if user_category:
            await self.db.delete(user_category)

        return user_category

    async def delete_category(self, category: Category):
        await self.db.delete(category)
