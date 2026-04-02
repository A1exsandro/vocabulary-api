from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.audio_generator import AudioGenerator
from app.application.ports.image_generator import ImageGenerator
from app.application.ports.vocabulary_enricher import VocabularyEnricher
from app.application.word.use_cases.sentence_payload import normalize_sentences
from app.core.config import commit_rollback
from app.core.grammar_class_data import GRAMMAR_CLASSES
from app.core.text_normalization import to_title_label
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

    def _resolve_grammar_class_slugs(self, phrases_data: dict, create_form: WordCreate) -> list[str]:
        if not create_form.use_ai_grammar_classification:
            return create_form.grammar_class_slugs

        allowed_slugs = {item["slug"] for item in GRAMMAR_CLASSES}
        grammar_class_slug = (phrases_data.get("grammar_class_slug") or "").strip().lower()
        return [grammar_class_slug] if grammar_class_slug in allowed_slugs else []

    async def execute(self, create_form: WordCreate):
        requested_word = create_form.english.strip()
        word = await self.repository.get_user_word_by_english(create_form.user_id, requested_word)
        if word:
            return WordResponse(detail="Essa palavra já está na sua lista.")

        phrases_data = self.vocabulary_enricher.enrich(requested_word)
        correct_word = to_title_label(phrases_data["correct_word"])
        translation = phrases_data["translation"]
        sentences = normalize_sentences(phrases_data.get("sentences"))
        grammar_class_slugs = self._resolve_grammar_class_slugs(phrases_data, create_form)

        existing_user_word = await self.repository.get_user_word_by_english(create_form.user_id, correct_word)
        if existing_user_word:
            return WordResponse(detail="Essa palavra já está na sua lista.")

        shareable_word = await self.repository.get_shareable_word_by_english(correct_word)
        if shareable_word:
            await self.repository.ensure_word_category(shareable_word.id, create_form.category_id)
            await self.repository.link_user_word(create_form.user_id, shareable_word.id)
            await self.repository.replace_word_grammar_classes(shareable_word.id, grammar_class_slugs)
            await commit_rollback(self.db)
            return WordResponse(detail="Palavra criada com sucesso.")

        image_key = await self.image_generator.generate(correct_word)
        audio_key = await self.audio_generator.generate(correct_word)

        word = await self.repository.create_word(
            english=correct_word,
            portuguese=translation,
            image_key=image_key,
            audio_key=audio_key,
            category_id=create_form.category_id,
            owner_user_id=None,
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
        await self.repository.replace_word_grammar_classes(word.id, grammar_class_slugs)
        await commit_rollback(self.db)
        await self.db.refresh(word)

        return WordResponse(detail="Palavra criada com sucesso.")
