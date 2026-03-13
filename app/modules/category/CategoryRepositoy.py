from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import commit_rollback
from app.modules.category.CategorySchema import CategoryCreate
from app.modules.category.CategoryModel import Category


class CategoryRepository:

    # CREATE
    @staticmethod
    async def create(create_form: CategoryCreate, db: AsyncSession):
        name_upcase = create_form.name.upper()
        db.add(Category(name=name_upcase))
        await commit_rollback(db)
