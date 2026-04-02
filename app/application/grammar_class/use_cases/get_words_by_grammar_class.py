import os

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.integrations.s3_client import s3_client
from app.modules.word.WordModel import GrammarClass, UserWord, Word, WordGrammarClass

S3_AUDIO_BUCKET_NAME = os.getenv("S3_AUDIO_BUCKET_NAME")
S3_IMAGE_BUCKET_NAME = os.getenv("S3_IMAGE_BUCKET_NAME")


def _build_presigned_url(bucket_name: str | None, key: str | None) -> str | None:
    if not bucket_name or not key:
        return None

    return s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket_name, "Key": key},
        ExpiresIn=600,
    )


class GetWordsByGrammarClassUseCase:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def execute(self, user_id: str, slug: str):
        stmt = (
            select(Word)
            .join(WordGrammarClass)
            .join(GrammarClass)
            .outerjoin(UserWord)
            .where(GrammarClass.slug == slug)
            .where((UserWord.user_id == user_id) | (Word.owner_user_id.is_(None)))
            .options(selectinload(Word.phrases), selectinload(Word.grammar_classes).selectinload(WordGrammarClass.grammar_class))
        )

        result = await self.db.execute(stmt)
        words = result.scalars().unique().all()

        response = []
        for word in words:
            image_url = _build_presigned_url(S3_IMAGE_BUCKET_NAME, word.image_key)
            audio_url = _build_presigned_url(S3_AUDIO_BUCKET_NAME, word.audio_key)

            phrases = []
            for phrase in word.phrases or []:
                phrase_audio_url = _build_presigned_url(S3_AUDIO_BUCKET_NAME, phrase.audio_key)

                phrases.append(
                    {
                        "id": phrase.id,
                        "text": phrase.text,
                        "translation": phrase.translation,
                        "audioUrl": phrase_audio_url,
                    }
                )

            response.append(
                {
                    "id": word.id,
                    "userId": user_id,
                    "english": word.english,
                    "portuguese": word.portuguese,
                    "phrases": phrases,
                    "audioUrl": audio_url,
                    "imageUrl": image_url,
                    "grammarClasses": [
                        {
                            "slug": grammar_link.grammar_class.slug,
                            "name": grammar_link.grammar_class.name,
                        }
                        for grammar_link in word.grammar_classes or []
                        if grammar_link.grammar_class
                    ],
                }
            )

        return response
