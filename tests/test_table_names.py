"""Guards table names that existing databases depend on."""

import unittest

from app.modules.category.CategoryModel import Category, UserCategory


class TableNameTest(unittest.TestCase):
    def test_category_tables(self):
        self.assertEqual(Category.__tablename__, "categories")
        self.assertEqual(UserCategory.__tablename__, "user_categories")


if __name__ == "__main__":
    unittest.main()
