import hashlib
from db import users_collection

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def add_user(username, password):
    """Registers a new user if username is unique."""
    if users_collection.find_one({"username": username}):
        return False
    users_collection.insert_one({
        "username": username,
        "password": hash_password(password),
        "added_recipes": [],
        "rated_recipes": {}  # Stores {recipe_name: rating}
    })
    return True

def authenticate_user(username, password):
    """Validates user credentials."""
    user = users_collection.find_one({"username": username, "password": hash_password(password)})
    return user is not None
