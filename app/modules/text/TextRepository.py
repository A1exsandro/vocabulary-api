from uuid import UUID

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from app.modules.text.TextModel import TextEntry


class TextRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_text(self, user_id: str, english: str, portuguese: str, audio_key: str | None):
        entry = TextEntry(
            user_id=user_id,
            english=english,
            portuguese=portuguese,
            audio_key=audio_key,
        )
        self.db.add(entry)
        await self.db.flush()
        return entry

    async def get_by_id(self, text_id: UUID):
        stmt = select(TextEntry).where(TextEntry.id == text_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: str):
        stmt = select(TextEntry).where(TextEntry.user_id == user_id).order_by(TextEntry.id.desc())
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update_text(self, entry: TextEntry, english: str, portuguese: str, audio_key: str | None):
        entry.english = english
        entry.portuguese = portuguese
        entry.audio_key = audio_key
        self.db.add(entry)
        await self.db.flush()
        return entry

    async def delete_text(self, entry: TextEntry):
        await self.db.delete(entry)
        await self.db.flush()

    async def count_similar_texts(self, user_id: str, english: str):
        stmt = select(func.count()).select_from(TextEntry).where(
            TextEntry.user_id == user_id,
            func.lower(TextEntry.english) == english.lower(),
        )
        result = await self.db.execute(stmt)
        return int(result.scalar_one())
