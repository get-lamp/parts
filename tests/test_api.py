from parts import api
from . import data


def test_get_next_legal_token_types():
    nxt = api.get_next_legal_token_types("C")


def test_list_categories(session):
    categories = api.list_categories(session)
    assert len(categories) == len(data.CATEGORIES)
    assert [c.identifier for c in categories] == [d[data.IDENTIFIER] for d in data.CATEGORIES]

    lookup = {c.identifier: c for c in categories}

    # test sub-categories
    for category, parent in data.CATEGORIES:
        if parent:
            assert len(children := api.list_categories(session, lookup[parent].id)) > 0

            for child in children:
                # test parent relationship
                assert child.parent.identifier == parent
                # test children relationship
                assert len(child.parent.children) > 0


def test_list_parts(session):
    parts = api.list_parts(session)
    assert len(parts) == len(data.PARTS)
    assert len(api.list_parts(session, category_id="gates")) == 2


def test_category_path(session):
    from parts.models import Category
    from sqlmodel import select

    # Create a category hierarchy
    root = api.create_category(db=session, identifier="root")
    child = api.create_category(db=session, identifier="child", parent_id=root.id)
    grandchild = api.create_category(db=session, identifier="grandchild", parent_id=child.id)

    session.commit()
    session.refresh(root)
    session.refresh(child)
    session.refresh(grandchild)

    # Test the python property
    assert grandchild.path == [root, child, grandchild]
    assert child.path == [root, child]
    assert root.path == [root]

    # Test the query expression
    descendants_of_root = session.exec(select(Category).where(Category.path.contains(root))).all()
    assert grandchild in descendants_of_root
    assert child in descendants_of_root
    assert root in descendants_of_root

    descendants_of_child = session.exec(select(Category).where(Category.path.contains(child))).all()
    assert grandchild in descendants_of_child
    assert child in descendants_of_child
    assert root not in descendants_of_child
