from flask import Blueprint, request, jsonify
from ..models import db, Category, Product

category_bp = Blueprint("category_bp", __name__)


@category_bp.route("/categories", methods=["GET"])
def get_categories():
    categories = Category.query.filter_by(is_deleted=False).all()
    return jsonify([cat.to_dict() for cat in categories]), 200

@category_bp.route("/categories/<int:id>", methods=["GET"])
def get_category(id):
    category = Category.query.filter_by(id=id, is_deleted=False).first()
    if not category:
        return jsonify({"error": "Category not found or has been deleted"}), 404
    return jsonify(category.to_dict()), 200


@category_bp.route("/categories", methods=["POST"])
def create_category():
    data = request.get_json()
    try:
        name = data.get("name")
        description = data.get("description", "")

        if not name:
            return jsonify({"error": "Category name is required"}), 400

        existing_category = Category.query.filter_by(name=name).first()
        if existing_category and not existing_category.is_deleted:
            return jsonify({"error": "Category with this name already exists"}), 409

        if existing_category and existing_category.is_deleted:
            existing_category.is_deleted = False
            existing_category.description = description # Update description if provided
            db.session.commit()
            return jsonify(existing_category.to_dict()), 200

        new_category = Category(name=name, description=description)
        db.session.add(new_category)
        db.session.commit()
        return jsonify(new_category.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@category_bp.route("/categories/<int:id>", methods=["PUT"])
def update_category(id):
    category = Category.query.filter_by(id=id, is_deleted=False).first()
    if not category:
        return jsonify({"error": "Category not found or has been deleted"}), 404

    data = request.get_json()
    if "name" in data:
        new_name = data["name"]
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
    category = Category.query.filter_by(id=id, is_deleted=False).first()
    if not category:
        return jsonify({"error": "Category not found or already deleted"}), 404

    category.is_deleted = True
    try:
        db.session.commit()
        return jsonify({"message": "Category soft-deleted successfully."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to soft-delete category: {str(e)}"}), 500