from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.application.providers import get_vocabulary_enricher
from app.application.category.use_cases.create_category import CreateCategoryUseCase
from app.application.category.use_cases.delete_category import DeleteCategoryUseCase
from app.application.category.use_cases.get_categories_by_user import GetCategoriesByUserUseCase
from app.application.category.use_cases.update_category import UpdateCategoryUseCase
from app.core.config import get_db

from app.modules.category.CategorySchema import (
    CategoryCreate,
    CategoryDelete,
    CategoryListItem,
    CategoryResponse,
    CategoryUpdate,
)

router = APIRouter(
    prefix="/api/vocabulary/category",
    tags=['category']
)

# CREATE
@router.post("", response_model=CategoryResponse, response_model_exclude_none=True)
async def create_category(
    create_form: CategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    return await CreateCategoryUseCase(db, get_vocabulary_enricher()).execute(create_form)


@router.put("/{category_id}", response_model=CategoryResponse, response_model_exclude_none=True)
async def update_category(
    category_id: UUID,
    update_form: CategoryUpdate,
    db: AsyncSession = Depends(get_db)
):
    return await UpdateCategoryUseCase(db, get_vocabulary_enricher()).execute(category_id, update_form)


@router.delete("/{category_id}", response_model=CategoryResponse, response_model_exclude_none=True)
async def delete_category(
    category_id: UUID,
    delete_form: CategoryDelete,
    db: AsyncSession = Depends(get_db)
):
    return await DeleteCategoryUseCase(db).execute(category_id, delete_form)


# READ BY USER
@router.get("/categories_by_user", response_model=list[CategoryListItem])
async def get_user_categories(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    return await GetCategoriesByUserUseCase(db).execute(user_id)
