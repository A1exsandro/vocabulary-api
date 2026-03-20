from pydantic import BaseModel

class WordCreate(BaseModel):
    english: str
    user_id: str
    category_id: str


class WordResponse(BaseModel):
    # id: str
    # name: str
    detail: str