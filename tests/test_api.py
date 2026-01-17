import unittest
import os
from uuid import uuid4
from sqlmodel import Session, create_engine, SQLModel
from parts.models import Part, Category
from parts.api import create_item, get_item
from parts.db import create_db_and_tables, engine


class TestAPI(unittest.TestCase):
    def setUp(self):
        self.db_file = "test_parts.db"
        if os.path.exists(self.db_file):
            os.remove(self.db_file)

        self.engine = create_engine(f"sqlite:///{self.db_file}")
        SQLModel.metadata.create_all(self.engine)

    def test_create_and_get_category(self):
        with Session(self.engine) as session:
            category_in = Category(name="Electronics")
            category = create_item(session, category_in)
            self.assertIsNotNone(category.id)
            self.assertEqual(category.name, "Electronics")

            fetched_category = get_item(session, Category, category.id)
            self.assertEqual(fetched_category.name, "Electronics")

    def test_create_and_get_part(self):
        with Session(self.engine) as session:
            category_in = Category(name="Mechanics")
            category = create_item(session, category_in)

            part_uuid = uuid4()
            part_in = Part(
                uuid=part_uuid,
                category_id=category.id,
                identifier="Bolt_M3",
                qty=100,
                datasheet="http://example.com/bolt.pdf",
                description="M3 Hex Bolt",
            )
            part = create_item(session, part_in)

            self.assertIsNotNone(part.id)
            self.assertEqual(part.uuid, part_uuid)
            self.assertEqual(part.identifier, "Bolt_M3")

            fetched_part = get_item(session, Part, part.id)
            self.assertEqual(fetched_part.uuid, part_uuid)
            self.assertEqual(fetched_part.category.name, "Mechanics")

    def test_create_and_get_nested_categories(self):
        with Session(self.engine) as session:
            parent_category_in = Category(name="Electronics")
            parent_category = create_item(session, parent_category_in)
            self.assertIsNotNone(parent_category.id)
            self.assertEqual(parent_category.name, "Electronics")

            child_category_in = Category(name="Resistors", parent_id=parent_category.id)
            child_category = create_item(session, child_category_in)
            self.assertIsNotNone(child_category.id)
            self.assertEqual(child_category.name, "Resistors")
            self.assertEqual(child_category.parent_id, parent_category.id)

            # Fetch parent again to check children relationship
            fetched_parent_category = get_item(session, Category, parent_category.id)
            self.assertEqual(len(fetched_parent_category.children), 1)
            self.assertEqual(fetched_parent_category.children[0].name, "Resistors")

            # Fetch child again to check parent relationship
            fetched_child_category = get_item(session, Category, child_category.id)
            self.assertIsNotNone(fetched_child_category.parent)
            self.assertEqual(fetched_child_category.parent.name, "Electronics")


if __name__ == "__main__":
    unittest.main()
