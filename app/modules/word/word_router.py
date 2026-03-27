import json
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.providers import get_audio_generator, get_image_generator, get_vocabulary_enricher
from app.application.word.use_cases.create_word import CreateWordUseCase
from app.application.word.use_cases.delete_word import DeleteWordUseCase
from app.application.word.use_cases.get_words_by_user import GetWordsByUserUseCase
from app.application.word.use_cases.import_words import ImportWordsUseCase
from app.application.word.use_cases.update_word import UpdateWordUseCase
from app.core.auth import AuthenticatedUser, ensure_same_user, require_authenticated_request
from app.core.config import get_db
from app.core.exceptions import DomainError
from app.modules.word.WordSchema import (
    WordCreate,
    WordDelete,
    WordImportRequest,
    WordImportResponse,
    WordResponse,
    WordUpdate,
)

router = APIRouter(prefix="/api/vocabulary/word", tags=["Word"])


@router.post("", response_model_exclude_none=True)
async def create_word(
    create_form: WordCreate,
    db: AsyncSession = Depends(get_db),
    authenticated_user: AuthenticatedUser = Depends(require_authenticated_request),
):
    ensure_same_user(authenticated_user, create_form.user_id)
    return await CreateWordUseCase(
        db,
        get_vocabulary_enricher(),
        get_audio_generator(),
        get_image_generator(),
    ).execute(create_form)


@router.post("/import", response_model=WordImportResponse, response_model_exclude_none=True)
async def import_words(
    payload: WordImportRequest,
    db: AsyncSession = Depends(get_db),
    authenticated_user: AuthenticatedUser = Depends(require_authenticated_request),
):
    ensure_same_user(authenticated_user, payload.user_id)
    return await ImportWordsUseCase(
        db,
        get_audio_generator(),
        get_image_generator(),
    ).execute(payload)


@router.post("/import/file", response_model=WordImportResponse, response_model_exclude_none=True)
async def import_words_from_file(
    file: UploadFile = File(...),
    user_id: str | None = Form(default=None),
    category_id: str | None = Form(default=None),
    mode: str | None = Form(default=None),
    db: AsyncSession = Depends(get_db),
    authenticated_user: AuthenticatedUser = Depends(require_authenticated_request),
):
    if user_id is not None:
        ensure_same_user(authenticated_user, user_id)

    payload_dict = await _parse_import_file(file)

    if user_id is not None:
        payload_dict["user_id"] = user_id
    if category_id is not None:
        payload_dict["category_id"] = category_id
    if mode is not None:
        payload_dict["mode"] = mode

    if "schema_version" not in payload_dict:
        payload_dict["schema_version"] = "1.0"

    payload = WordImportRequest(**payload_dict)
    return await ImportWordsUseCase(
        db,
        get_audio_generator(),
        get_image_generator(),
    ).execute(payload)


@router.put("/{word_id}", response_model=WordResponse, response_model_exclude_none=True)
async def update_word(
    word_id: UUID,
    update_form: WordUpdate,
    db: AsyncSession = Depends(get_db),
    authenticated_user: AuthenticatedUser = Depends(require_authenticated_request),
):
    ensure_same_user(authenticated_user, update_form.user_id)
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
    db: AsyncSession = Depends(get_db),
    authenticated_user: AuthenticatedUser = Depends(require_authenticated_request),
):
    ensure_same_user(authenticated_user, delete_form.user_id)
    return await DeleteWordUseCase(db).execute(word_id, delete_form)


@router.get("/words")
async def get_user_words(user_id: str, category_id: str, db: AsyncSession = Depends(get_db)):
    return await GetWordsByUserUseCase(db).execute(user_id, category_id)


async def _parse_import_file(file: UploadFile) -> dict:
    filename = (file.filename or "").lower()
    raw_bytes = await file.read()

    try:
        content = raw_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise DomainError("Arquivo deve estar codificado em UTF-8.") from exc

    if filename.endswith(".json"):
        return _parse_json(content)

    if filename.endswith(".md") or filename.endswith(".markdown"):
        return _parse_markdown_json(content)

    raise DomainError("Formato inválido. Envie arquivo .json, .md ou .markdown.")


def _parse_json(content: str) -> dict:
    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise DomainError("JSON inválido no arquivo de importação.") from exc

    if not isinstance(data, dict):
        raise DomainError("O conteúdo JSON deve ser um objeto.")

    return data


def _parse_markdown_json(content: str) -> dict:
    if "```" in content:
        chunks = content.split("```")
        for chunk in chunks:
            candidate = chunk.strip()
            if not candidate:
                continue

            if candidate.lower().startswith("json"):
                candidate = candidate[4:].strip()

            try:
                return _parse_json(candidate)
            except DomainError:
                continue

    start = content.find("{")
    end = content.rfind("}")
    if start != -1 and end != -1 and start < end:
        return _parse_json(content[start : end + 1])

    raise DomainError("Markdown sem JSON válido para importação.")
