from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import commit_rollback
from app.core.exceptions import NotFoundError
from app.modules.category.CategoryRepositoy import CategoryRepository
from app.modules.category.CategorySchema import CategoryDelete, CategoryResponse


class DeleteCategoryUseCase:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = CategoryRepository(db)

    async def execute(self, category_id: UUID, delete_form: CategoryDelete) -> CategoryResponse:
        category = await self.repository.get_by_id(category_id)
        if not category:
            raise NotFoundError("Categoria não encontrada.")

        if not await self.repository.exists_user_category(delete_form.user_id, category_id):
            raise NotFoundError("Categoria não encontrada para este usuário.")

        await self.repository.unlink_user_category(delete_form.user_id, category_id)

        remaining_user_links = await self.repository.count_user_links(category_id)
        remaining_word_links = await self.repository.count_word_links(category_id)

        if remaining_user_links == 0 and remaining_word_links == 0:
            await self.repository.delete_category(category)

        await commit_rollback(self.db)
        return CategoryResponse(detail="Categoria removida com sucesso.")
