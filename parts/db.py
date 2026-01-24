from sqlmodel import create_engine, SQLModel, Session
import functools

SQLITE_FILE_NAME = "parts.db"
SQLITE_URL = f"sqlite:///{SQLITE_FILE_NAME}"

engine = create_engine(SQLITE_URL, echo=False)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def with_session(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with Session(engine) as session:
            return func(session, *args, **kwargs)

    return wrapper


def _insert(db: Session, obj: SQLModel):
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def _get(db: Session, model: SQLModel, item_id: int):
    return db.get(model, item_id)
