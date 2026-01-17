import unittest
import os
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from parts.database import Base, create_tables, Part, Category
from parts.schemas import PartCreate, CategoryCreate
from parts.api import create_category, create_part, get_part, get_category


class TestCRUD(unittest.TestCase):
    def setUp(self):
        self.db_file = "test_parts.db"
        if os.path.exists(self.db_file):
            os.remove(self.db_file)

        self.engine = create_engine(f"sqlite:///{self.db_file}")
        Base.metadata.create_all(bind=self.engine)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def tearDown(self):
        if os.path.exists(self.db_file):
            os.remove(self.db_file)

    def test_create_and_get_category(self):
        db = self.SessionLocal()
        category_in = CategoryCreate(name="Electronics")
        category = create_category(db, category_in)
        self.assertIsNotNone(category.id)
        self.assertEqual(category.name, "Electronics")

        fetched_category = get_category(db, category.id)
        self.assertEqual(fetched_category.name, "Electronics")
        db.close()

    def test_create_and_get_part(self):
        db = self.SessionLocal()
        category_in = CategoryCreate(name="Mechanics")
        category = create_category(db, category_in)

        part_uuid = uuid4()
        part_in = PartCreate(
            uuid=part_uuid,
            category_id=category.id,
            identifier="Bolt_M3",
            qty=100,
            datasheet="http://example.com/bolt.pdf",
            description="M3 Hex Bolt",
        )
        part = create_part(db, part_in)

        self.assertIsNotNone(part.id)
        self.assertEqual(part.uuid, part_uuid)
        self.assertEqual(part.identifier, "Bolt_M3")

        fetched_part = get_part(db, part.id)
        self.assertEqual(fetched_part.uuid, part_uuid)
        self.assertEqual(fetched_part.category.name, "Mechanics")
        db.close()


if __name__ == "__main__":
    unittest.main()
