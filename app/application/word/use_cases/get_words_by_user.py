import os

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.integrations.s3_client import s3_client
from app.modules.word.WordModel import Word, UserWord, WordCategory

S3_AUDIO_BUCKET_NAME = os.getenv("S3_AUDIO_BUCKET_NAME")
S3_IMAGE_BUCKET_NAME = os.getenv("S3_IMAGE_BUCKET_NAME")


class GetWordsByUserUseCase:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute(self, user_id: str, category_id: str):
        stmt = (
            select(Word)
            .join(UserWord)
            .join(WordCategory)
            .where(UserWord.user_id == user_id, WordCategory.category_id == category_id)
            .options(selectinload(Word.phrases))
        )

        result = await self.db.execute(stmt)
        words = result.scalars().unique().all()

        response = []
        for word in words:
            image_url = None
            audio_url = None

            if word.image_key:
                image_url = s3_client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": S3_IMAGE_BUCKET_NAME, "Key": word.image_key},
                    ExpiresIn=600,
                )

            if word.audio_key:
                audio_url = s3_client.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": S3_AUDIO_BUCKET_NAME, "Key": word.audio_key},
                    ExpiresIn=600,
                )

            phrases = []
            for phrase in word.phrases or []:
                phrase_audio_url = None
                if phrase.audio_key:
                    phrase_audio_url = s3_client.generate_presigned_url(
                        "get_object",
                        Params={"Bucket": S3_AUDIO_BUCKET_NAME, "Key": phrase.audio_key},
                        ExpiresIn=600,
                    )

                phrases.append(
                    {
                        "id": phrase.id,
                        "text": phrase.text,
                        "audioUrl": phrase_audio_url,
                    }
                )

            response.append(
                {
                    "userId": user_id,
                    "english": word.english,
                    "portuguese": word.portuguese,
                    "phrases": phrases,
                    "audioUrl": audio_url,
                    "imageUrl": image_url,
                }
            )

        return response
