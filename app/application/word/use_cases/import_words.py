from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError
from app.modules.word.WordRepositoy import WordRepository
from app.modules.word.WordSchema import WordImportError, WordImportItem, WordImportRequest, WordImportResponse


class ImportWordsUseCase:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = WordRepository(db)

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

    async def _import_item(self, payload: WordImportRequest, item: WordImportItem) -> str:
        english = item.english.strip().lower()
        portuguese = item.portuguese.strip()
        phrase_records = [
            {
                "text": sentence.english.strip(),
                "translation": sentence.portuguese.strip(),
                "audio_key": None,
            }
            for sentence in item.sentences
            if sentence.english.strip()
        ]

        if not english:
            raise ValueError("english vazio.")

        word = await self.repository.get_by_english(english)

        if not word:
            word = await self.repository.create_word(
                english=english,
                portuguese=portuguese,
                image_key=None,
                audio_key=None,
                category_id=payload.category_id,
            )
            await self.repository.replace_phrases(word.id, phrase_records)
            await self.repository.link_user_word(payload.user_id, word.id)
            return "created"

        user_has_word = await self.repository.exists_user_word(payload.user_id, word.id)

        if not user_has_word:
            await self.repository.ensure_word_category(word.id, payload.category_id)
            await self.repository.link_user_word(payload.user_id, word.id)
            return "linked"

        if payload.mode == "skip":
            return "skipped"

        if payload.mode == "error":
            raise ConflictError("Essa palavra já está na sua lista.")

        user_links = await self.repository.count_user_links(word.id)
        if user_links > 1:
            raise ConflictError(
                "Não foi possível atualizar porque a palavra é compartilhada por outros usuários."
            )

        await self.repository.update_word(
            word=word,
            english=english,
            portuguese=portuguese,
            image_key=word.image_key,
            audio_key=word.audio_key,
        )
        await self.repository.ensure_word_category(word.id, payload.category_id)
        await self.repository.replace_phrases(word.id, phrase_records)
        return "updated"
