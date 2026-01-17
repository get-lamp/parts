import unittest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from parts.database import create_tables, Base


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.db_file = "parts.db"
        if os.path.exists(self.db_file):
            os.remove(self.db_file)
        self.engine = create_engine(f"sqlite:///{self.db_file}")
        self.Session = sessionmaker(bind=self.engine)

    def tearDown(self):
        if os.path.exists(self.db_file):
            os.remove(self.db_file)

    def test_create_tables(self):
        create_tables()
        self.assertTrue(os.path.exists(self.db_file))

        # Create a new engine and session for the test
        engine = create_engine(f"sqlite:///{self.db_file}")
        Base.metadata.reflect(bind=engine)

        self.assertIn("parts", Base.metadata.tables)
        self.assertIn("categories", Base.metadata.tables)


if __name__ == "__main__":
    unittest.main()
