from typing import List, Optional
from uuid import UUID, uuid4
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import CHAR, TypeDecorator, Column
import uuid

from sqlalchemy import select, literal
from sqlalchemy.orm import aliased
from sqlalchemy.orm import column_property


class GUID(TypeDecorator):
    """Platform-independent GUID type. Stores UUID as char(32), converts to UUID.UUID python objects."""

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        else:
            return value.hex  # Store as 32-character hex string

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)  # Convert back to uuid.UUID object


class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    identifier: str = Field(index=True, unique=True, nullable=False)
    parent_id: Optional[int] = Field(default=None, foreign_key="category.id")

    parent: Optional["Category"] = Relationship(
        back_populates="children", sa_relationship_kwargs={"remote_side": "Category.id"}
    )
    children: List["Category"] = Relationship(back_populates="parent")
    parts: List["Part"] = Relationship(back_populates="category")


class Part(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: UUID = Field(default_factory=uuid4, sa_column=Column(GUID, nullable=False, unique=True))
    identifier: str = Field(index=True, unique=True, nullable=False)
    qty: Optional[int] = 0
    datasheet: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = Field(default=None, foreign_key="category.id", nullable=True)

    category: Optional[Category] = Relationship(back_populates="parts")


def recursive_hierarchy(model_class):
    cat = aliased(model_class)

    category_path = (
        select(model_class.id.label("id"), model_class.identifier.label("path"))
        .where(model_class.parent_id.is_(None))
        .cte(name="category_path", recursive=True)
    )

    recursive = select(cat.id, (category_path.c.path + literal("/") + cat.identifier).label("path")).join(
        category_path, cat.parent_id == category_path.c.id
    )

    category_path = category_path.union_all(recursive)

    return column_property(select(category_path.c.path).where(category_path.c.id == Part.category_id).scalar_subquery())


Part.path = recursive_hierarchy(Category)


class Token(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    word: str = Field(index=True, unique=True, nullable=False)

    token_entities: List["TokenEntity"] = Relationship(back_populates="token")


class TokenEntity(SQLModel, table=True):
    __tablename__ = "token_entity"

    id: Optional[int] = Field(default=None, primary_key=True)
    token_id: int = Field(foreign_key="token.id")
    token_type: str
    entity_id: int
    entity_type: str

    token: Token = Relationship(back_populates="token_entities")
