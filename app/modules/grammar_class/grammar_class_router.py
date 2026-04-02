from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.grammar_class.use_cases.get_grammar_classes_by_user import GetGrammarClassesByUserUseCase
from app.application.grammar_class.use_cases.get_words_by_grammar_class import GetWordsByGrammarClassUseCase
from app.core.auth import AuthenticatedUser, ensure_same_user, require_authenticated_request
from app.core.config import get_db
from app.modules.grammar_class.GrammarClassSchema import GrammarClassListItem

router = APIRouter(prefix="/api/vocabulary/grammar-class", tags=["Grammar Class"])


@router.get("/by_user", response_model=list[GrammarClassListItem])
async def get_grammar_classes_by_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    authenticated_user: AuthenticatedUser = Depends(require_authenticated_request),
):
    ensure_same_user(authenticated_user, user_id)
    return await GetGrammarClassesByUserUseCase(db).execute(user_id)


@router.get("/{slug}/words")
async def get_words_by_grammar_class(
    slug: str,
    user_id: str,
    db: AsyncSession = Depends(get_db),
    authenticated_user: AuthenticatedUser = Depends(require_authenticated_request),
):
    ensure_same_user(authenticated_user, user_id)
    return await GetWordsByGrammarClassUseCase(db).execute(user_id, slug)
