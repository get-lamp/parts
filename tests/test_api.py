from uuid import uuid4
from parts.models import Part, Category
from parts.api import _insert, _get


def test_create_and_get_category(session):
    category_in = Category(name="Electronics")
    category = _insert(session, category_in)
    assert category.id is not None
    assert category.name == "Electronics"

    fetched_category = _get(session, Category, category.id)
    assert fetched_category.name == "Electronics"


def test_create_and_get_part(session):
    category_in = Category(name="Mechanics")
    category = _insert(session, category_in)

    part_uuid = uuid4()
    part_in = Part(
        uuid=part_uuid,
        category_id=category.id,
        identifier="Bolt_M3",
        qty=100,
        datasheet="http://example.com/bolt.pdf",
        description="M3 Hex Bolt",
    )
    part = _insert(session, part_in)

    assert part.id is not None
    assert part.uuid == part_uuid
    assert part.identifier == "Bolt_M3"

    fetched_part = _get(session, Part, part.id)
    assert fetched_part.uuid == part_uuid
    assert fetched_part.category.name == "Mechanics"


def test_create_and_get_nested_categories(session):
    parent_category_in = Category(name="Electronics")
    parent_category = _insert(session, parent_category_in)
    assert parent_category.id is not None
    assert parent_category.name == "Electronics"

    child_category_in = Category(name="Resistors", parent_id=parent_category.id)
    child_category = _insert(session, child_category_in)

    assert child_category.id is not None
    assert child_category.name == "Resistors"
    assert child_category.parent_id == parent_category.id

    # Fetch parent again to check children relationship
    fetched_parent_category = _get(session, Category, parent_category.id)
    assert len(fetched_parent_category.children) == 1
    assert fetched_parent_category.children[0].name == "Resistors"

    # Fetch child again to check parent relationship
    fetched_child_category = _get(session, Category, child_category.id)
    assert fetched_child_category.parent is not None
    assert fetched_child_category.parent.name == "Electronics"
