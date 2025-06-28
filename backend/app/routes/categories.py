from flask import Blueprint, request, jsonify
from ..models import db, Category, Product  # Assuming Product model is also defined and might be needed for cascade checks

category_bp = Blueprint("category_bp", __name__) # Removed url_prefix here, will add to route definitions for clarity


@category_bp.route("/categories", methods=["GET"])
def get_categories():
    # Only retrieve categories that are not marked as deleted
    categories = Category.query.filter_by(is_deleted=False).all()
    return jsonify([cat.to_dict() for cat in categories]), 200

@category_bp.route("/categories/<int:id>", methods=["GET"])
def get_category(id):
    # Retrieve a category by ID, ensuring it's not deleted
    category = Category.query.filter_by(id=id, is_deleted=False).first()
    if not category:
        return jsonify({"error": "Category not found or has been deleted"}), 404
    return jsonify(category.to_dict()), 200


@category_bp.route("/categories", methods=["POST"])
def create_category():
    data = request.get_json()
    try:
        name = data.get("name") # Use .get() for safer access and provide default
        description = data.get("description", "")

        if not name:
            return jsonify({"error": "Category name is required"}), 400

        # Check if a category with the same name already exists (even if soft-deleted)
        existing_category = Category.query.filter_by(name=name).first()
        if existing_category and not existing_category.is_deleted:
            return jsonify({"error": "Category with this name already exists"}), 409 # Conflict

        # If a soft-deleted category with the same name exists, "undelete" it
        if existing_category and existing_category.is_deleted:
            existing_category.is_deleted = False
            existing_category.description = description # Update description if provided
            db.session.commit()
            return jsonify(existing_category.to_dict()), 200 # Return 200 OK as it's an update/restore

        new_category = Category(name=name, description=description)
        db.session.add(new_category)
        db.session.commit()
        return jsonify(new_category.to_dict()), 201
    except Exception as e: # Catch a broader exception for unexpected errors
        db.session.rollback() # Rollback in case of an error during commit
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@category_bp.route("/categories/<int:id>", methods=["PUT"])
def update_category(id):
    # Only allow updating of non-deleted categories
    category = Category.query.filter_by(id=id, is_deleted=False).first()
    if not category:
        return jsonify({"error": "Category not found or has been deleted"}), 404

    data = request.get_json()
    if "name" in data:
        new_name = data["name"]
        # Check if the new name conflicts with an existing, non-deleted category
        if Category.query.filter(Category.name == new_name, Category.id != id, Category.is_deleted == False).first():
            return jsonify({"error": "Another non-deleted category with this name already exists"}), 409
        category.name = new_name
    if "description" in data:
        category.description = data["description"]

    try:
        db.session.commit()
        return jsonify(category.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500


@category_bp.route("/categories/<int:id>", methods=["DELETE"])
def delete_category(id):
    # Ensure the category exists and is not already soft-deleted
    category = Category.query.filter_by(id=id, is_deleted=False).first()
    if not category:
        return jsonify({"error": "Category not found or already deleted"}), 404

    # Perform the soft delete
    category.is_deleted = True
    try:
        db.session.commit()
        return jsonify({"message": "Category soft-deleted successfully."}), 200
    except Exception as e:
        db.session.rollback() # Rollback in case of a database error during commit
        return jsonify({"error": f"Failed to soft-delete category: {str(e)}"}), 500