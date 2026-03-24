from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.audio_generator import AudioGenerator
from app.application.ports.image_generator import ImageGenerator
from app.core.exceptions import ConflictError
from app.core.text_normalization import to_title_label
from app.modules.word.WordRepositoy import WordRepository
from app.modules.word.WordSchema import WordImportError, WordImportItem, WordImportRequest, WordImportResponse


class ImportWordsUseCase:
    def __init__(self, db: AsyncSession, audio_generator: AudioGenerator, image_generator: ImageGenerator):
        self.db = db
        self.repository = WordRepository(db)
        self.audio_generator = audio_generator
        self.image_generator = image_generator

    async def execute(self, payload: WordImportRequest) -> WordImportResponse:
        created = 0
        linked = 0
        updated = 0
        skipped = 0
        failed = 0
        errors: list[WordImportError] = []

        for index, item in enumerate(payload.items):
            try:
                status = await self._import_item(payload, item)
                await self.db.commit()

                if status == "created":
                    created += 1
                elif status == "linked":
                    linked += 1
                elif status == "updated":
                    updated += 1
                else:
                    skipped += 1

            except Exception as exc:  # noqa: BLE001
                await self.db.rollback()
                failed += 1
                errors.append(
                    WordImportError(
                        index=index,
                        english=item.english,
                        reason=str(exc),
                    )
                )

        return WordImportResponse(
            total=len(payload.items),
            created=created,
            linked=linked,
            updated=updated,
            skipped=skipped,
            failed=failed,
            errors=errors,
        )

    async def _build_phrase_records(self, item: WordImportItem):
        phrase_records = []
        for sentence in item.sentences:
            english = sentence.english.strip()
            if not english:
                continue

            phrase_records.append(
                {
                    "text": english,
                    "translation": sentence.portuguese.strip(),
                    "audio_key": await self.audio_generator.generate(english),
                }
            )

        return phrase_records

    async def _cleanup_orphan_word(self, word_id, word) -> None:
        if await self.repository.count_user_links(word_id) > 0:
            return

        await self.repository.delete_phrases_by_word_id(word_id)
        await self.repository.delete_word_categories_by_word_id(word_id)
        await self.repository.delete_word(word)

    async def _import_item(self, payload: WordImportRequest, item: WordImportItem) -> str:
        english = to_title_label(item.english)
        portuguese = item.portuguese.strip()
        phrase_records = await self._build_phrase_records(item)

        if not english:
            raise ValueError("english vazio.")

        user_word = await self.repository.get_user_word_by_english(payload.user_id, english)
        if not user_word:
            shareable_word = await self.repository.get_shareable_word_by_english(english)
            if shareable_word:
                await self.repository.ensure_word_category(shareable_word.id, payload.category_id)
                await self.repository.link_user_word(payload.user_id, shareable_word.id)
                return "linked"

            image_key = await self.image_generator.generate(english)
            audio_key = await self.audio_generator.generate(english)
            word = await self.repository.create_word(
                english=english,
                portuguese=portuguese,
                image_key=image_key,
                audio_key=audio_key,
                category_id=payload.category_id,
                owner_user_id=payload.user_id,
            )
            await self.repository.replace_phrases(word.id, phrase_records)
            await self.repository.link_user_word(payload.user_id, word.id)
            return "created"

        if payload.mode == "skip":
            return "skipped"

        if payload.mode == "error":
            raise ConflictError("Essa palavra já está na sua lista.")

        user_links = await self.repository.count_user_links(user_word.id)
        image_key = await self.image_generator.generate(english)
        audio_key = await self.audio_generator.generate(english)

        if user_links > 1:
            new_word = await self.repository.create_word(
                english=english,
                portuguese=portuguese,
                image_key=image_key,
                audio_key=audio_key,
                category_id=payload.category_id,
                owner_user_id=payload.user_id,
            )
            await self.repository.replace_phrases(new_word.id, phrase_records)
            await self.repository.link_user_word(payload.user_id, new_word.id)
            await self.repository.unlink_user_word(payload.user_id, user_word.id)
            return "updated"

        await self.repository.update_word(
            word=user_word,
            english=english,
            portuguese=portuguese,
            image_key=image_key,
            audio_key=audio_key,
            owner_user_id=payload.user_id,
        )
        await self.repository.ensure_word_category(user_word.id, payload.category_id)
        await self.repository.replace_phrases(user_word.id, phrase_records)
        return "updated"
