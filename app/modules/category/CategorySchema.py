from pydantic import BaseModel

class CategoryCreate(BaseModel):
    name: str


class CategoryResponse(BaseModel):
    # id: str
    # name: str
    detail: str