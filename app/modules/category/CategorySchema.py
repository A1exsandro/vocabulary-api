from pydantic import BaseModel

class CategoryCreate(BaseModel):
    name: str
    user_id: str


class CategoryResponse(BaseModel):
    # id: str
    # name: str
    detail: str