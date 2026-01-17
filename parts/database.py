from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.types import TypeDecorator, CHAR
import uuid


class GUID(TypeDecorator):
    """Platform-independent GUID type. Stores UUID as char(32), converts to UUID.UUID python objects."""

    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        else:
            return value.hex  # Store as 32-character hex string

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            return uuid.UUID(value)  # Convert back to uuid.UUID object


engine = create_engine("sqlite:///parts.db")
Session = sessionmaker(bind=engine)
Base = declarative_base()


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    parts = relationship("Part", back_populates="category")


class Part(Base):
    __tablename__ = "parts"
    id = Column(Integer, primary_key=True)
    uuid = Column(GUID, nullable=False, unique=True)  # Use the custom GUID type
    category_id = Column(Integer, ForeignKey("categories.id"))
    identifier = Column(String)
    qty = Column(Integer)
    datasheet = Column(String)
    description = Column(String)
    category = relationship("Category", back_populates="parts")


def create_tables():
    Base.metadata.create_all(engine)
