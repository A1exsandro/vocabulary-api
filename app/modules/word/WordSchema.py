from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


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


class PhraseImportItem(BaseModel):
    english: str
    portuguese: str


class WordImportItem(BaseModel):
    english: str
    portuguese: str
    sentences: list[PhraseImportItem] = Field(default_factory=list)


class WordImportRequest(BaseModel):
    schema_version: Literal["1.0"] = "1.0"
    user_id: str
    category_id: UUID
    mode: Literal["skip", "update", "error"] = "skip"
    items: list[WordImportItem]


class WordImportError(BaseModel):
    index: int
    english: str
    reason: str


class WordImportResponse(BaseModel):
    total: int
    created: int
    linked: int
    updated: int
    skipped: int
    failed: int
    errors: list[WordImportError] = Field(default_factory=list)
