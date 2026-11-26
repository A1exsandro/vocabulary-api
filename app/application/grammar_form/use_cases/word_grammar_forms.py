"""Read and save a word's grammar card for one class (vocabulary-api#15)."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import commit_rollback
from app.core.exceptions import DomainError, NotFoundError
from app.core.grammar_forms import normalize_forms
from app.modules.grammar_form.GrammarFormRepository import GrammarFormRepository
from app.modules.grammar_form.GrammarFormSchema import GrammarFormsResponse, GrammarFormsUpdate


class _GrammarFormUseCase:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = GrammarFormRepository(db)

    async def _class_id(self, user_id: str, word_id: UUID, slug: str) -> UUID:
        grammar_class = await self.repository.get_grammar_class(slug)
        if grammar_class is None:
            raise NotFoundError("Classe gramatical não encontrada.")
        if not await self.repository.word_has_class_for_user(user_id, word_id, grammar_class.id):
            raise NotFoundError("Palavra não encontrada nesta classe gramatical.")
        return grammar_class.id

    async def _response(self, user_id: str, word_id: UUID, slug: str, grammar_class_id: UUID) -> GrammarFormsResponse:
        forms = await self.repository.get_forms(user_id, word_id, grammar_class_id)
        status = await self.repository.get_status(user_id, word_id, grammar_class_id)
        return GrammarFormsResponse(
            wordId=str(word_id),
            slug=slug,
            status=status.status if status else None,
            forms={
                form.field: {"english": form.english, "portuguese": form.portuguese, "spanish": form.spanish}
                for form in forms
            },
        )


class GetWordGrammarFormsUseCase(_GrammarFormUseCase):
    async def execute(self, user_id: str, word_id: UUID, slug: str) -> GrammarFormsResponse:
        grammar_class_id = await self._class_id(user_id, word_id, slug)
        return await self._response(user_id, word_id, slug, grammar_class_id)


class SaveWordGrammarFormsUseCase(_GrammarFormUseCase):
    async def execute(self, word_id: UUID, slug: str, update: GrammarFormsUpdate) -> GrammarFormsResponse:
        forms, problem = normalize_forms(slug, {key: value.model_dump() for key, value in update.forms.items()})
        if problem:
            raise DomainError(problem)
        grammar_class_id = await self._class_id(update.user_id, word_id, slug)
        await self.repository.replace(update.user_id, word_id, grammar_class_id, forms, update.status)
        await commit_rollback(self.db)
        return await self._response(update.user_id, word_id, slug, grammar_class_id)
