from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TextGenerateRequest(BaseModel):
    user_id: str
    topic: str


class TextManualCreate(BaseModel):
    user_id: str
    english: str
    portuguese: str


class TextUpdate(BaseModel):
    user_id: str
    english: str
    portuguese: str


class TextDelete(BaseModel):
    user_id: str


class TextResponse(BaseModel):
    detail: str


class TextListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    userId: str
    english: str
    portuguese: str
    audioUrl: str | None = None
