from pydantic import BaseModel


class UserCardItem(BaseModel):
    id: str
    name: str
    username: str | None = None
    email: str | None = None
    enabled: bool = True
    categoriesCount: int = 0
    wordsCount: int = 0
    textsCount: int = 0
