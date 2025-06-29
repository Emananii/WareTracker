from flask import Blueprint, request, jsonify
from flasgger import swag_from
from ..models import db, Category, Product

category_bp = Blueprint("category_bp", __name__)


@category_bp.route("/categories", methods=["GET"])
@swag_from({
    'tags': ['Categories'],
    'summary': 'Get all active categories',
    'responses': {
        200: {
            'description': 'List of categories',
            'content': {
                'application/json': {
                    'example': [
                        {
                            "id": 1,
                            "name": "Beverages",
                            "description": "All drinkable products",
                            "is_deleted": False
                        }
                    ]
                }
            }
        }
    }
})
def get_categories():
    categories = Category.query.filter_by(is_deleted=False).all()
    return jsonify([cat.to_dict() for cat in categories]), 200


@category_bp.route("/categories/<int:id>", methods=["GET"])
@swag_from({
    'tags': ['Categories'],
    'summary': 'Get a specific category by ID',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'required': True,
            'schema': {'type': 'integer'}
        }
    ],
    'responses': {
        200: {
            'description': 'Category found',
            'content': {
                'application/json': {
                    'example': {
                        "id": 1,
                        "name": "Beverages",
                        "description": "All drinkable products",
                        "is_deleted": False
                    }
                }
            }
        },
        404: {
            'description': 'Category not found or deleted'
        }
    }
})
def get_category(id):
    category = Category.query.filter_by(id=id, is_deleted=False).first()
    if not category:
        return jsonify({"error": "Category not found or has been deleted"}), 404
    return jsonify(category.to_dict()), 200


@category_bp.route("/categories", methods=["POST"])
@swag_from({
    'tags': ['Categories'],
    'summary': 'Create a new category',
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'example': {
                    "name": "Snacks",
                    "description": "Quick bites"
                }
            }
        }
    },
    'responses': {
        201: {'description': 'Category created'},
        400: {'description': 'Missing category name'},
        409: {'description': 'Category already exists'},
        500: {'description': 'Unexpected server error'}
    }
})
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
            existing_category.description = description
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
@swag_from({
    'tags': ['Categories'],
    'summary': 'Update a category',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'required': True,
            'schema': {'type': 'integer'}
        }
    ],
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'example': {
                    "name": "New Category Name",
                    "description": "Updated description"
                }
            }
        }
    },
    'responses': {
        200: {'description': 'Category updated'},
        404: {'description': 'Category not found'},
        409: {'description': 'Duplicate name error'},
        500: {'description': 'Unexpected error'}
    }
})
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
@swag_from({
    'tags': ['Categories'],
    'summary': 'Soft delete a category',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'required': True,
            'schema': {'type': 'integer'}
        }
    ],
    'responses': {
        200: {'description': 'Category deleted successfully'},
        404: {'description': 'Category not found or already deleted'},
        500: {'description': 'Unexpected error'}
    }
})
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
