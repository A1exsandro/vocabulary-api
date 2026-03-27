from fastapi import APIRouter

router = APIRouter()

from app.modules.category.category_router import router as category_router
from app.modules.text.text_router import router as text_router
from app.modules.user.user_router import router as user_router
from app.modules.word.word_router import router as word_router

router.include_router(category_router)
router.include_router(word_router)
router.include_router(text_router)
router.include_router(user_router)
