from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.grammar_form.GrammarFormModel import WordForm, WordGrammarStatus
from app.modules.word.WordModel import GrammarClass, UserWord, Word, WordGrammarClass


class GrammarFormRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_grammar_class(self, slug: str) -> GrammarClass | None:
        result = await self.db.execute(select(GrammarClass).where(GrammarClass.slug == slug))
        return result.scalar_one_or_none()

    async def word_has_class_for_user(self, user_id: str, word_id: UUID, grammar_class_id: UUID) -> bool:
        """The word has the class and the user can see it (linked, or a shared word)."""
        stmt = (
            select(Word.id)
            .join(WordGrammarClass, WordGrammarClass.word_id == Word.id)
            .outerjoin(UserWord, (UserWord.word_id == Word.id) & (UserWord.user_id == user_id))
            .where(Word.id == word_id, WordGrammarClass.grammar_class_id == grammar_class_id)
            .where((UserWord.user_id.is_not(None)) | (Word.owner_user_id.is_(None)))
        )
        return (await self.db.execute(stmt)).first() is not None

    async def get_forms(self, user_id: str, word_id: UUID, grammar_class_id: UUID) -> list[WordForm]:
        stmt = select(WordForm).where(
            WordForm.user_id == user_id,
            WordForm.word_id == word_id,
            WordForm.grammar_class_id == grammar_class_id,
        )
        return list((await self.db.execute(stmt)).scalars().all())

    async def get_status(self, user_id: str, word_id: UUID, grammar_class_id: UUID) -> WordGrammarStatus | None:
        stmt = select(WordGrammarStatus).where(
            WordGrammarStatus.user_id == user_id,
            WordGrammarStatus.word_id == word_id,
            WordGrammarStatus.grammar_class_id == grammar_class_id,
        )
        return (await self.db.execute(stmt)).scalar_one_or_none()

    async def replace(self, user_id: str, word_id: UUID, grammar_class_id: UUID, forms: dict[str, dict], status: str):
        await self.delete_card(user_id, word_id, grammar_class_id)
        if not forms:
            return
        for field, value in forms.items():
            self.db.add(WordForm(user_id=user_id, word_id=word_id, grammar_class_id=grammar_class_id, field=field, **value))
        self.db.add(
            WordGrammarStatus(
                user_id=user_id,
                word_id=word_id,
                grammar_class_id=grammar_class_id,
                status=status,
                updated_at=datetime.now(timezone.utc).isoformat(),
            )
        )
        await self.db.flush()

    async def delete_card(self, user_id: str, word_id: UUID, grammar_class_id: UUID):
        for model in (WordForm, WordGrammarStatus):
            await self.db.execute(
                delete(model).where(
                    model.user_id == user_id, model.word_id == word_id, model.grammar_class_id == grammar_class_id
                )
            )
        await self.db.flush()


async def delete_user_word_cards(db: AsyncSession, user_id: str, word_id: UUID):
    """A user who removes a word loses its grammar cards."""
    for model in (WordForm, WordGrammarStatus):
        await db.execute(delete(model).where(model.user_id == user_id, model.word_id == word_id))
    await db.flush()


async def delete_cards_outside_classes(db: AsyncSession, word_id: UUID, grammar_class_ids: list[UUID]):
    """A class taken off a word takes its cards with it, for every user."""
    for model in (WordForm, WordGrammarStatus):
        stmt = delete(model).where(model.word_id == word_id)
        if grammar_class_ids:
            stmt = stmt.where(model.grammar_class_id.not_in(grammar_class_ids))
        await db.execute(stmt)
    await db.flush()
