from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from app.modules.word.WordModel import GrammarClass, Phrase, UserWord, Word, WordCategory, WordGrammarClass


class WordRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_english(self, english: str):
        normalized = english.lower()
        stmt = (
            select(Word)
            .where(func.lower(Word.english) == normalized)
            .order_by(Word.owner_user_id.is_not(None), Word.id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_shareable_word_by_english(self, english: str):
        normalized = english.lower()
        stmt = (
            select(Word)
            .where(func.lower(Word.english) == normalized, Word.owner_user_id.is_(None))
            .order_by(Word.id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_user_word_by_english(self, user_id: str, english: str):
        normalized = english.lower()
        stmt = (
            select(Word)
            .join(UserWord)
            .where(UserWord.user_id == user_id, func.lower(Word.english) == normalized)
            .order_by(Word.id)
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def create_word(self, english, portuguese, image_key, audio_key, category_id, owner_user_id=None):
        word = Word(
            english=english,
            portuguese=portuguese,
            image_key=image_key,
            audio_key=audio_key,
            owner_user_id=owner_user_id,
        )

        self.db.add(word)
        await self.db.flush()
        await self.ensure_word_category(word.id, category_id)

        return word

    async def create_phrase(self, word_id, text, audio_key, translation=None):
        phrase = Phrase(
            word_id=word_id,
            text=text,
            translation=translation,
            audio_key=audio_key,
        )
        self.db.add(phrase)
        await self.db.flush()

    async def link_user_word(self, user_id, word_id):
        if await self.exists_user_word(user_id, word_id):
            return None

        user_word = UserWord(user_id=user_id, word_id=word_id)
        self.db.add(user_word)
        await self.db.flush()
        return user_word

    async def exists_user_word(self, user_id, word_id):
        stmt = select(UserWord).where(UserWord.user_id == user_id, UserWord.word_id == word_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None

    async def get_by_id(self, word_id):
        stmt = select(Word).where(Word.id == word_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_grammar_classes_by_slugs(self, slugs: list[str]):
        if not slugs:
            return []

        stmt = select(GrammarClass).where(GrammarClass.slug.in_(slugs))
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_word_category(self, word_id, category_id):
        stmt = select(WordCategory).where(
            WordCategory.word_id == word_id,
            WordCategory.category_id == category_id,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def ensure_word_category(self, word_id, category_id):
        word_category = await self.get_word_category(word_id, category_id)
        if word_category:
            return word_category

        word_category = WordCategory(word_id=word_id, category_id=category_id)
        self.db.add(word_category)
        await self.db.flush()
        return word_category

    async def count_user_links(self, word_id):
        stmt = select(func.count()).select_from(UserWord).where(UserWord.word_id == word_id)
        result = await self.db.execute(stmt)
        return int(result.scalar_one())

    async def update_word(self, word: Word, english: str, portuguese: str, image_key: str, audio_key: str, owner_user_id=None):
        word.english = english
        word.portuguese = portuguese
        word.image_key = image_key
        word.audio_key = audio_key
        word.owner_user_id = owner_user_id
        self.db.add(word)
        await self.db.flush()
        return word

    async def delete_phrases_by_word_id(self, word_id):
        stmt = select(Phrase).where(Phrase.word_id == word_id)
        result = await self.db.execute(stmt)

        for phrase in result.scalars().all():
            await self.db.delete(phrase)

    async def replace_phrases(self, word_id, phrases_data):
        await self.delete_phrases_by_word_id(word_id)

        for phrase in phrases_data:
            phrase_model = Phrase(
                word_id=word_id,
                text=phrase["text"],
                translation=phrase.get("translation"),
                audio_key=phrase.get("audio_key"),
            )
            self.db.add(phrase_model)
        await self.db.flush()

    async def delete_word_grammar_classes_by_word_id(self, word_id):
        stmt = select(WordGrammarClass).where(WordGrammarClass.word_id == word_id)
        result = await self.db.execute(stmt)

        for word_grammar_class in result.scalars().all():
            await self.db.delete(word_grammar_class)

        await self.db.flush()

    async def replace_word_grammar_classes(self, word_id, grammar_class_slugs: list[str]):
        await self.delete_word_grammar_classes_by_word_id(word_id)
        grammar_classes = await self.get_grammar_classes_by_slugs(grammar_class_slugs)

        for grammar_class in grammar_classes:
            self.db.add(
                WordGrammarClass(
                    word_id=word_id,
                    grammar_class_id=grammar_class.id,
                )
            )

        await self.db.flush()

    async def unlink_user_word(self, user_id, word_id):
        stmt = select(UserWord).where(UserWord.user_id == user_id, UserWord.word_id == word_id)
        result = await self.db.execute(stmt)
        user_word = result.scalar_one_or_none()

        if user_word:
            await self.db.delete(user_word)
            await self.db.flush()

        return user_word

    async def delete_word_categories_by_word_id(self, word_id):
        stmt = select(WordCategory).where(WordCategory.word_id == word_id)
        result = await self.db.execute(stmt)

        for word_category in result.scalars().all():
            await self.db.delete(word_category)

    async def delete_word(self, word: Word):
        await self.db.delete(word)
        await self.db.flush()
