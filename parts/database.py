from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker, declarative_base

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
    uuid = Column(String, nullable=False, unique=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    identifier = Column(String)
    qty = Column(Integer)
    datasheet = Column(String)
    description = Column(String)
    category = relationship("Category", back_populates="parts")


def create_tables():
    Base.metadata.create_all(engine)
