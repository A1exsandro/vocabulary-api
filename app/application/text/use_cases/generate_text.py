from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.audio_generator import AudioGenerator
from app.application.ports.text_generator import TextGenerator
from app.core.config import commit_rollback
from app.core.exceptions import DomainError
from app.modules.text.TextRepository import TextRepository
from app.modules.text.TextSchema import TextGenerateRequest, TextResponse


class GenerateTextUseCase:
    def __init__(self, db: AsyncSession, text_generator: TextGenerator, audio_generator: AudioGenerator):
        self.db = db
        self.repository = TextRepository(db)
        self.text_generator = text_generator
        self.audio_generator = audio_generator

    async def execute(self, payload: TextGenerateRequest) -> TextResponse:
        topic = payload.topic.strip()
        if not topic:
            raise DomainError("Tema do texto e obrigatorio.")

        generated = self.text_generator.generate(topic)
        english = generated.get("english", "").strip()
        portuguese = generated.get("portuguese", "").strip()

        if not english or not portuguese:
            raise DomainError("Nao foi possivel gerar o texto com traducao.")

        audio_key = await self.audio_generator.generate(english)
        await self.repository.create_text(payload.user_id, english, portuguese, audio_key)
        await commit_rollback(self.db)
        return TextResponse(detail="Texto gerado com sucesso.")
