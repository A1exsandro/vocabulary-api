from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.audio_generator import AudioGenerator
from app.application.ports.image_generator import ImageGenerator
from app.application.ports.vocabulary_enricher import VocabularyEnricher
from app.application.word.use_cases.sentence_payload import normalize_sentences
from app.core.config import commit_rollback
from app.core.exceptions import ConflictError, NotFoundError
from app.core.grammar_class_data import GRAMMAR_CLASSES
from app.core.text_normalization import to_title_label
from app.modules.word.WordRepositoy import WordRepository
from app.modules.word.WordSchema import WordResponse, WordUpdate


class UpdateWordUseCase:
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

    def _resolve_grammar_class_slugs(self, phrases_data: dict, update_form: WordUpdate) -> list[str]:
        if not update_form.use_ai_grammar_classification:
            return update_form.grammar_class_slugs

        allowed_slugs = {item["slug"] for item in GRAMMAR_CLASSES}
        grammar_class_slug = (phrases_data.get("grammar_class_slug") or "").strip().lower()
        return [grammar_class_slug] if grammar_class_slug in allowed_slugs else []

    async def _build_word_assets(self, english: str, update_form: WordUpdate):
        phrases_data = self.vocabulary_enricher.enrich(english)
        correct_word = to_title_label(phrases_data["correct_word"])
        translation = phrases_data["translation"]
        sentences = normalize_sentences(phrases_data.get("sentences"))
        grammar_class_slugs = self._resolve_grammar_class_slugs(phrases_data, update_form)

        image_key = await self.image_generator.generate(correct_word)
        audio_key = await self.audio_generator.generate(correct_word)

        phrase_records = []
        for sentence in sentences:
            sentence_audio_key = await self.audio_generator.generate(sentence["english"])
            phrase_records.append(
                {
                    "text": sentence["english"],
                    "translation": sentence.get("portuguese"),
                    "audio_key": sentence_audio_key,
                }
            )

        return correct_word, translation, image_key, audio_key, phrase_records, grammar_class_slugs

    async def _cleanup_orphan_word(self, word_id: UUID, word) -> None:
        if await self.repository.count_user_links(word_id) > 0:
            return

        await self.repository.delete_phrases_by_word_id(word_id)
        await self.repository.delete_word_categories_by_word_id(word_id)
        await self.repository.delete_word(word)

    async def execute(self, word_id: UUID, update_form: WordUpdate) -> WordResponse:
        word = await self.repository.get_by_id(word_id)
        if not word:
            raise NotFoundError("Palavra não encontrada.")

        if not await self.repository.exists_user_word(update_form.user_id, word_id):
            raise NotFoundError("Palavra não encontrada para este usuário.")

        correct_word, translation, image_key, audio_key, phrase_records, grammar_class_slugs = await self._build_word_assets(
            update_form.english.strip(),
            update_form,
        )

        user_existing_target = await self.repository.get_user_word_by_english(update_form.user_id, correct_word)
        if user_existing_target and user_existing_target.id != word_id:
            raise ConflictError("Essa palavra já está na sua lista.")

        user_links = await self.repository.count_user_links(word_id)
        if user_links > 1:
            new_word = await self.repository.create_word(
                english=correct_word,
                portuguese=translation,
                image_key=image_key,
                audio_key=audio_key,
                category_id=update_form.category_id,
                owner_user_id=update_form.user_id,
            )
            await self.repository.replace_phrases(new_word.id, phrase_records)
            await self.repository.replace_word_grammar_classes(new_word.id, grammar_class_slugs)
            await self.repository.link_user_word(update_form.user_id, new_word.id)
            await self.repository.unlink_user_word(update_form.user_id, word_id)
            await commit_rollback(self.db)
            return WordResponse(detail="Palavra atualizada com sucesso.")

        await self.repository.update_word(
            word,
            correct_word,
            translation,
            image_key,
            audio_key,
            owner_user_id=update_form.user_id,
        )
        await self.repository.ensure_word_category(word_id, update_form.category_id)
        await self.repository.replace_phrases(word_id, phrase_records)
        await self.repository.replace_word_grammar_classes(word_id, grammar_class_slugs)
        await commit_rollback(self.db)
        await self.db.refresh(word)

        return WordResponse(detail="Palavra atualizada com sucesso.")
