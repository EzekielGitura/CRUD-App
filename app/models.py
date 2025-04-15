from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

from app.db.database import Base

# Association table for many-to-many relationship between items and tags
item_tag = Table(
    'item_tag',
    Base.metadata,
    Column('item_id', Integer, ForeignKey('items.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

class User(Base):
    """User model for authentication."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationships
    items = relationship("Item", back_populates="owner")
    
    def __init__(self, username, email, password, is_admin=False):
        self.username = username
        self.email = email
        self.set_password(password)
        self.is_admin = is_admin
    
    def set_password(self, password):
        """Hash and set the password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat()
        }

class Category(Base):
    """Category model for organizing items."""
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationships
    items = relationship("Item", back_populates="category")
    
    def to_dict(self):
        """Convert category to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }

class Tag(Base):
    """Tag model for labeling items."""
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(30), unique=True, nullable=False)
    
    # Relationships
    items = relationship("Item", secondary=item_tag, back_populates="tags")
    
    def to_dict(self):
        """Convert tag to dictionary."""
        return {
            "id": self.id,
            "name": self.name
        }

class Item(Base):
    """Item model (main data entity)."""
    __tablename__ = 'items'
    
    id = Column(Integer, primary_key=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, onupdate=datetime.now)
    
    # Foreign keys
    owner_id = Column(Integer, ForeignKey('users.id'))
    category_id = Column(Integer, ForeignKey('categories.id'))
    
    # Relationships
    owner = relationship("User", back_populates="items")
    category = relationship("Category", back_populates="items")
    tags = relationship("Tag", secondary=item_tag, back_populates="items")
    
    def to_dict(self):
        """Convert item to dictionary."""
        return {
            "id": self.id,
            "uuid": self.uuid,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "owner": self.owner.username if self.owner else None,
            "category": self.category.name if self.category else None,
            "tags": [tag.name for tag in self.tags]
        }