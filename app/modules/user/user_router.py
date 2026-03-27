from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.user.use_cases.get_user_card_by_id import GetUserCardByIdUseCase
from app.application.user.use_cases.list_user_cards import ListUserCardsUseCase
from app.core.config import get_db
from app.modules.user.UserSchema import UserCardItem

router = APIRouter(prefix="/api/vocabulary/user", tags=["User"])


@router.get("/cards", response_model=list[UserCardItem])
async def get_user_cards(db: AsyncSession = Depends(get_db)):
    return await ListUserCardsUseCase(db).execute()


@router.get("/{user_id}", response_model=UserCardItem)
async def get_user_by_id(user_id: str, db: AsyncSession = Depends(get_db)):
    return await GetUserCardByIdUseCase(db).execute(user_id)
