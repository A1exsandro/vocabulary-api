from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.modules.category.CategoryModel import Category, UserCategory
from app.modules.category.CategoryRepositoy import CategoryRepository
from app.modules.category.CategorySchema import CategoryResponse, CategoryCreate

from app.core.config import commit_rollback
from app.integrations.openrouter_client import generate_sentences

class CategoryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = CategoryRepository(db)

    # CREATE
    async def create(self, create_form: CategoryCreate):

        # verificar se já existe
        category = await self.repository.get_category_by_name(create_form.name)
        if category:
            # verificar se relação user_categoria existe
            if await self.repository.exists_user_category(create_form.user_id, category.id):
                return CategoryResponse(detail="Essa Categoria já está na sua lista.")

        if not category:
            category_data = generate_sentences(create_form.name)
            correct_word = category_data["correct_word"]

            category = await self.repository.create_category(
                name=correct_word
            )
            
        # cria relação
        await self.repository.link_user_category(create_form.user_id, category.id)
        return CategoryResponse(detail="Categoria Criada com sucesso!")


    # Get by user
    async def get_by_user(user_id: str, db: AsyncSession):

        stmt = (
            select(Category)
            .join(UserCategory)
            .where(UserCategory.user_id == user_id)
        )

        result = await db.execute(stmt)
        categories = result.scalars().unique().all()

        return categories
    