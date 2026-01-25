from uuid import uuid4

from sqlmodel import select

from parts import api
from parts.models import Part, Category, Token, TokenEntity


def test_create_and_get_category(session):
    category = api._insert(session, Category(identifier="Electronics"))
    assert category.id is not None
    assert category.identifier == "Electronics"

    fetched_category = api._get(session, Category, category.id)
    assert fetched_category.identifier == "Electronics"


def test_create_and_get_part(session):
    category = api._insert(session, Category(identifier="Mechanics"))

    part_uuid = uuid4()
    part = api._insert(
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

    fetched_part = api._get(session, Part, part.id)
    assert fetched_part.uuid == part_uuid
    assert fetched_part.category.identifier == "Mechanics"


def test_create_and_get_nested_categories(session):
    parent_category = api._insert(session, Category(identifier="Electronics"))

    assert parent_category.id is not None
    assert parent_category.identifier == "Electronics"

    child_category = api._insert(session, Category(identifier="Resistors", parent_id=parent_category.id))

    assert child_category.id is not None
    assert child_category.identifier == "Resistors"
    assert child_category.parent_id == parent_category.id

    # Fetch parent again to check children relationship
    fetched_parent_category = api._get(session, Category, parent_category.id)

    assert len(fetched_parent_category.children) == 1

    assert fetched_parent_category.children[0].identifier == "Resistors"

    # Fetch child again to check parent relationship

    fetched_child_category = api._get(session, Category, child_category.id)

    assert fetched_child_category.parent is not None

    assert fetched_child_category.parent.identifier == "Electronics"


def test_get_or_create_token(session):
    token_id = api._get_or_create_token(session, "test")
    assert isinstance(token_id, int)
    token_id_2 = api._get_or_create_token(session, "test")
    assert token_id == token_id_2
    token_id_3 = api._get_or_create_token(session, "test2")
    assert token_id != token_id_3


def test_create_token_relation(session):
    token_id = api._get_or_create_token(session, "test")
    api._create_token_relation(session, token_id, "test_type", "test_entity", 1)
    statement = select(TokenEntity).where(TokenEntity.token_id == token_id)
    token_entity = session.exec(statement).first()
    assert token_entity is not None
    assert token_entity.token_type == "test_type"
    assert token_entity.entity_type == "test_entity"
    assert token_entity.entity_id == 1


def test_tokenize(session):
    category = api._insert(session, Category(identifier="Mechanics"))
    part = api.create_part(
        db=session,
        category_id=category.id,
        identifier="Bolt_M3",
        description="M3 Hex Bolt",
    )
    api._tokenize(session, part)
    statement = select(Token).where(Token.word == "Bolt_M3")
    token = session.exec(statement).first()
    assert token is not None
    statement = select(TokenEntity).where(TokenEntity.token_id == token.id)
    token_entity = session.exec(statement).first()
    assert token_entity is not None
    assert token_entity.entity_type == "part"
    assert token_entity.entity_id == part.id


def test_find_token(session):
    cat_a = api._insert(session, Category(identifier="foobar foo baz qux"))
    api._tokenize(session, cat_a)

    cat_b = api._insert(session, Category(identifier="goo moo boo", parent_id=cat_a.id))
    api._tokenize(session, cat_b)

    cat_c = api._insert(session, Category(identifier='orange cat'))
    api._tokenize(session, cat_c)

    part_a = api._insert(session, Part(identifier="Bofoolt_M3", category_id=cat_b.id))
    api._tokenize(session, part_a)

    part_b = api._insert(session, Part(identifier="Foo Thing",category_id=cat_c.id))
    api._tokenize(session, part_b)

    found = api.find_token(session, 'foo')

    breakpoint()




