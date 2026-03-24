from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.audio_generator import AudioGenerator
from app.core.config import commit_rollback
from app.core.exceptions import DomainError
from app.modules.text.TextRepository import TextRepository
from app.modules.text.TextSchema import TextManualCreate, TextResponse


class CreateManualTextUseCase:
    def __init__(self, db: AsyncSession, audio_generator: AudioGenerator):
        self.db = db
        self.repository = TextRepository(db)
        self.audio_generator = audio_generator

    async def execute(self, payload: TextManualCreate) -> TextResponse:
        english = payload.english.strip()
        portuguese = payload.portuguese.strip()

        if not english or not portuguese:
            raise DomainError("Texto em ingles e traducao em portugues sao obrigatorios.")

        audio_key = await self.audio_generator.generate(english)
        await self.repository.create_text(payload.user_id, english, portuguese, audio_key)
        await commit_rollback(self.db)
        return TextResponse(detail="Texto criado com sucesso.")
