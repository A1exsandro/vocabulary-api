from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.audio_generator import AudioGenerator
from app.application.ports.image_generator import ImageGenerator
from app.application.ports.vocabulary_enricher import VocabularyEnricher
from app.application.word.use_cases.sentence_payload import normalize_sentences
from app.core.config import commit_rollback
from app.modules.word.WordRepositoy import WordRepository
from app.modules.word.WordSchema import WordCreate, WordResponse


class CreateWordUseCase:
    def __init__(
        self,
        db: AsyncSession,
        vocabulary_enricher: VocabularyEnricher,
        audio_generator: AudioGenerator,
        image_generator: ImageGenerator,
    ):
        self.db = db
        self.repository = WordRepository(db)
        self.vocabulary_enricher = vocabulary_enricher
        self.audio_generator = audio_generator
        self.image_generator = image_generator

    async def execute(self, create_form: WordCreate):
        word = await self.repository.get_by_english(create_form.english)
        if word and await self.repository.exists_user_word(create_form.user_id, word.id):
            return WordResponse(detail="Essa palavra já está na sua lista.")

        if not word:
            phrases_data = self.vocabulary_enricher.enrich(create_form.english)
            correct_word = phrases_data["correct_word"]
            translation = phrases_data["translation"]
            sentences = normalize_sentences(phrases_data.get("sentences"))

            word = await self.repository.get_by_english(correct_word)
            if word and await self.repository.exists_user_word(create_form.user_id, word.id):
                return WordResponse(detail="Essa palavra já está na sua lista.")

            if word:
                await self.repository.ensure_word_category(word.id, create_form.category_id)
            else:
                image_key = await self.image_generator.generate(correct_word)
                audio_key = await self.audio_generator.generate(correct_word)

                word = await self.repository.create_word(
                    english=correct_word,
                    portuguese=translation,
                    image_key=image_key,
                    audio_key=audio_key,
                    category_id=create_form.category_id,
                )

                for sentence in sentences:
                    sentence_audio_key = await self.audio_generator.generate(sentence["english"])
                    await self.repository.create_phrase(
                        word_id=word.id,
                        text=sentence["english"],
                        translation=sentence.get("portuguese"),
                        audio_key=sentence_audio_key,
                    )

        await self.repository.link_user_word(create_form.user_id, word.id)
        await commit_rollback(self.db)
        await self.db.refresh(word)

        return word
