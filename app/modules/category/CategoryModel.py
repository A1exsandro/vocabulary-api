from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4


class Category(SQLModel, table=True):
    __tablename__ = "categories"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(index=True, unique=True)

    users: list["UserCategory"] = Relationship(back_populates="category")


class UserCategory(SQLModel, table=True):
    __tablename__ = "user_cotegories"

    user_id: str = Field(primary_key=True)

    category_id: UUID = Field(
        foreign_key="categories.id",
        primary_key=True
    )

    category: "Category" = Relationship(back_populates="users")
    