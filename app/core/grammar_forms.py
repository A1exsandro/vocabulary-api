"""The standard form of each grammar class (vocabulary-api#15).

Mirrors vocabulary-mobile `src/db/grammarForms.ts`: every word of a class
has the same fields. The word itself is the base form, so it is not a field.
A text field holds English, Portuguese and Spanish; a choice is stored in
English only, from its options.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class FormField:
    key: str
    options: tuple[str, ...] | None = None  # None: a text field

    @property
    def is_choice(self) -> bool:
        return self.options is not None


def _text(*keys: str) -> list[FormField]:
    return [FormField(key) for key in keys]


_USAGE = _text("usage", "example")

GRAMMAR_FORMS: dict[str, list[FormField]] = {
    "verbos": [
        *_text("third_person", "past", "past_participle", "ing"),
        FormField("regularity", ("regular", "irregular")),
    ],
    "substantivos": [
        *_text("plural"),
        FormField("countability", ("countable", "uncountable", "both")),
        *_text("gender", "derivations"),
    ],
    "adjetivos": _text("comparative", "superlative", "adverb", "opposite"),
    # Most adverbs have no degrees, so every adverb also has its usage and an example.
    "adverbios": _text("comparative", "superlative", "source", "usage", "example"),
    "pronomes": _text("subject", "object", "possessive_adjective", "possessive_pronoun", "reflexive"),
    "preposicoes": _USAGE,
    "conjuncoes": _USAGE,
    "interjeicoes": _USAGE,
    "artigos": _USAGE,
    "numerais": _text("digits", "ordinal", "multiplicative", "fractional"),
}

GRAMMAR_STATUSES = ("unverified", "ai_generated", "verified")


def _clean(value: str | None) -> str | None:
    value = (value or "").strip()
    return value or None


def normalize_forms(slug: str, forms: dict[str, dict]) -> tuple[dict[str, dict], str | None]:
    """Trims every value and drops empty fields, so a card can be partly filled.

    Returns the clean forms and the problem, if any: an unknown field, a
    translation without its English, or a choice outside its options.
    """
    fields = {field.key: field for field in GRAMMAR_FORMS.get(slug, [])}
    result: dict[str, dict] = {}
    for key, value in forms.items():
        field = fields.get(key)
        if field is None:
            return result, f"Campo desconhecido: {key}."
        english = _clean(value.get("english"))
        if field.is_choice:
            if english is None:
                continue
            if english not in field.options:
                return result, f"Escolha uma das opções de {key}: {', '.join(field.options)}."
            result[key] = {"english": english, "portuguese": None, "spanish": None}
            continue
        portuguese = _clean(value.get("portuguese"))
        spanish = _clean(value.get("spanish"))
        if english is None and portuguese is None and spanish is None:
            continue
        if english is None:
            return result, f"Preencha o inglês de {key} antes das traduções."
        result[key] = {"english": english, "portuguese": portuguese, "spanish": spanish}
    return result, None
