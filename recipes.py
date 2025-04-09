from db import recipes_collection, users_collection

def add_recipe(username, name, ingredients, cuisine, cook_time, instructions):
    """Adds a new recipe and updates the user's added_recipes list."""
    if recipes_collection.find_one({"name": name}):
        return False  # Recipe name should be unique

    recipe = {
        "name": name,
        "ingredients": ingredients,
        "cuisine": cuisine,
        "cook_time": cook_time,
        "instructions": instructions,
        "added_by": username,
        "ratings": {},  # Stores {username: rating}
        "reviews": [],  # List of {user, rating, feedback}
        "average_rating": 0.0
    }

    recipes_collection.insert_one(recipe)
    users_collection.update_one({"username": username}, {"$push": {"added_recipes": name}})
    return True

def edit_recipe(username, recipe_name, new_data):
    """Allows the user who created the recipe to edit it."""
    recipe = recipes_collection.find_one({"name": recipe_name, "added_by": username})
    if not recipe:
        return False  # User can only edit their own recipes

    recipes_collection.update_one({"name": recipe_name}, {"$set": new_data})
    return True

def delete_recipe(username, recipe_name):
    """Allows a user to delete their own recipe."""
    recipe = recipes_collection.find_one({"name": recipe_name, "added_by": username})
    if not recipe:
        return False  # User can only delete their own recipes

    recipes_collection.delete_one({"name": recipe_name})
    users_collection.update_one({"username": username}, {"$pull": {"added_recipes": recipe_name}})
    return True

def rate_recipe(username, recipe_name, rating, feedback=""):
    """Allows users to rate a recipe only once and optionally add feedback."""
    recipe = recipes_collection.find_one({"name": recipe_name})
    
    if not recipe or username in recipe.get("ratings", {}):
        return False  # Recipe doesn't exist or user already rated

    # Ensure the "reviews" field exists
    if "reviews" not in recipe:
        recipe["reviews"] = []

    # Add rating & feedback
    recipe["ratings"][username] = rating
    review_entry = {"user": username, "rating": rating, "feedback": feedback}
    recipe["reviews"].append(review_entry)

    # Update average rating
    new_avg = sum(recipe["ratings"].values()) / len(recipe["ratings"])

    recipes_collection.update_one({"name": recipe_name}, {
        "$set": {
            "ratings": recipe["ratings"],
            "reviews": recipe["reviews"],
            "average_rating": new_avg
        }
    })

    users_collection.update_one({"username": username}, {
        "$set": {f"rated_recipes.{recipe_name}": rating}
    })

    return True


def get_all_recipes():
    """Fetches all recipes."""
    return list(recipes_collection.find({}, {"_id": 0}))

def get_user_recipes(username):
    """Fetches only the recipes created by the logged-in user."""
    return list(recipes_collection.find({"added_by": username}, {"_id": 0}))

def get_recipe_reviews(recipe_name):
    """Fetches all reviews for a given recipe."""
    recipe = recipes_collection.find_one({"name": recipe_name}, {"_id": 0, "reviews": 1})
    return recipe["reviews"] if recipe else []
