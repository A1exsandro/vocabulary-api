import asyncio
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.keycloak_admin_client import KeycloakAdminClient
from app.modules.category.CategoryModel import UserCategory
from app.modules.text.TextModel import TextEntry
from app.modules.user.UserSchema import UserCardItem
from app.modules.word.WordModel import UserWord


class ListUserCardsUseCase:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.keycloak_admin = KeycloakAdminClient.from_env()

    async def _build_count_map(self, model, count_column) -> dict[str, int]:
        stmt = (
            select(model.user_id, func.count(func.distinct(count_column)).label("total"))
            .group_by(model.user_id)
        )
        result = await self.db.execute(stmt)
        rows: Sequence[tuple[str, int]] = result.all()
        return {row[0]: int(row[1]) for row in rows}

    async def execute(self) -> list[UserCardItem]:
        users = await asyncio.to_thread(self.keycloak_admin.list_users)
        category_counts = await self._build_count_map(UserCategory, UserCategory.category_id)
        word_counts = await self._build_count_map(UserWord, UserWord.word_id)
        text_counts = await self._build_count_map(TextEntry, TextEntry.id)

        cards = [
            UserCardItem(
                id=user["id"],
                name=user["name"],
                username=user["username"],
                email=user["email"],
                enabled=user["enabled"],
                categoriesCount=category_counts.get(user["id"], 0),
                wordsCount=word_counts.get(user["id"], 0),
                textsCount=text_counts.get(user["id"], 0),
            )
            for user in users
        ]

        return sorted(cards, key=lambda item: item.name.lower())
