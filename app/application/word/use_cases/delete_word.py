from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import commit_rollback
from app.core.exceptions import NotFoundError
from app.modules.word.WordRepositoy import WordRepository
from app.modules.word.WordSchema import WordDelete, WordResponse


class DeleteWordUseCase:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = WordRepository(db)

    async def execute(self, word_id: UUID, delete_form: WordDelete) -> WordResponse:
        word = await self.repository.get_by_id(word_id)
        if not word:
            raise NotFoundError("Palavra não encontrada.")

        if not await self.repository.exists_user_word(delete_form.user_id, word_id):
            raise NotFoundError("Palavra não encontrada para este usuário.")

        await self.repository.unlink_user_word(delete_form.user_id, word_id)

        if await self.repository.count_user_links(word_id) == 0:
            await self.repository.delete_phrases_by_word_id(word_id)
            await self.repository.delete_word_categories_by_word_id(word_id)
            await self.repository.delete_word_grammar_classes_by_word_id(word_id)
            await self.repository.delete_word(word)

        await commit_rollback(self.db)
        return WordResponse(detail="Palavra removida com sucesso.")
