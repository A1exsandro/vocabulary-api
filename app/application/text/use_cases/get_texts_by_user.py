import os

from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.s3_client import s3_client
from app.modules.text.TextRepository import TextRepository
from app.modules.text.TextSchema import TextListItem

S3_AUDIO_BUCKET_NAME = os.getenv("S3_AUDIO_BUCKET_NAME")


class GetTextsByUserUseCase:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = TextRepository(db)

    async def execute(self, user_id: str) -> list[TextListItem]:
        entries = await self.repository.get_by_user(user_id)
        response: list[TextListItem] = []

        for entry in entries:
            audio_url = None
            if entry.audio_key:
                audio_url = s3_client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": S3_AUDIO_BUCKET_NAME, "Key": entry.audio_key},
                    ExpiresIn=600,
                )

            response.append(
                TextListItem(
                    id=entry.id,
                    userId=entry.user_id,
                    english=entry.english,
                    portuguese=entry.portuguese,
                    audioUrl=audio_url,
                )
            )

        return response
