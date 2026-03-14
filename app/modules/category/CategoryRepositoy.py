from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from app.core.config import commit_rollback
from app.modules.category.CategorySchema import CategoryCreate
from app.modules.category.CategoryModel import Category


class CategoryRepository:

    # CREATE
    @staticmethod
    async def create(create_form: CategoryCreate, db: AsyncSession):
        name_upcase = create_form.name.upper()
        user_id = create_form.user_id
        db.add(Category(name=name_upcase, user_id=user_id))
        await commit_rollback(db)


    # READ
    @staticmethod
    async def get_all(db: AsyncSession, limit: int = 10, offset: int = 0):
        query = select(Category).limit(limit).offset(offset)
        result = await db.execute(query)
        return result.scalars().all()
