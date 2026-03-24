from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.vocabulary_enricher import VocabularyEnricher
from app.core.config import commit_rollback
from app.core.text_normalization import to_title_label
from app.modules.category.CategoryRepositoy import CategoryRepository
from app.modules.category.CategorySchema import CategoryCreate, CategoryResponse


class CreateCategoryUseCase:
    def __init__(self, db: AsyncSession, vocabulary_enricher: VocabularyEnricher):
        self.db = db
        self.repository = CategoryRepository(db)
        self.vocabulary_enricher = vocabulary_enricher

    async def execute(self, create_form: CategoryCreate) -> CategoryResponse:
        normalized_input = to_title_label(create_form.name)
        category = await self.repository.get_category_by_name(normalized_input)
        if category and await self.repository.exists_user_category(create_form.user_id, category.id):
            return CategoryResponse(detail="Essa Categoria já está na sua lista.")

        if not category:
            category_data = self.vocabulary_enricher.enrich(create_form.name.strip())
            correct_word = to_title_label(category_data["correct_word"])
            category = await self.repository.get_category_by_name(correct_word)

            if category and await self.repository.exists_user_category(create_form.user_id, category.id):
                return CategoryResponse(detail="Essa Categoria já está na sua lista.")

            if not category:
                category = await self.repository.create_category(correct_word)

        await self.repository.link_user_category(create_form.user_id, category.id)
        await commit_rollback(self.db)
        await self.db.refresh(category)

        return CategoryResponse(detail="Categoria Criada com sucesso!")
