from flask import Blueprint, jsonify, request, g
from typing import List, Dict, Any

from app import crud
from app.api.auth import token_required, admin_required, create_token
from app.utils import validate_item_data

# Create API blueprint
api_bp = Blueprint("api", __name__, url_prefix="/api")

# Authentication endpoints
@api_bp.route("/auth/login", methods=["POST"])
def login():
    """Authenticate a user and return a token."""
    data = request.json
    
    # Check if username and password are provided
    if not data or not data.get("username") or not data.get("password"):
        return jsonify({"error": "Username and password are required"}), 400
    
    # Get user from database
    user = crud.get_user_by_username(data["username"])
    if not user or not user.check_password(data["password"]):
        return jsonify({"error": "Invalid username or password"}), 401
    
    # Create token
    token = create_token(user.id)
    
    return jsonify({
        "token": token,
        "user": user.to_dict()
    })

@api_bp.route("/auth/register", methods=["POST"])
def register():
    """Register a new user."""
    data = request.json
    
    # Check if required fields are provided
    if not data or not data.get("username") or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Username, email, and password are required"}), 400
    
    # Check if username or email already exists
    if crud.get_user_by_username(data["username"]):
        return jsonify({"error": "Username already exists"}), 400
    
    if crud.get_user_by_email(data["email"]):
        return jsonify({"error": "Email already exists"}), 400
    
    # Create user
    user = crud.create_user(
        username=data["username"],
        email=data["email"],
        password=data["password"]
    )
    
    # Create token
    token = create_token(user.id)
    
    return jsonify({
        "token": token,
        "user": user.to_dict()
    }), 201

# User endpoints
@api_bp.route("/users", methods=["GET"])
@token_required
@admin_required
def get_users():
    """Get all users (admin only)."""
    users = crud.get_users()
    return jsonify([user.to_dict() for user in users])

@api_bp.route("/users/<int:user_id>", methods=["GET"])
@token_required
def get_user(user_id):
    """Get a user by ID."""
    # Check if user is requesting their own info or is an admin
    if g.current_user.id != user_id and not g.current_user.is_admin:
        return jsonify({"error": "Unauthorized"}), 403
    
    user = crud.get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify(user.to_dict())

@api_bp.route("/users/<int:user_id>", methods=["PUT"])
@token_required
def update_user(user_id):
    """Update a user."""
    # Check if user is updating their own info or is an admin
    if g.current_user.id != user_id and not g.current_user.is_admin:
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Update user
    user = crud.update_user(
        user_id=user_id,
        username=data.get("username"),
        email=data.get("email"),
        password=data.get("password"),
        is_admin=data.get("is_admin") if g.current_user.is_admin else None
    )
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify(user.to_dict())

@api_bp.route("/users/<int:user_id>", methods=["DELETE"])
@token_required
@admin_required
def delete_user(user_id):
    """Delete a user (admin only)."""
    # Prevent deleting self
    if g.current_user.id == user_id:
        return jsonify({"error": "Cannot delete yourself"}), 400
    
    success = crud.delete_user(user_id)
    if not success:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({"message": "User deleted successfully"}), 200

# Item endpoints
@api_bp.route("/items", methods=["GET"])
def get_items():
    """Get all items with optional filtering and pagination."""
    # Get query parameters
    limit = request.args.get("limit", type=int)
    offset = request.args.get("offset", type=int)
    search = request.args.get("search")
    category_id = request.args.get("category_id", type=int)
    tag_ids = request.args.getlist("tag_id", type=int)
    
    # Search items or get all
    if search or category_id or tag_ids:
        items = crud.search_items(search, category_id, tag_ids)
    else:
        items = crud.get_items(limit, offset)
    
    # Get total count for pagination
    total_count = crud.count_items(category_id)
    
    return jsonify({
        "items": [item.to_dict() for item in items],
        "total": total_count,
        "limit": limit,
        "offset": offset
    })

@api_bp.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    """Get an item by ID."""
    item = crud.get_item_by_id(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    
    return jsonify(item.to_dict())

@api_bp.route("/items", methods=["POST"])
@token_required
def create_item():
    """Create a new item."""
    data = request.json
    
    # Validate item data
    errors = validate_item_data(data)
    if errors:
        return jsonify({"errors": errors}), 400
    
    # Create item
    item = crud.create_item(
        name=data["name"],
        description=data["description"],
        owner_id=g.current_user.id,
        category_id=data.get("category_id"),
        tag_ids=data.get("tag_ids", [])
    )
    
    return jsonify(item.to_dict()), 201

@api_bp.route("/items/<int:item_id>", methods=["PUT"])
@token_required
def update_item(item_id):
    """Update an item."""
    # Get item from database
    item = crud.get_item_by_id(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    
    # Check if user is the owner or an admin
    if item.owner_id != g.current_user.id and not g.current_user.is_admin:
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Update item
    updated_item = crud.update_item(
        item_id=item_id,
        name=data.get("name"),
        description=data.get("description"),
        category_id=data.get("category_id"),
        tag_ids=data.get("tag_ids")
    )
    
    return jsonify(updated_item.to_dict())

@api_bp.route("/items/<int:item_id>", methods=["DELETE"])
@token_required
def delete_item(item_id):
    """Delete an item."""
    # Get item from database
    item = crud.get_item_by_id(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404
    
    # Check if user is the owner or an admin
    if item.owner_id != g.current_user.id and not g.current_user.is_admin:
        return jsonify({"error": "Unauthorized"}), 403
    
    success = crud.delete_item(item_id)
    return jsonify({"message": "Item deleted successfully"}), 200

# Category endpoints
@api_bp.route("/categories", methods=["GET"])
def get_categories():
    """Get all categories."""
    categories = crud.get_categories()
    return jsonify([category.to_dict() for category in categories])

@api_bp.route("/categories/<int:category_id>", methods=["GET"])
def get_category(category_id):
    """Get a category by ID."""
    category = crud.get_category_by_id(category_id)
    if not category:
        return jsonify({"error": "Category not found"}), 404
    
    return jsonify(category.to_dict())

@api_bp.route("/categories", methods=["POST"])
@token_required
@admin_required
def create_category():
    """Create a new category (admin only)."""
    data = request.json
    
    # Check if required fields are provided
    if not data or not data.get("name"):
        return jsonify({"error": "Name is required"}), 400
    
    # Check if category already exists
    if crud.get_category_by_name(data["name"]):
        return jsonify({"error": "Category already exists"}), 400
    
    # Create category
     # Create category
    category = crud.create_category(
        name=data["name"],
        description=data.get("description")
    )
    
    return jsonify(category.to_dict()), 201

@api_bp.route("/categories/<int:category_id>", methods=["PUT"])
@token_required
@admin_required
def update_category(category_id):
    """Update a category (admin only)."""
    data = request.json
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Update category
    category = crud.update_category(
        category_id=category_id,
        name=data.get("name"),
        description=data.get("description")
    )
    
    if not category:
        return jsonify({"error": "Category not found"}), 404
    
    return jsonify(category.to_dict())

@api_bp.route("/categories/<int:category_id>", methods=["DELETE"])
@token_required
@admin_required
def delete_category(category_id):
    """Delete a category (admin only)."""
    success = crud.delete_category(category_id)
    if not success:
        return jsonify({"error": "Category not found"}), 404
    
    return jsonify({"message": "Category deleted successfully"}), 200

# Tag endpoints
@api_bp.route("/tags", methods=["GET"])
def get_tags():
    """Get all tags."""
    tags = crud.get_tags()
    return jsonify([tag.to_dict() for tag in tags])

@api_bp.route("/tags/<int:tag_id>", methods=["GET"])
def get_tag(tag_id):
    """Get a tag by ID."""
    tag = crud.get_tag_by_id(tag_id)
    if not tag:
        return jsonify({"error": "Tag not found"}), 404
    
    return jsonify(tag.to_dict())

@api_bp.route("/tags", methods=["POST"])
@token_required
def create_tag():
    """Create a new tag."""
    data = request.json
    
    # Check if required fields are provided
    if not data or not data.get("name"):
        return jsonify({"error": "Name is required"}), 400
    
    # Check if tag already exists
    if crud.get_tag_by_name(data["name"]):
        return jsonify({"error": "Tag already exists"}), 400
    
    # Create tag
    tag = crud.create_tag(name=data["name"])
    
    return jsonify(tag.to_dict()), 201

@api_bp.route("/tags/<int:tag_id>", methods=["DELETE"])
@token_required
@admin_required
def delete_tag(tag_id):
    """Delete a tag (admin only)."""
    success = crud.delete_tag(tag_id)
    if not success:
        return jsonify({"error": "Tag not found"}), 404
    
    return jsonify({"message": "Tag deleted successfully"}), 200