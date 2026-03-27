from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.providers import get_audio_generator, get_text_generator
from app.application.text.use_cases.create_manual_text import CreateManualTextUseCase
from app.application.text.use_cases.delete_text import DeleteTextUseCase
from app.application.text.use_cases.generate_text import GenerateTextUseCase
from app.application.text.use_cases.get_texts_by_user import GetTextsByUserUseCase
from app.application.text.use_cases.update_text import UpdateTextUseCase
from app.core.auth import AuthenticatedUser, ensure_same_user, require_authenticated_request
from app.core.config import get_db
from app.modules.text.TextSchema import TextDelete, TextGenerateRequest, TextListItem, TextManualCreate, TextResponse, TextUpdate

router = APIRouter(prefix="/api/vocabulary/text", tags=["Text"])


@router.post("/generate", response_model=TextResponse, response_model_exclude_none=True)
async def generate_text(
    payload: TextGenerateRequest,
    db: AsyncSession = Depends(get_db),
    authenticated_user: AuthenticatedUser = Depends(require_authenticated_request),
):
    ensure_same_user(authenticated_user, payload.user_id)
    return await GenerateTextUseCase(db, get_text_generator(), get_audio_generator()).execute(payload)


@router.post("/manual", response_model=TextResponse, response_model_exclude_none=True)
async def create_manual_text(
    payload: TextManualCreate,
    db: AsyncSession = Depends(get_db),
    authenticated_user: AuthenticatedUser = Depends(require_authenticated_request),
):
    ensure_same_user(authenticated_user, payload.user_id)
    return await CreateManualTextUseCase(db, get_audio_generator()).execute(payload)


@router.put("/{text_id}", response_model=TextResponse, response_model_exclude_none=True)
async def update_text(
    text_id: UUID,
    payload: TextUpdate,
    db: AsyncSession = Depends(get_db),
    authenticated_user: AuthenticatedUser = Depends(require_authenticated_request),
):
    ensure_same_user(authenticated_user, payload.user_id)
    return await UpdateTextUseCase(db, get_audio_generator()).execute(text_id, payload)


@router.get("/by_user", response_model=list[TextListItem])
async def get_texts_by_user(user_id: str, db: AsyncSession = Depends(get_db)):
    return await GetTextsByUserUseCase(db).execute(user_id)


@router.delete("/{text_id}", response_model=TextResponse, response_model_exclude_none=True)
async def delete_text(
    text_id: UUID,
    payload: TextDelete,
    db: AsyncSession = Depends(get_db),
    authenticated_user: AuthenticatedUser = Depends(require_authenticated_request),
):
    ensure_same_user(authenticated_user, payload.user_id)
    return await DeleteTextUseCase(db).execute(text_id, payload)
