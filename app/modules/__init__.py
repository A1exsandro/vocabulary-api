from fastapi import APIRouter

router = APIRouter()

from app.modules.category.category_router import router as category_router


router.include_router(category_router)
