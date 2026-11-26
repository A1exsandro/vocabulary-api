"""Grammar cards per user (vocabulary-api#15), mirroring vocabulary-mobile#87.

Words are shared between users, so the forms and the status belong to a
user: two users can fill the same word differently. `field` follows the
standard form of the class (app/core/grammar_forms.py).
"""

from uuid import UUID

from sqlmodel import Field, SQLModel


class WordForm(SQLModel, table=True):
    __tablename__ = "word_forms"

    user_id: str = Field(primary_key=True)
    word_id: UUID = Field(foreign_key="words.id", primary_key=True)
    grammar_class_id: UUID = Field(foreign_key="grammar_classes.id", primary_key=True)
    field: str = Field(primary_key=True)
    english: str
    portuguese: str | None = None
    spanish: str | None = None


class WordGrammarStatus(SQLModel, table=True):
    __tablename__ = "word_grammar_status"

    user_id: str = Field(primary_key=True)
    word_id: UUID = Field(foreign_key="words.id", primary_key=True)
    grammar_class_id: UUID = Field(foreign_key="grammar_classes.id", primary_key=True)
    # "unverified" (by hand), "ai_generated" or "verified".
    status: str
    # ISO 8601, as the mobile app stores it.
    updated_at: str
