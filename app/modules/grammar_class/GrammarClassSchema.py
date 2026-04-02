from pydantic import BaseModel


class GrammarClassListItem(BaseModel):
    slug: str
    name: str
    description: str | None = None
    wordsCount: int = 0
