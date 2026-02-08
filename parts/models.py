from typing import List, Optional, ClassVar
from uuid import UUID, uuid4

from sqlalchemy.ext.hybrid import hybrid_property, Comparator
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import CHAR, TypeDecorator, Column, select
import uuid

from sqlalchemy.orm import aliased


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


class AncestorComparator(Comparator):
    def operate(self, op, other, **kwargs):
        if op.__name__ != "contains_op":  # Corrected from "contains"
            raise NotImplementedError()

        ancestor_id = other.id if hasattr(other, "id") else other

        cls = self.__clause_element__()  # This is the Category class

        descendants_cte = (
            select(cls.id.label("id")).where(cls.id == ancestor_id).cte(name="descendants_cte", recursive=True)
        )

        category_alias = aliased(cls, name="category_alias")
        descendants_cte = descendants_cte.union_all(
            select(category_alias.id).join(descendants_cte, category_alias.parent_id == descendants_cte.c.id)
        )

        return self.__clause_element__().id.in_(select(descendants_cte.c.id))


class Category(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: UUID = Field(default_factory=uuid4, sa_column=Column(GUID, nullable=False, unique=True))
    identifier: str = Field(index=True, unique=True, nullable=False)
    parent_id: Optional[int] = Field(default=None, foreign_key="category.id")

    parent: Optional["Category"] = Relationship(
        back_populates="children", sa_relationship_kwargs={"remote_side": "Category.id"}
    )
    children: List["Category"] = Relationship(back_populates="parent")
    parts: List["Part"] = Relationship(back_populates="category")

    path: ClassVar[List["Category"]]

    @hybrid_property
    def path(self):
        """Returns the path of ancestor categories as a list, from the root to the current category."""
        path_list = []
        curr = self
        while curr:
            path_list.insert(0, curr)
            curr = curr.parent
        return path_list

    @path.comparator
    def path(cls):
        return AncestorComparator(cls)


class Part(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: UUID = Field(default_factory=uuid4, sa_column=Column(GUID, nullable=False, unique=True))
    identifier: str = Field(index=True, unique=True, nullable=False)
    qty: Optional[int] = 0
    datasheet: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[str] = Field(default=None, foreign_key="category.identifier", nullable=True)
    category: Optional[Category] = Relationship(back_populates="parts")
