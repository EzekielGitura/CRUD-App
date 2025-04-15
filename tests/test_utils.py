import unittest
from app.utils import validate_item_data, format_item_for_display, search_items, generate_slug

class TestUtils(unittest.TestCase):
    def test_validate_item_data(self):
        """Test item data validation."""
        # Valid data
        valid_data = {"name": "Test Item", "description": "This is a test item"}
        errors = validate_item_data(valid_data)
        self.assertEqual(len(errors), 0)
        
        # Missing name
        invalid_data = {"description": "This is a test item"}
        errors = validate_item_data(invalid_data)
        self.assertEqual(len(errors), 1)
        self.assertIn("Name is required", errors)
        
        # Missing description
        invalid_data = {"name": "Test Item"}
        errors = validate_item_data(invalid_data)
        self.assertEqual(len(errors), 1)
        self.assertIn("Description is required", errors)
        
        # Empty name
        invalid_data = {"name": "", "description": "This is a test item"}
        errors = validate_item_data(invalid_data)
        self.assertEqual(len(errors), 1)
        self.assertIn("Name cannot be empty", errors)
        
        # Name too long
        invalid_data = {"name": "x" * 101, "description": "This is a test item"}
        errors = validate_item_data(invalid_data)
        self.assertEqual(len(errors), 1)
        self.assertIn("Name must be less than 100 characters", errors)
    
    def test_format_item_for_display(self):
        """Test formatting item for display."""
        item = {
            "id": "12345",
            "name": "Test Item",
            "description": "This is a test item",
            "created_at": "2023-01-01T12:00:00.123456",
            "updated_at": "2023-01-02T13:00:00.123456"
        }
        
        formatted = format_item_for_display(item)
        
        self.assertEqual(formatted["created_at"], "2023-01-01 12:00:00")
        self.assertEqual(formatted["updated_at"], "2023-01-02 13:00:00")
        
        # Test with missing updated_at
        item = {
            "id": "12345",
            "name": "Test Item",
            "description": "This is a test item",
            "created_at": "2023-01-01T12:00:00.123456",
            "updated_at": None
        }
        
        formatted = format_item_for_display(item)
        self.assertEqual(formatted["updated_at"], None)
    
    def test_search_items(self):
        """Test searching items."""
        items = [
            {"name": "Apple", "description": "A fruit"},
            {"name": "Banana", "description": "A yellow fruit"},
            {"name": "Orange", "description": "A citrus fruit"}
        ]
        
        # Search by name
        results = search_items(items, "apple")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Apple")
        
        # Search by description
        results = search_items(items, "citrus")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Orange")
        
        # Search with multiple matches
        results = search_items(items, "fruit")
        self.assertEqual(len(results), 3)
        
        # Search with no matches
        results = search_items(items, "grape")
        self.assertEqual(len(results), 0)
        
        # Empty search query
        results = search_items(items, "")
        self.assertEqual(len(results), 3)
    
    def test_generate_slug(self):
        """Test generating slugs."""
        self.assertEqual(generate_slug("Hello World"), "hello-world")
        self.assertEqual(generate_slug("Test Item 123"), "test-item-123")
        self.assertEqual(generate_slug("Special!@#$Characters"), "special-characters")
        self.assertEqual(generate_slug("  Leading and Trailing Spaces  "), "leading-and-trailing-spaces")
        self.assertEqual(generate_slug("Multiple--Hyphens"), "multiple-hyphens")

if __name__ == "__main__":
    unittest.main()