from typing import Literal

from pydantic import BaseModel, Field

GrammarStatus = Literal["unverified", "ai_generated", "verified"]


class FormTexts(BaseModel):
    english: str
    portuguese: str | None = None
    spanish: str | None = None


class FormTextsInput(BaseModel):
    english: str | None = None
    portuguese: str | None = None
    spanish: str | None = None


class GrammarFormsResponse(BaseModel):
    """A word's grammar card for one class; status is null while it has no forms."""

    wordId: str
    slug: str
    status: GrammarStatus | None = None
    forms: dict[str, FormTexts] = Field(default_factory=dict)


class GrammarFormsUpdate(BaseModel):
    """Replaces the card. Empty fields are dropped; no forms left empties the card."""

    user_id: str
    status: GrammarStatus
    forms: dict[str, FormTextsInput] = Field(default_factory=dict)
