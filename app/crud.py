from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.models import Item, User, Category, Tag
from app.db.database import get_db
from app.utils import generate_slug

# User CRUD operations
def create_user(username: str, email: str, password: str, is_admin: bool = False) -> User:
    """Create a new user."""
    with get_db() as db:
        user = User(username=username, email=email, password=password, is_admin=is_admin)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

def get_users() -> List[User]:
    """Get all users."""
    with get_db() as db:
        return db.query(User).all()

def get_user_by_id(user_id: int) -> Optional[User]:
    """Get a user by ID."""
    with get_db() as db:
        return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(username: str) -> Optional[User]:
    """Get a user by username."""
    with get_db() as db:
        return db.query(User).filter(User.username == username).first()

def get_user_by_email(email: str) -> Optional[User]:
    """Get a user by email."""
    with get_db() as db:
        return db.query(User).filter(User.email == email).first()

def update_user(user_id: int, username: Optional[str] = None, 
               email: Optional[str] = None, password: Optional[str] = None,
               is_admin: Optional[bool] = None) -> Optional[User]:
    """Update a user."""
    with get_db() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return None
        
        if username is not None:
            user.username = username
        if email is not None:
            user.email = email
        if password is not None:
            user.set_password(password)
        if is_admin is not None:
            user.is_admin = is_admin
        
        db.commit()
        db.refresh(user)
        return user

def delete_user(user_id: int) -> bool:
    """Delete a user."""
    with get_db() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return False
        
        db.delete(user)
        db.commit()
        return True

# Category CRUD operations
def create_category(name: str, description: Optional[str] = None) -> Category:
    """Create a new category."""
    with get_db() as db:
        category = Category(name=name, description=description)
        db.add(category)
        db.commit()
        db.refresh(category)
        return category

def get_categories() -> List[Category]:
    """Get all categories."""
    with get_db() as db:
        return db.query(Category).all()

def get_category_by_id(category_id: int) -> Optional[Category]:
    """Get a category by ID."""
    with get_db() as db:
        return db.query(Category).filter(Category.id == category_id).first()

def get_category_by_name(name: str) -> Optional[Category]:
    """Get a category by name."""
    with get_db() as db:
        return db.query(Category).filter(Category.name == name).first()

def update_category(category_id: int, name: Optional[str] = None,
                   description: Optional[str] = None) -> Optional[Category]:
    """Update a category."""
    with get_db() as db:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return None
        
        if name is not None:
            category.name = name
        if description is not None:
            category.description = description
        
        db.commit()
        db.refresh(category)
        return category

def delete_category(category_id: int) -> bool:
    """Delete a category."""
    with get_db() as db:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return False
        
        db.delete(category)
        db.commit()
        return True

# Tag CRUD operations
def create_tag(name: str) -> Tag:
    """Create a new tag."""
    with get_db() as db:
        tag = Tag(name=name)
        db.add(tag)
        db.commit()
        db.refresh(tag)
        return tag

def get_tags() -> List[Tag]:
    """Get all tags."""
    with get_db() as db:
        return db.query(Tag).all()

def get_tag_by_id(tag_id: int) -> Optional[Tag]:
    """Get a tag by ID."""
    with get_db() as db:
        return db.query(Tag).filter(Tag.id == tag_id).first()

def get_tag_by_name(name: str) -> Optional[Tag]:
    """Get a tag by name."""
    with get_db() as db:
        return db.query(Tag).filter(Tag.name == name).first()

def delete_tag(tag_id: int) -> bool:
    """Delete a tag."""
    with get_db() as db:
        tag = db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            return False
        
        db.delete(tag)
        db.commit()
        return True

# Item CRUD operations (updated to use SQLAlchemy)
def create_item(name: str, description: str, owner_id: Optional[int] = None,
               category_id: Optional[int] = None, tag_ids: Optional[List[int]] = None) -> Item:
    """Create a new item."""
    with get_db() as db:
        item = Item(name=name, description=description)
        
        # Set owner if provided
        if owner_id:
            item.owner_id = owner_id
        
        # Set category if provided
        if category_id:
            item.category_id = category_id
        
        # Add tags if provided
        if tag_ids:
            tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
            item.tags = tags
        
        db.add(item)
        db.commit()
        db.refresh(item)
        return item

def get_items(limit: Optional[int] = None, offset: Optional[int] = None) -> List[Item]:
    """Get all items with optional pagination."""
    with get_db() as db:
        query = db.query(Item)
        
        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)
            
        return query.all()

def get_item_by_id(item_id: int) -> Optional[Item]:
    """Get an item by ID."""
    with get_db() as db:
        return db.query(Item).filter(Item.id == item_id).first()

def get_item_by_uuid(uuid: str) -> Optional[Item]:
    """Get an item by UUID."""
    with get_db() as db:
        return db.query(Item).filter(Item.uuid == uuid).first()

def search_items(query: str, category_id: Optional[int] = None, 
                tag_ids: Optional[List[int]] = None) -> List[Item]:
    """Search items by query, optionally filtered by category and tags."""
    with get_db() as db:
        item_query = db.query(Item)
        
        # Apply text search
        if query:
            item_query = item_query.filter(
                (Item.name.ilike(f"%{query}%")) | 
                (Item.description.ilike(f"%{query}%"))
            )
        
        # Filter by category
        if category_id:
            item_query = item_query.filter(Item.category_id == category_id)
        
        # Filter by tags (items must have ALL specified tags)
        if tag_ids:
            for tag_id in tag_ids:
                item_query = item_query.filter(
                    Item.tags.any(Tag.id == tag_id)
                )
                
        return item_query.all()

def update_item(item_id: int, name: Optional[str] = None, 
               description: Optional[str] = None, owner_id: Optional[int] = None,
               category_id: Optional[int] = None, tag_ids: Optional[List[int]] = None) -> Optional[Item]:
    """Update an item."""
    with get_db() as db:
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
            return None
        
        # Update basic fields
        if name is not None:
            item.name = name
        if description is not None:
            item.description = description
        if owner_id is not None:
            item.owner_id = owner_id
        if category_id is not None:
            item.category_id = category_id
        
        # Update tags if provided
        if tag_ids is not None:
            tags = db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
            item.tags = tags
        
        item.updated_at = datetime.now()
        db.commit()
        db.refresh(item)
        return item

def delete_item(item_id: int) -> bool:
    """Delete an item."""
    with get_db() as db:
        item = db.query(Item).filter(Item.id == item_id).first()
        if not item:
            return False
        
        db.delete(item)
        db.commit()
        return True

def count_items(category_id: Optional[int] = None) -> int:
    """Count items, optionally filtered by category."""
    with get_db() as db:
        query = db.query(Item)
        if category_id:
            query = query.filter(Item.category_id == category_id)
        return query.count()