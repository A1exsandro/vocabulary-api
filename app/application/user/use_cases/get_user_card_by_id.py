import asyncio

from fastapi import HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.keycloak_admin_client import KeycloakAdminClient
from app.modules.category.CategoryModel import UserCategory
from app.modules.text.TextModel import TextEntry
from app.modules.user.UserSchema import UserCardItem
from app.modules.word.WordModel import UserWord


class GetUserCardByIdUseCase:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.keycloak_admin = KeycloakAdminClient.from_env()

    async def _count_for_user(self, model, count_column, user_id: str) -> int:
        stmt = select(func.count(func.distinct(count_column))).where(model.user_id == user_id)
        result = await self.db.execute(stmt)
        return int(result.scalar() or 0)

    async def execute(self, user_id: str) -> UserCardItem:
        user = await asyncio.to_thread(self.keycloak_admin.get_user_by_id, user_id)

        if not user:
            raise HTTPException(status_code=404, detail="Usuario nao encontrado.")

        return UserCardItem(
            id=user["id"],
            name=user["name"],
            username=user["username"],
            email=user["email"],
            enabled=user["enabled"],
            categoriesCount=await self._count_for_user(UserCategory, UserCategory.category_id, user_id),
            wordsCount=await self._count_for_user(UserWord, UserWord.word_id, user_id),
            textsCount=await self._count_for_user(TextEntry, TextEntry.id, user_id),
        )
