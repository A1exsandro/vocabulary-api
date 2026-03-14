from fastapi import APIRouter, Path, Query, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_db

from app.modules.category.CategorySchema import CategoryCreate, CategoryResponse
from app.modules.category.CategoryRepositoy import CategoryRepository

router = APIRouter(
    prefix="/api/vacabulary/category",
    tags=['category']
)

# CREATE
@router.post("", response_model=CategoryResponse, response_model_exclude_none=True)
async def create_marca(
    create_form: CategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    await CategoryRepository.create(create_form, db) 
    return CategoryResponse(detail="Categoria Criada com sucesso!")


# READ
@router.get('')
async def get_all_marca(
    db: AsyncSession = Depends(get_db),
    limit: int = Query(100, ge=1), 
    offset: int = Query(0, ge=0)
):
    return await CategoryRepository.get_all(db, limit=limit, offset=offset)
