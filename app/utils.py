from typing import Dict, Any, List, Optional
import re

def validate_item_data(data: Dict[str, Any]) -> List[str]:
    """
    Validate item data before creating or updating.
    Returns a list of error messages. Empty list means validation passed.
    """
    errors = []
    
    # Check for required fields
    if "name" not in data:
        errors.append("Name is required")
    elif not data["name"].strip():
        errors.append("Name cannot be empty")
        
    if "description" not in data:
        errors.append("Description is required")
    elif not data["description"].strip():
        errors.append("Description cannot be empty")
    
    # Validate name length
    if "name" in data and len(data["name"]) > 100:
        errors.append("Name must be less than 100 characters")
    
    return errors

def format_item_for_display(item_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Format an item dictionary for display (e.g., in an API response)."""
    # Create a copy to avoid modifying the original
    formatted = item_dict.copy()
    
    # Format dates for better readability
    if "created_at" in formatted:
        # Just keep the date part without milliseconds
        formatted["created_at"] = formatted["created_at"].split(".")[0].replace("T", " ")
    
    if "updated_at" in formatted and formatted["updated_at"]:
        formatted["updated_at"] = formatted["updated_at"].split(".")[0].replace("T", " ")
    
    return formatted

def search_items(items: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
    """Search items by name or description."""
    if not query:
        return items
    
    query = query.lower()
    return [
        item for item in items
        if query in item["name"].lower() or query in item["description"].lower()
    ]

def generate_slug(name: str) -> str:
    """Generate a URL-friendly slug from a name."""
    # Convert to lowercase
    slug = name.lower()
    # Replace non-alphanumeric characters with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    return slug