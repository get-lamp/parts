import unittest
from uuid import uuid4
from parts.schemas import Category, CategoryCreate, Part, PartCreate


class TestSchemas(unittest.TestCase):
    def test_category_create(self):
        category_data = {"name": "Resistors"}
        category = CategoryCreate(**category_data)
        self.assertEqual(category.name, "Resistors")

    def test_category_model(self):
        category_data = {"id": 1, "name": "Capacitors"}
        category = Category(**category_data)
        self.assertEqual(category.id, 1)
        self.assertEqual(category.name, "Capacitors")

    def test_part_create(self):
        part_data = {
            "uuid": str(uuid4()),
            "category_id": 1,
            "identifier": "100R",
            "qty": 500,
            "datasheet": "http://example.com/100r.pdf",
            "description": "1/4W Carbon Film Resistor",
        }
        part = PartCreate(**part_data)
        self.assertEqual(str(part.uuid), part_data["uuid"])
        self.assertEqual(part.category_id, 1)

    def test_part_model(self):
        part_data = {
            "id": 1,
            "uuid": str(uuid4()),
            "category_id": 1,
            "identifier": "10k",
            "qty": 200,
            "datasheet": "http://example.com/10k.pdf",
            "description": "SMD Resistor",
        }
        part = Part(**part_data)
        self.assertEqual(part.id, 1)
        self.assertEqual(str(part.uuid), part_data["uuid"])


if __name__ == "__main__":
    unittest.main()
