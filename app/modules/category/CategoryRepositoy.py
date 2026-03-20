from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from app.core.config import commit_rollback
from app.modules.category.CategorySchema import CategoryCreate
from app.modules.category.CategoryModel import Category, UserCategory
from app.integrations.openrouter_client import generate_sentences


class CategoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    # CREATE
    async def create_category(self, name): 
        category = Category(name=name)
        self.db.add(category)
        await self.db.commit()
        await self.db.refresh(category)

        return category
    

    # CRIA A RELAÇÃO CATEGORIA USER
    async def link_user_category(self, user_id, category_id):
        user_category = UserCategory(
            user_id=user_id,
            category_id=category_id
        ) 
        self.db.add(user_category)
        await self.db.commit()
        

    # GET CATEGORY BY NAME
    async def get_category_by_name(self, english: str):
        stmt = select(Category).where(Category.name == english)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()


    # VERIFICA SE EXISTE RELAÇÃO CATEGORIA USER
    async def exists_user_category(self, user_id, category_id):
        stmt = select(UserCategory).where(
            UserCategory.user_id == user_id,
            UserCategory.category_id == category_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
