from uuid import UUID

from pydantic import BaseModel

class WordCreate(BaseModel):
    english: str
    user_id: str
    category_id: str


class WordUpdate(BaseModel):
    english: str
    user_id: str
    category_id: UUID


class WordDelete(BaseModel):
    user_id: str


class WordResponse(BaseModel):
    detail: str
