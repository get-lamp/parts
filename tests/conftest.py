import pytest
import os
from sqlmodel import Session, create_engine, SQLModel
from parts import parser as g
from . import data
from parts.api import create_category, create_part

TEST_DB_FILENAME = "test_parts.db"


@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(f"sqlite:///{TEST_DB_FILENAME}")
    SQLModel.metadata.create_all(engine)
    yield engine
    os.remove(TEST_DB_FILENAME)


@pytest.fixture()
def session(db_engine):
    with Session(db_engine) as session:
        yield session
        session.rollback()  # Rollback any changes to keep the database clean for the next test
        # Clear all data from tables after each test
        for table in reversed(SQLModel.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()


@pytest.fixture(autouse=True)
def patch_lexicon():
    original = g.LEXICON
    g.LEXICON = {
        **g.LEXICON,
        **{p[data.IDENTIFIER]: [g.PART_ID] for p in data.PARTS},
        **{c[data.IDENTIFIER]: [g.CAT_ID] for c in data.CATEGORIES},
    }

    try:
        yield
    finally:
        g.LEXICON = original


@pytest.fixture(autouse=True)
def seed(session):
    cats = {}

    for category, parent in data.CATEGORIES:
        cat = create_category(session, identifier=category, parent_id=cats[parent].id if parent else None)
        cats[cat.identifier] = cat

    for part, parent in data.PARTS:
        create_part(
            session,
            identifier=part,
            descript=f"-- {part} description --",
            category_identifier=cats[parent].identifier if parent else None,
        )

    session.commit()
