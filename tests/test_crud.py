import os
import json
import unittest
from datetime import datetime
import tempfile
import shutil

from app import crud
from app.models import Item

class TestCrud(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        # Create a temporary directory for the test database
        self.temp_dir = tempfile.mkdtemp()
        self.original_db_path = crud.DB_PATH
        
        # Set the database path to the temporary location
        crud.DB_PATH = os.path.join(self.temp_dir, "db.json")
        
        # Create an empty database file
        os.makedirs(os.path.dirname(crud.DB_PATH), exist_ok=True)
        with open(crud.DB_PATH, "w") as f:
            json.dump({"items": []}, f)
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)
        
        # Restore the original database path
        crud.DB_PATH = self.original_db_path
    
    def test_create_item(self):
        """Test creating an item."""
        name = "Test Item"
        description = "This is a test item"
        
        item = crud.create_item(name, description)
        
        self.assertEqual(item.name, name)
        self.assertEqual(item.description, description)
        self.assertIsNotNone(item.id)
        
        # Check if the item was saved to the database
        with open(crud.DB_PATH, "r") as f:
            db = json.load(f)
        
        self.assertEqual(len(db["items"]), 1)
        self.assertEqual(db["items"][0]["name"], name)
    
    def test_get_items(self):
        """Test getting all items."""
        # Create some test items
        item1 = crud.create_item("Item 1", "Description 1")
        item2 = crud.create_item("Item 2", "Description 2")
        
        items = crud.get_items()
        
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].name, "Item 1")
        self.assertEqual(items[1].name, "Item 2")
    
    def test_get_item_by_id(self):
        """Test getting an item by ID."""
        # Create a test item
        item = crud.create_item("Test Item", "Description")
        
        # Get the item by ID
        retrieved_item = crud.get_item_by_id(item.id)
        
        self.assertIsNotNone(retrieved_item)
        self.assertEqual(retrieved_item.id, item.id)
        self.assertEqual(retrieved_item.name, item.name)
        
        # Test with non-existent ID
        non_existent = crud.get_item_by_id("non-existent-id")
        self.assertIsNone(non_existent)
    
    def test_update_item(self):
        """Test updating an item."""
        # Create a test item
        item = crud.create_item("Original Name", "Original Description")
        
        # Update the item
        updated_item = crud.update_item(item.id, name="Updated Name")
        
        self.assertIsNotNone(updated_item)
        self.assertEqual(updated_item.name, "Updated Name")
        self.assertEqual(updated_item.description, "Original Description")
        self.assertIsNotNone(updated_item.updated_at)
        
        # Check if the update was saved to the database
        retrieved_item = crud.get_item_by_id(item.id)
        self.assertEqual(retrieved_item.name, "Updated Name")
        
        # Test updating description only
        updated_item = crud.update_item(item.id, description="Updated Description")
        self.assertEqual(updated_item.name, "Updated Name")
        self.assertEqual(updated_item.description, "Updated Description")
        
        # Test with non-existent ID
        non_existent = crud.update_item("non-existent-id", name="New Name")
        self.assertIsNone(non_existent)
    
    def test_delete_item(self):
        """Test deleting an item."""
        # Create a test item
        item = crud.create_item("Test Item", "Description")
        
        # Delete the item
        success = crud.delete_item(item.id)
        
        self.assertTrue(success)
        
        # Check if the item was deleted from the database
        items = crud.get_items()
        self.assertEqual(len(items), 0)
        
        # Test with non-existent ID
        success = crud.delete_item("non-existent-id")
        self.assertFalse(success)

if __name__ == "__main__":
    unittest.main()