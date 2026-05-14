import os
import shutil
import sys
from uuid import uuid4

from sqlalchemy import and_, or_
from sqlalchemy.orm import aliased, selectinload
from sqlmodel import Session, select, SQLModel

from parts import parser
from parts.db import create_db_and_tables, db_insert, with_db
from parts.models import Part, Category
from parts.parser import TokenEntity, Token

DATASHEET_DIR = "datasheets"


def init():
    create_db_and_tables()
    _create_datasheet_path()


def _create_datasheet_path():
    if os.path.exists(DATASHEET_DIR):
        shutil.rmtree(DATASHEET_DIR)
    os.makedirs(DATASHEET_DIR)


def _get_or_create_token(db: Session, word: str) -> int:
    statement = select(Token).where(Token.word == word)
    token = db.exec(statement).first()
    if not token:
        token = db_insert(db, Token(word=word))
    return token.id


def _create_token_relation(db: Session, token_id: int, token_type: str, entity_type: str, entity_id: int):
    db_insert(
        db,
        TokenEntity(
            token_id=token_id,
            token_type=token_type,
            entity_type=entity_type,
            entity_id=str(entity_id),
        ),
    )


def tokenize(db: Session, entity: SQLModel):
    # Get of create a token from a word extracted from indexable fields.
    # These tokens allow for map user input words to database entities
    for attr in ["description", "identifier"]:
        if hasattr(entity, attr) and (prop := getattr(entity, attr)):
            for word in prop.split(" "):
                token_id = _get_or_create_token(db, word=word.lower())

                _create_token_relation(
                    db,
                    token_id=token_id,
                    token_type=attr,
                    entity_type=entity.__class__.__name__.lower(),
                    entity_id=entity.id,
                )


def get_next_legal_token_types(sentence: str):

    if legal := parser.parse(sentence).keys():
        types, subtypes = zip(*map(lambda s: s.split(":"), legal))
        return set(types), set(subtypes)
    else:
        return set(), set()

def list_categories(db, parent_id=None):
    query = select(Category)

    if parent_id:
        query = query.where(Category.parent_id == parent_id)

    return db.execute(query).scalars().all()


def create_part(db: Session, identifier: str, descript: str, qty: int = 1, cat_id: str = None, datasheet: str = None):
    part = db_insert(
        db=db,
        obj=Part(
            uuid=uuid4(),
            identifier=identifier,
            qty=qty,
            description=descript,
            datasheet=datasheet,
            category_id=cat_id,
        ),
    )

    tokenize(db, part)

    return part


def list_parts(db, category_id=None):
    parent_cat = aliased(Category)
    query = (
        select(Part)
        .options(selectinload(Part.category).selectinload(Category.parent))
        .outerjoin(Category, Part.category_id == Category.identifier)
        .outerjoin(parent_cat, Category.parent_id == parent_cat.id)
        .order_by(parent_cat.identifier, Category.identifier, Part.identifier)
    )

    if category_id:
        leaf = category_id.split("/")[-1]
        target_category = db.exec(select(Category).where(Category.identifier == leaf)).first()
        if target_category:
            query = query.where(Category.path.contains(target_category))
        else:
            query = query.where(Part.identifier.contains(leaf))

    return db.execute(query).scalars().all()


def create_category(db: Session, identifier: str, parent_id: int = None) -> Category:
    cat = db_insert(db=db, obj=Category(uuid=uuid4(), identifier=identifier, parent_id=parent_id))

    tokenize(db, cat)

    return cat


def get_or_create_category(session: Session, identifier: str, parent_id: int = None) -> Category:
    statement = select(Category).where(Category.identifier == identifier).where(Category.parent_id == parent_id)

    category = session.exec(statement).first()

    if category:
        return category

    return create_category(db=session, identifier=identifier, parent_id=parent_id)


"""
@with_session
def list(db, args):
    if not args:
        # If no category specified, list all parts

        statement = select(Part)

        return db.exec(statement).all()

    else:
        category_path = args[0].split("/")

        parent_uuid = None

        target_category = None

        for category_identifier in category_path:
            statement = (
                select(Category)
                .where(Category.identifier == category_identifier)
                .where(Category.parent_uuid == parent_uuid)
            )

            target_category = db.exec(statement).first()

            if not target_category:
                print(f"Category not found: {args[0]}")

                return

            parent_uuid = target_category.id

        # List parts directly in the target category

        statement = select(Part).where(Part.category_id == target_category.id).options(selectinload(Part.category))

        return db.exec(statement).all()


def delete_part(db: Session, part: Part):
    db.delete(part)

    db.commit()


def delete_category(db: Session, category: Category):
    db.delete(category)

    db.commit()


@with_session
def find_token(db, string: str):
    return db.exec(select(Token).where(Token.word.contains(string)).order_by(Token.word)).all()

"""


def delete_part(db: Session, part: Part):
    db.delete(part)
    db.commit()


def delete_category(db: Session, category: Category):
    db.delete(category)
    db.commit()


@with_db
def match_token(db, string: str, token_types=None, entity_types=None):
    token_types = token_types or []

    entity_types = entity_types or []

    def _filter(q):
        return q.where(
            and_(
                or_(*[TokenEntity.token_type == t for t in token_types]),
                or_(*[TokenEntity.entity_type == t for t in entity_types]),
            )
        )

    query = select(Token, TokenEntity).where(Token.word.contains(string)).join(TokenEntity)

    query = _filter(query)

    tokens = db.exec(query.order_by(TokenEntity.entity_type, TokenEntity.token_type)).all()

    if not tokens:
        return []

    entity_types = {}

    found = []

    for token, token_entity in tokens:
        entity_types.setdefault(token_entity.entity_type, []).append(token_entity)

    for cls_name, entities in entity_types.items():
        cls = getattr(sys.modules[__name__], cls_name.capitalize())

        found += db.exec(select(cls).where(getattr(cls, "id").in_([ent.entity_id for ent in entities]))).all()

    return found
