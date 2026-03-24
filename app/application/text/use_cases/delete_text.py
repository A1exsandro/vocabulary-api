from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import commit_rollback
from app.core.exceptions import NotFoundError
from app.modules.text.TextRepository import TextRepository
from app.modules.text.TextSchema import TextDelete, TextResponse


class DeleteTextUseCase:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = TextRepository(db)

    async def execute(self, text_id: UUID, payload: TextDelete) -> TextResponse:
        entry = await self.repository.get_by_id(text_id)
        if not entry or entry.user_id != payload.user_id:
            raise NotFoundError("Texto nao encontrado para este usuario.")

        await self.repository.delete_text(entry)
        await commit_rollback(self.db)
        return TextResponse(detail="Texto removido com sucesso.")
