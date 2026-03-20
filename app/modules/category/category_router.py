from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_db

from app.modules.category.CategorySchema import CategoryCreate, CategoryResponse
from app.modules.category.CategoryService import CategoryService

router = APIRouter(
    prefix="/api/vacabulary/category",
    tags=['category']
)

# CREATE
@router.post("", response_model=CategoryResponse, response_model_exclude_none=True)
async def create_category(
    create_form: CategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    return await CategoryService(db).create(create_form) 


# READ BY USER
@router.get("/categories_by_user")
async def get_user_categories(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    return await CategoryService.get_by_user(user_id, db)
