from flask import Blueprint, request, jsonify
from ..models import db, Category

category_bp = Blueprint("category_bp", __name__)

# GET /categories - List all categories
@category_bp.route("/categories", methods=["GET"])
def get_categories():
    categories = Category.query.all()
    return jsonify([cat.to_dict() for cat in categories]), 200

# GET /categories/<int:id> - Get a single category
@category_bp.route("/categories/<int:id>", methods=["GET"])
def get_category(id):
    category = Category.query.get(id)
    if not category:
        return jsonify({"error": "Category not found"}), 404
    return jsonify(category.to_dict()), 200

# POST /categories - Create a new category
@category_bp.route("/categories", methods=["POST"])
def create_category():
    data = request.get_json()
    try:
        name = data["name"]
        description = data.get("description", "")
        new_category = Category(name=name, description=description)
        db.session.add(new_category)
        db.session.commit()
        return jsonify(new_category.to_dict()), 201
    except KeyError:
        return jsonify({"error": "Missing 'name' field"}), 400

# PUT /categories/<int:id> - Update a category
@category_bp.route("/categories/<int:id>", methods=["PUT"])
def update_category(id):
    category = Category.query.get(id)
    if not category:
        return jsonify({"error": "Category not found"}), 404

    data = request.get_json()
    if "name" in data:
        category.name = data["name"]
    if "description" in data:
        category.description = data["description"]

    db.session.commit()
    return jsonify(category.to_dict()), 200

# DELETE /categories/<int:id> - Delete a category
@category_bp.route("/categories/<int:id>", methods=["DELETE"])
def delete_category(id):
    category = Category.query.get(id)
    if not category:
        return jsonify({"error": "Category not found"}), 404

    db.session.delete(category)
    db.session.commit()
    return jsonify({"message": f"Category #{id} deleted"}), 200
