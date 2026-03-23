from __future__ import annotations

from typing import Any


def normalize_sentences(raw_sentences: Any) -> list[dict[str, str | None]]:
    """Normalize sentence payloads into [{'english': str, 'portuguese': str | None}].

    Accepts both legacy list[str] and new list[dict].
    """
    normalized: list[dict[str, str | None]] = []

    if not isinstance(raw_sentences, list):
        return normalized

    for sentence in raw_sentences:
        if isinstance(sentence, str):
            text = sentence.strip()
            if text:
                normalized.append({"english": text, "portuguese": None})
            continue

        if isinstance(sentence, dict):
            english = (
                sentence.get("english")
                or sentence.get("text")
                or sentence.get("sentence")
                or ""
            )
            portuguese = sentence.get("portuguese") or sentence.get("translation")

            if isinstance(english, str):
                english = english.strip()
            else:
                english = ""

            if isinstance(portuguese, str):
                portuguese = portuguese.strip() or None
            else:
                portuguese = None

            if english:
                normalized.append({"english": english, "portuguese": portuguese})

    return normalized
