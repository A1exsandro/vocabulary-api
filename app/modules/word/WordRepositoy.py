from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from app.core.config import commit_rollback
from app.modules.word.WordModel import Word, Phrase, UserWord, WordCategory


class WordRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_english(self, english: str):
        stmt = select(Word).where(Word.english == english)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_word(self, english, portuguese, image_key, audio_key, category_id):

        word = Word(
            english=english,
            portuguese=portuguese,
            image_key=image_key,
            audio_key=audio_key
        )

        self.db.add(word)
        await self.db.flush()

        word_category = WordCategory(
            word_id=word.id,
            category_id=category_id
        )

        self.db.add(word_category)

        await self.db.commit()
        await self.db.refresh(word)

        return word

    async def create_phrase(self, word_id, text, audio_key):
        phrase = Phrase(
            word_id=word_id,
            text=text,
            audio_key=audio_key
        )
        self.db.add(phrase)
        await self.db.commit()

    async def link_user_word(self, user_id, word_id):
        user_word = UserWord(user_id=user_id, word_id=word_id)
        self.db.add(user_word)
        await self.db.commit()
        

    async def exists_user_word(self, user_id, word_id):
        stmt = select(UserWord).where(
            UserWord.user_id == user_id,
            UserWord.word_id == word_id
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none() is not None
    