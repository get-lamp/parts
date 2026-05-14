from sqlmodel import select
from parts import api
from parts.models import Part, Category
from parts.parser import Token, TokenEntity
from . import data


def test_get_next_legal_token_types():
    types, subtypes = api.get_next_legal_token_types("list")
    assert "keyword" not in types
    assert "category" in types


def test_get_next_legal_token_types_invalid():
    types, subtypes = api.get_next_legal_token_types("list nonsense")
    assert types == set()
    assert subtypes == set()


def test_list_categories(session):
    categories = api.list_categories(session)
    assert len(categories) == len(data.CATEGORIES)
    assert [c.identifier for c in categories] == [d[data.IDENTIFIER] for d in data.CATEGORIES]

    lookup = {c.identifier: c for c in categories}

    for category, parent in data.CATEGORIES:
        if parent:
            children = api.list_categories(session, lookup[parent].id)
            assert len(children) > 0
            for child in children:
                assert child.parent.identifier == parent
                assert len(child.parent.children) > 0


def test_list_parts(session):
    parts = api.list_parts(session)
    assert len(parts) == len(data.PARTS)
    assert len(api.list_parts(session, category_id="gates")) == 2


def test_list_parts_part_identifier_fallback(session):
    """When the leaf is a part identifier, not a category, list_parts should find it."""
    results = api.list_parts(session, category_id="counter/CD4029")
    identifiers = [p.identifier for p in results]
    assert "CD4029" in identifiers


def test_create_part(session):
    part = api.create_part(session, identifier="TESTPART", descript="Test description", qty=5, cat_id="counter")
    assert part.identifier == "TESTPART"
    assert part.qty == 5
    assert part.description == "Test description"
    assert part.category_id == "counter"

    # Verify it was persisted
    found = session.exec(select(Part).where(Part.identifier == "TESTPART")).first()
    assert found is not None


def test_create_category(session):
    cat = api.create_category(session, identifier="testcat")
    assert cat.identifier == "testcat"
    assert cat.parent_id is None

    child = api.create_category(session, identifier="childcat", parent_id=cat.id)
    assert child.parent_id == cat.id


def test_get_or_create_category_existing(session):
    cat1 = api.get_or_create_category(session, identifier="counter")
    cat2 = api.get_or_create_category(session, identifier="counter")
    assert cat1.id == cat2.id


def test_get_or_create_category_new(session):
    cat = api.get_or_create_category(session, identifier="newcat")
    assert cat.identifier == "newcat"
    assert cat.id is not None


def test_delete_part(session):
    part = session.exec(select(Part).where(Part.identifier == "CD4029")).first()
    assert part is not None
    api.delete_part(session, part)

    # Sessions are rolled back after each test, so re-fetch in this session
    deleted = session.exec(select(Part).where(Part.identifier == "CD4029")).first()
    assert deleted is None


def test_delete_category(session):
    cat = session.exec(select(Category).where(Category.identifier == "buffer")).first()
    assert cat is not None
    api.delete_category(session, cat)

    deleted = session.exec(select(Category).where(Category.identifier == "buffer")).first()
    assert deleted is None


def test_tokenize(session):
    part = session.exec(select(Part).where(Part.identifier == "N555")).first()
    assert part is not None

    # Token relations should exist from the seed fixture
    entities = session.exec(
        select(TokenEntity).where(
            TokenEntity.entity_id == str(part.id),
            TokenEntity.entity_type == "part",
        )
    ).all()
    assert len(entities) > 0


def test_match_token(session):
    results = api.match_token(session, "n555", token_types=["identifier"], entity_types=["part"])
    assert len(results) > 0
    assert any(p.identifier == "N555" for p in results)


def test_match_token_no_match(session):
    results = api.match_token(session, "nonexistent12345", token_types=["identifier"], entity_types=["part"])
    assert results == []


def test_category_path(session):
    root = api.create_category(db=session, identifier="root")
    child = api.create_category(db=session, identifier="child", parent_id=root.id)
    grandchild = api.create_category(db=session, identifier="grandchild", parent_id=child.id)

    session.commit()
    session.refresh(root)
    session.refresh(child)
    session.refresh(grandchild)

    assert grandchild.path == [root, child, grandchild]
    assert child.path == [root, child]
    assert root.path == [root]

    descendants_of_root = session.exec(select(Category).where(Category.path.contains(root))).all()
    assert grandchild in descendants_of_root
    assert child in descendants_of_root
    assert root in descendants_of_root

    descendants_of_child = session.exec(select(Category).where(Category.path.contains(child))).all()
    assert grandchild in descendants_of_child
    assert child in descendants_of_child
    assert root not in descendants_of_child
