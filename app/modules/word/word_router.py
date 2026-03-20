from fastapi import APIRouter, Path, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_db

from app.modules.word.WordSchema import WordCreate, WordResponse
from app.modules.word.WordRepositoy import WordRepository
from app.modules.word.WordService import WordService

router = APIRouter(
    prefix="/api/vacabulary/word",
    tags=['Word']
)

# CREATE
@router.post("", response_model_exclude_none=True)
async def create_word(
    create_form: WordCreate,
    db: AsyncSession = Depends(get_db)
):
    return await WordService(db).create(create_form) 
    # return WordResponse(detail="Categoria Criada com sucesso!")


# READ BY USER
@router.get("/words")
async def get_user_words(
    user_id: str,
    category_id: str,
    db: AsyncSession = Depends(get_db)
):
    return await WordService.get_by_user(user_id, category_id, db)
