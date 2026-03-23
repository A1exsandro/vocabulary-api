from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.application.providers import get_audio_generator, get_image_generator, get_vocabulary_enricher
from app.application.word.use_cases.create_word import CreateWordUseCase
from app.application.word.use_cases.delete_word import DeleteWordUseCase
from app.application.word.use_cases.get_words_by_user import GetWordsByUserUseCase
from app.application.word.use_cases.update_word import UpdateWordUseCase
from app.core.config import get_db

from app.modules.word.WordSchema import WordCreate, WordDelete, WordResponse, WordUpdate

router = APIRouter(
    prefix="/api/vocabulary/word",
    tags=['Word']
)

# CREATE
@router.post("", response_model_exclude_none=True)
async def create_word(
    create_form: WordCreate,
    db: AsyncSession = Depends(get_db)
):
    return await CreateWordUseCase(
        db,
        get_vocabulary_enricher(),
        get_audio_generator(),
        get_image_generator(),
    ).execute(create_form)


@router.put("/{word_id}", response_model=WordResponse, response_model_exclude_none=True)
async def update_word(
    word_id: UUID,
    update_form: WordUpdate,
    db: AsyncSession = Depends(get_db)
):
    return await UpdateWordUseCase(
        db,
        get_vocabulary_enricher(),
        get_audio_generator(),
        get_image_generator(),
    ).execute(word_id, update_form)


@router.delete("/{word_id}", response_model=WordResponse, response_model_exclude_none=True)
async def delete_word(
    word_id: UUID,
    delete_form: WordDelete,
    db: AsyncSession = Depends(get_db)
):
    return await DeleteWordUseCase(db).execute(word_id, delete_form)


# READ BY USER
@router.get("/words")
async def get_user_words(
    user_id: str,
    category_id: str,
    db: AsyncSession = Depends(get_db)
):
    return await GetWordsByUserUseCase(db).execute(user_id, category_id)
