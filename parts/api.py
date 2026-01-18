import os
import shutil
from uuid import UUID, uuid4

from sqlmodel import Session, SQLModel, select

from parts.db import create_db_and_tables
from parts.models import Part, Category

DATASHEET_DIR = "datasheets"


def _create_datasheet_path():
    if os.path.exists(DATASHEET_DIR):
        shutil.rmtree(DATASHEET_DIR)
    os.makedirs(DATASHEET_DIR)


def init():
    create_db_and_tables()
    _create_datasheet_path()


def _insert(db: Session, obj: SQLModel):
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def _get(db: Session, model: SQLModel, item_id: int):
    return db.get(model, item_id)


def create_part(
    db: Session,
    category_id: int,
    identifier: str,
    description: str,
    qty: int = 0,
    datasheet: str = None,
):
    part = Part(
        uuid=uuid4(),
        identifier=identifier,
        qty=qty,
        description=description,
        datasheet=datasheet,
        category_id=category_id,
    )

    return _insert(db=db, obj=part)


def delete_part(db: Session, part: Part):
    db.delete(part)
    db.commit()


def create_category(db: Session, name: str, parent_id: int = None):
    category = Category(name=name, parent_id=parent_id)
    return _insert(db=db, obj=category)


def delete_category(db: Session, category: Category):
    db.delete(category)
    db.commit()


def increase_qty(db: Session, part: Part, qty: int):
    pass


def decrease_qty(db: Session, uuid: UUID, qry: int):
    pass


def get_or_create_category(
    session: Session, name: str, parent_id: int = None
) -> Category:
    statement = select(Category).where(Category.name == name)

    if parent_id is None:
        statement = statement.where(Category.parent_id is None)
    else:
        statement = statement.where(Category.parent_id == parent_id)

    category = session.exec(statement).first()

    if category:
        return category

    return api.create_category(
        db=session,
        name=name,
        parent_id=parent_id,
    )
