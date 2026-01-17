from sqlmodel import Session, SQLModel
from parts.models import Part, Category


def create_item(db: Session, item: SQLModel):
    db.add(item)

    db.commit()

    db.refresh(item)

    return item


def get_item(db: Session, model: SQLModel, item_id: int):
    return db.get(model, item_id)
