from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from flask import current_app, request, jsonify, g
from functools import wraps

from app.crud import get_user_by_username, get_user_by_id

# Secret key for JWT encoding/decoding
SECRET_KEY = "your-secret-key"  # In production, this should be in environment variables

def create_token(user_id: int, expires_delta: Optional[timedelta] = None) -> str:
    """Create a new JWT token for a user."""
    # Set token expiration time (default: 1 day)
    if expires_delta is None:
        expires_delta = timedelta(days=1)
    
    # Create token payload
    payload = {
        "sub": user_id,
        "exp": datetime.utcnow() + expires_delta,
        "iat": datetime.utcnow()
    }
    
    # Encode token
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Decode a JWT token and return the payload."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.PyJWTError:
        return None

def token_required(f):
    """Decorator to require a valid token for API endpoints."""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid token"}), 401
        
        token = auth_header.split(" ")[1]
        
        # Decode token
        payload = decode_token(token)
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        # Get user from database
        user_id = payload["sub"]
        user = get_user_by_id(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 401
        
        # Store user in request context
        g.current_user = user
        
        return f(*args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator to require admin privileges for API endpoints."""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Check if user is authenticated
        if not hasattr(g, "current_user"):
            return jsonify({"error": "Authentication required"}), 401
        
        # Check if user is an admin
        if not g.current_user.is_admin:
            return jsonify({"error": "Admin privileges required"}), 403
        
        return f(*args, **kwargs)
    
    return decorated