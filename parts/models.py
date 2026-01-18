from typing import List, Optional
from uuid import UUID, uuid4
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine
from sqlalchemy import CHAR, TypeDecorator, Column
import uuid


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
    name: str = Field(index=True, unique=True, nullable=False)
    parent_id: Optional[int] = Field(default=None, foreign_key="category.id")

    parent: Optional["Category"] = Relationship(
        back_populates="children", sa_relationship_kwargs={"remote_side": "Category.id"}
    )
    children: List["Category"] = Relationship(back_populates="parent")
    parts: List["Part"] = Relationship(back_populates="category")


class Part(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: UUID = Field(
        default_factory=uuid4, sa_column=Column(GUID, nullable=False, unique=True)
    )
    identifier: str = Field(index=True, unique=True, nullable=False)
    qty: Optional[int] = 0
    datasheet: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = Field(default=None, foreign_key="category.id")

    category: Optional[Category] = Relationship(back_populates="parts")
