from sqlmodel import create_engine, SQLModel, Session
from typing import Generator
import functools

sqlite_file_name = "parts.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def with_session(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with Session(engine) as session:
            return func(session, *args, **kwargs)

    return wrapper
