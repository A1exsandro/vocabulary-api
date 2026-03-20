import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.modules.word.WordModel import Word, UserWord, WordCategory
from app.modules.word.WordRepositoy import WordRepository
from app.modules.word.WordSchema import WordCreate, WordResponse
from app.integrations.s3_client import s3_client

from app.integrations.openrouter_client import generate_sentences
from app.services.audio_service import AudioService
from app.services.image_service import ImageService

# ENV
S3_ENDPOINT = os.getenv("S3_ENDPOINT")
S3_AUDIO_BUCKET_NAME = os.getenv("S3_AUDIO_BUCKET_NAME")
S3_IMAGE_BUCKET_NAME = os.getenv("S3_IMAGE_BUCKET_NAME")

class WordService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = WordRepository(db)

    # CREATE
    async def create(self, create_form: WordCreate):

        # verificar se já existe
        word = await self.repository.get_by_english(create_form.english)
        if word:
            # verificar se relação user_word existe
            if await self.repository.exists_user_word(create_form.user_id, word.id):
                return WordResponse(detail="Essa palavra já está na sua lista.")


        # criar se não existir
        if not word:
            # gerar dados
            phrases_data = generate_sentences(create_form.english)
            print('------------retorno -------phrases_data-----', phrases_data)

            correct_word = phrases_data["correct_word"]
            translation = phrases_data["translation"]
            sentences = phrases_data["sentences"]

            image_key = await ImageService.generate(correct_word)
            audio_key = await AudioService.generate(correct_word)

            word = await self.repository.create_word(
                english=correct_word,
                portuguese=translation,
                image_key=image_key,
                audio_key=audio_key,
                category_id=create_form.category_id
            )

            # criar frases
            for sentence in sentences:
                audio_key = await AudioService.generate(sentence)
                await self.repository.create_phrase(word.id, sentence, audio_key)

        # vincular usuário
        await self.repository.link_user_word(create_form.user_id, word.id)

        return word


    # READ BY USER
    @staticmethod
    async def get_by_user(user_id: str, category_id: str, db: AsyncSession):

        stmt = (
            select(Word)
            .join(UserWord)
            .join(WordCategory)
            .where(UserWord.user_id == user_id, WordCategory.category_id == category_id)
            .options(selectinload(Word.phrases))
        )

        result = await db.execute(stmt)
        words = result.scalars().unique().all()

        response = []

        for word in words:

            image_url = None
            audio_url = None

            if word.image_key:
                image_url = s3_client.generate_presigned_url(
                    "get_object",
                    Params={
                        "Bucket": S3_IMAGE_BUCKET_NAME,
                        "Key": word.image_key,
                    },
                    ExpiresIn=600,
                )

            if word.audio_key:
                audio_url = s3_client.generate_presigned_url(
                    "get_object",
                    Params={
                        "Bucket": S3_AUDIO_BUCKET_NAME,
                        "Key": word.audio_key,
                    },
                    ExpiresIn=600,
                )

            # Cria um array de objeto PHRASE com url de audio pre assinada
            phrases = []
            if word.phrases:
                phrase_audio_url = ''

                for phrase in word.phrases:
                    if phrase.audio_key:
                        phrase_audio_url = s3_client.generate_presigned_url(
                            "get_object",
                            Params={
                                "Bucket": S3_AUDIO_BUCKET_NAME,
                                "Key": phrase.audio_key,
                            },
                            ExpiresIn=600,
                        )
                    
                    obj_phrase = {
                        "id": phrase.id,
                        "text": phrase.text,
                        "audioUrl": phrase_audio_url
                    }

                    phrases.append(obj_phrase)


            response.append({
                "userId": user_id,
                "english": word.english,
                "portuguese": word.portuguese,
                "phrases": phrases,
                "audioUrl": audio_url,
                "imageUrl": image_url,
            })

        return response
    