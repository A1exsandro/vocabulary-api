from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.audio_generator import AudioGenerator
from app.core.config import commit_rollback
from app.core.exceptions import DomainError, NotFoundError
from app.modules.text.TextRepository import TextRepository
from app.modules.text.TextSchema import TextResponse, TextUpdate


class UpdateTextUseCase:
    def __init__(self, db: AsyncSession, audio_generator: AudioGenerator):
        self.db = db
        self.repository = TextRepository(db)
        self.audio_generator = audio_generator

    async def execute(self, text_id: UUID, payload: TextUpdate) -> TextResponse:
        entry = await self.repository.get_by_id(text_id)
        if not entry or entry.user_id != payload.user_id:
            raise NotFoundError("Texto nao encontrado para este usuario.")

        english = payload.english.strip()
        portuguese = payload.portuguese.strip()

        if not english or not portuguese:
            raise DomainError("Texto em ingles e traducao em portugues sao obrigatorios.")

        audio_key = await self.audio_generator.generate(english)
        await self.repository.update_text(entry, english, portuguese, audio_key)
        await commit_rollback(self.db)
        return TextResponse(detail="Texto atualizado com sucesso.")
