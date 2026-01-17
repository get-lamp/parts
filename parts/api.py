from sqlalchemy.orm import Session
from parts.database import Part, Category
from parts.schemas import PartCreate, CategoryCreate


def create_category(db: Session, category: CategoryCreate):
    db_category = Category(name=category.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def create_part(db: Session, part: PartCreate):
    db_part = Part(**part.model_dump())
    db.add(db_part)
    db.commit()
    db.refresh(db_part)
    return db_part


def get_part(db: Session, part_id: int):
    return db.query(Part).filter(Part.id == part_id).first()


def get_category(db: Session, category_id: int):
    return db.query(Category).filter(Category.id == category_id).first()
