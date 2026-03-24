from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel


class Word(SQLModel, table=True):
    __tablename__ = "words"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    english: str = Field(index=True)
    portuguese: str | None = None
    image_key: str | None = None
    audio_key: str | None = None
    owner_user_id: str | None = Field(default=None, index=True)

    phrases: list["Phrase"] = Relationship(back_populates="word")
    categories: list["WordCategory"] = Relationship(back_populates="word")
    users: list["UserWord"] = Relationship(back_populates="word")


class UserWord(SQLModel, table=True):
    __tablename__ = "user_words"

    user_id: str = Field(primary_key=True)
    word_id: UUID = Field(foreign_key="words.id", primary_key=True)

    word: "Word" = Relationship(back_populates="users")


class WordCategory(SQLModel, table=True):
    __tablename__ = "word_categories"

    category_id: UUID = Field(foreign_key="categories.id", primary_key=True)
    word_id: UUID = Field(foreign_key="words.id", primary_key=True)

    word: "Word" = Relationship(back_populates="categories")


class Phrase(SQLModel, table=True):
    __tablename__ = "phrases"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    text: str
    translation: str | None = None
    audio_key: str | None = None
    word_id: UUID = Field(foreign_key="words.id")

    word: Word = Relationship(back_populates="phrases")
