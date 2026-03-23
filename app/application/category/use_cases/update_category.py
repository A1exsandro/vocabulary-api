from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.vocabulary_enricher import VocabularyEnricher
from app.core.config import commit_rollback
from app.core.exceptions import ConflictError, NotFoundError
from app.modules.category.CategoryRepositoy import CategoryRepository
from app.modules.category.CategorySchema import CategoryResponse, CategoryUpdate


class UpdateCategoryUseCase:
    def __init__(self, db: AsyncSession, vocabulary_enricher: VocabularyEnricher):
        self.db = db
        self.repository = CategoryRepository(db)
        self.vocabulary_enricher = vocabulary_enricher

    async def execute(self, category_id: UUID, update_form: CategoryUpdate) -> CategoryResponse:
        category = await self.repository.get_by_id(category_id)
        if not category:
            raise NotFoundError("Categoria não encontrada.")

        if not await self.repository.exists_user_category(update_form.user_id, category_id):
            raise NotFoundError("Categoria não encontrada para este usuário.")

        category_data = self.vocabulary_enricher.enrich(update_form.name)
        normalized_name = category_data["correct_word"]
        user_links = await self.repository.count_user_links(category_id)
        word_links = await self.repository.count_word_links(category_id)

        if normalized_name == category.name:
            return CategoryResponse(detail="Categoria atualizada com sucesso!")

        existing_category = await self.repository.get_category_by_name(normalized_name)
        if existing_category and existing_category.id != category_id:
            if await self.repository.exists_user_category(update_form.user_id, existing_category.id):
                raise ConflictError("Essa categoria já está na sua lista.")

            await self.repository.link_user_category(update_form.user_id, existing_category.id)
            await self.repository.unlink_user_category(update_form.user_id, category_id)

            if user_links == 1 and word_links == 0:
                await self.repository.delete_category(category)

            await commit_rollback(self.db)
            return CategoryResponse(detail="Categoria atualizada com sucesso!")

        if user_links > 1 or word_links > 0:
            new_category = await self.repository.create_category(normalized_name)
            await self.repository.link_user_category(update_form.user_id, new_category.id)
            await self.repository.unlink_user_category(update_form.user_id, category_id)
            await commit_rollback(self.db)
            return CategoryResponse(detail="Categoria atualizada com sucesso!")

        await self.repository.update_category_name(category, normalized_name)
        await commit_rollback(self.db)
        await self.db.refresh(category)
        return CategoryResponse(detail="Categoria atualizada com sucesso!")
