from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class TextEntry(SQLModel, table=True):
    __tablename__ = "texts"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(index=True)
    english: str
    portuguese: str
    audio_key: str | None = None
