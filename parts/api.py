import os
import shutil
from uuid import UUID, uuid4

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select, SQLModel

from parts.db import create_db_and_tables, with_session, _insert
from parts.models import Part, Category, Token, TokenEntity


DATASHEET_DIR = "datasheets"


def _get_or_create_token(db: Session, word: str) -> int:
    statement = select(Token).where(Token.word == word)
    token = db.exec(statement).first()
    if not token:
        token = _insert(db, Token(word=word))
    return token.id


def create_token_relation(db: Session, token_id: int, token_type: str, entity_type: str, entity_id: int):
    _insert(
        db,
        TokenEntity(
            token_id=token_id,
            token_type=token_type,
            entity_type=entity_type,
            entity_id=str(entity_id),
        ),
    )


@with_session
def list(db, args):
    if not args:
        # If no category specified, list all parts
        statement = select(Part)
        return db.exec(statement).all()

    else:
        category_path = args[0].split("/")
        parent_id = None
        target_category = None
        for category_identifier in category_path:
            statement = (
                select(Category)
                .where(Category.identifier == category_identifier)
                .where(Category.parent_id == parent_id)
            )

            target_category = db.exec(statement).first()
            if not target_category:
                print(f"Category not found: {args[0]}")
                return
            parent_id = target_category.id

        # List parts directly in the target category
        statement = select(Part).where(Part.category_id == target_category.id).options(selectinload(Part.category))
        return db.exec(statement).all()


def _create_datasheet_path():
    if os.path.exists(DATASHEET_DIR):
        shutil.rmtree(DATASHEET_DIR)
    os.makedirs(DATASHEET_DIR)


def init():
    create_db_and_tables()
    _create_datasheet_path()


def _tokenize(db, entity: SQLModel):
    # Get of create a token from a word extracted from indexable fields.
    # These tokens allow for map user input words to database entities
    for attr in ["description", "identifier"]:
        if hasattr(entity, attr):
            for word in getattr(entity, attr).split(" "):
                token_id = _get_or_create_token(db, word=word)

                create_token_relation(
                    db,
                    token_id=token_id,
                    token_type=attr,
                    entity_type=entity.__class__.__name__.lower(),
                    entity_id=entity.id,
                )


def create_part(
    db: Session,
    category_id: int,
    identifier: str,
    description: str,
    qty: int = 0,
    datasheet: str = None,
):
    part = _insert(
        db=db,
        obj=Part(
            uuid=uuid4(),
            identifier=identifier,
            qty=qty,
            description=description,
            datasheet=datasheet,
            category_id=category_id,
        ),
    )

    _tokenize(db, part)

    return part


def delete_part(db: Session, part: Part):
    db.delete(part)
    db.commit()


def create_category(db: Session, identifier: str, parent_id: int = None):
    cat = _insert(db=db, obj=Category(identifier=identifier, parent_id=parent_id))
    _tokenize(db, cat)
    return cat


def delete_category(db: Session, category: Category):
    db.delete(category)
    db.commit()


def get_or_create_category(session: Session, identifier: str, parent_id: int = None) -> Category:
    statement = select(Category).where(Category.identifier == identifier).where(Category.parent_id == parent_id)
    category = session.exec(statement).first()

    if category:
        return category

    return create_category(db=session, identifier=identifier, parent_id=parent_id)
