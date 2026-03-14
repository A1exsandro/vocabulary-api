from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4


class Category(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str
    user_id: str
