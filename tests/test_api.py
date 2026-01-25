from uuid import uuid4
from parts.models import Part, Category, Token, TokenEntity
from parts.db import _insert, _get
from parts.api import (
    _get_or_create_token,
    create_token_relation,
    _tokenize,
    create_part,
)
from sqlmodel import select


def test_create_and_get_category(session):
    category = _insert(session, Category(identifier="Electronics"))
    assert category.id is not None
    assert category.identifier == "Electronics"

    fetched_category = _get(session, Category, category.id)
    assert fetched_category.identifier == "Electronics"


def test_create_and_get_part(session):
    category = _insert(session, Category(identifier="Mechanics"))

    part_uuid = uuid4()
    part = _insert(
        session,
        Part(
            uuid=part_uuid,
            category_id=category.id,
            identifier="Bolt_M3",
            qty=100,
            datasheet="http://example.com/bolt.pdf",
            description="M3 Hex Bolt",
        ),
    )

    assert part.id is not None
    assert part.uuid == part_uuid
    assert part.identifier == "Bolt_M3"

    fetched_part = _get(session, Part, part.id)
    assert fetched_part.uuid == part_uuid
    assert fetched_part.category.identifier == "Mechanics"


def test_create_and_get_nested_categories(session):
    parent_category = _insert(session, Category(identifier="Electronics"))

    assert parent_category.id is not None

    assert parent_category.identifier == "Electronics"

    child_category = _insert(session, Category(identifier="Resistors", parent_id=parent_category.id))

    assert child_category.id is not None

    assert child_category.identifier == "Resistors"

    assert child_category.parent_id == parent_category.id

    # Fetch parent again to check children relationship

    fetched_parent_category = _get(session, Category, parent_category.id)

    assert len(fetched_parent_category.children) == 1

    assert fetched_parent_category.children[0].identifier == "Resistors"

    # Fetch child again to check parent relationship

    fetched_child_category = _get(session, Category, child_category.id)

    assert fetched_child_category.parent is not None

    assert fetched_child_category.parent.identifier == "Electronics"


def test_get_or_create_token(session):
    token_id = _get_or_create_token(session, "test")
    assert isinstance(token_id, int)
    token_id_2 = _get_or_create_token(session, "test")
    assert token_id == token_id_2
    token_id_3 = _get_or_create_token(session, "test2")
    assert token_id != token_id_3


def test_create_token_relation(session):
    token_id = _get_or_create_token(session, "test")
    create_token_relation(session, token_id, "test_type", "test_entity", 1)
    statement = select(TokenEntity).where(TokenEntity.token_id == token_id)
    token_entity = session.exec(statement).first()
    assert token_entity is not None
    assert token_entity.token_type == "test_type"
    assert token_entity.entity_type == "test_entity"
    assert token_entity.entity_id == 1


def test_tokenize(session):
    category = _insert(session, Category(identifier="Mechanics"))
    part = create_part(
        db=session,
        category_id=category.id,
        identifier="Bolt_M3",
        description="M3 Hex Bolt",
    )
    _tokenize(session, part)
    statement = select(Token).where(Token.word == "Bolt_M3")
    token = session.exec(statement).first()
    assert token is not None
    statement = select(TokenEntity).where(TokenEntity.token_id == token.id)
    token_entity = session.exec(statement).first()
    assert token_entity is not None
    assert token_entity.entity_type == "part"
    assert token_entity.entity_id == part.id
