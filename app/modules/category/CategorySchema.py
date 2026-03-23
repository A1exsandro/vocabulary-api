from uuid import UUID

from pydantic import BaseModel, ConfigDict

class CategoryCreate(BaseModel):
    name: str
    user_id: str


class CategoryUpdate(BaseModel):
    name: str
    user_id: str


class CategoryResponse(BaseModel):
    detail: str


class CategoryDelete(BaseModel):
    user_id: str


class CategoryListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
