import pytest
import os
from sqlmodel import Session, create_engine, SQLModel

TEST_DB_FILENAME = "test_parts.db"


@pytest.fixture(name="session")
def session_fixture():
    TEST_DB_FILENAME = "test_parts.db"
    engine = create_engine(f"sqlite:///{TEST_DB_FILENAME}")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    os.remove(TEST_DB_FILENAME)
