from flask import Blueprint, request, jsonify
from ..models import db, Product, Category
from sqlalchemy.exc import IntegrityError
from flasgger import swag_from

product_bp = Blueprint("product_routes", __name__)


@product_bp.route("/products", methods=["GET"])
@swag_from({
    'tags': ['Products'],
    'summary': 'Get all non-deleted products',
    'description': 'Returns a list of all products whose category is not deleted and which are not soft-deleted.',
    'responses': {
        200: {
            'description': 'List of products',
            'content': {
                'application/json': {
                    'example': [
                        {
                            "id": 1,
                            "name": "Sugar",
                            "sku": "SG-001",
                            "unit": "kg",
                            "description": "Refined white sugar",
                            "category_id": 2
                        }
                    ]
                }
            }
        }
    }
})
def get_products():
    products = (
        Product.query
        .filter(Product.is_deleted == False)
        .join(Product.category)
        .filter(Category.is_deleted == False)
        .all()
    )
    return jsonify([p.to_dict() for p in products]), 200


@product_bp.route("/products/<int:id>", methods=["GET"])
@swag_from({
    'tags': ['Products'],
    'summary': 'Get a specific product by ID',
    'description': 'Fetch a product only if it and its category are not soft-deleted.',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'required': True,
            'description': 'Product ID',
            'schema': {'type': 'integer'}
        }
    ],
    'responses': {
        200: {
            'description': 'Product data',
            'content': {
                'application/json': {
                    'example': {
                        "id": 1,
                        "name": "Sugar",
                        "sku": "SG-001",
                        "unit": "kg",
                        "description": "Refined white sugar",
                        "category_id": 2
                    }
                }
            }
        },
        404: {
            'description': 'Product not found or its category is deleted'
        }
    }
})
def get_product(id):
    product = Product.query.filter_by(id=id, is_deleted=False).first()
    if not product or (product.category and product.category.is_deleted):
        return jsonify({"error": "Product not found or category is deleted"}), 404
    return jsonify(product.to_dict()), 200


@product_bp.route("/products", methods=["POST"])
@swag_from({
    'tags': ['Products'],
    'summary': 'Create a new product',
    'description': 'Creates a new product and associates it with a non-deleted category.',
    'consumes': ['application/json'],
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string'},
                        'sku': {'type': 'string'},
                        'unit': {'type': 'string'},
                        'description': {'type': 'string'},
                        'category_id': {'type': 'integer'}
                    },
                    'required': ['name', 'category_id']
                },
                'example': {
                    "name": "Salt",
                    "sku": "SL-001",
                    "unit": "kg",
                    "description": "Table salt",
                    "category_id": 1
                }
            }
        }
    },
    'responses': {
        201: {'description': 'Product created successfully'},
        400: {'description': 'Missing required fields or invalid category'},
        409: {'description': 'Product with same name or SKU already exists'}
    }
})
def create_product():
    data = request.get_json()

    try:
        new_product = Product(
            name=data["name"],
            sku=data.get("sku"),
            unit=data.get("unit"),
            description=data.get("description"),
            category_id=data["category_id"],
            is_deleted=False
        )

        category = Category.query.filter_by(id=new_product.category_id, is_deleted=False).first()
        if not category:
            return jsonify({"error": "Invalid or deleted category"}), 400

        db.session.add(new_product)
        db.session.commit()
        return jsonify(new_product.to_dict()), 201

    except KeyError as e:
        return jsonify({"error": f"Missing field: {str(e)}"}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Product with this name or SKU already exists"}), 409


@product_bp.route("/products/<int:id>", methods=["PUT"])
@swag_from({
    'tags': ['Products'],
    'summary': 'Update a product',
    'description': 'Update the name, SKU, unit, description or category of a product.',
    'consumes': ['application/json'],
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'required': True,
            'schema': {'type': 'integer'},
            'description': 'Product ID'
        }
    ],
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'schema': {
                    'type': 'object',
                    'properties': {
                        'name': {'type': 'string'},
                        'sku': {'type': 'string'},
                        'unit': {'type': 'string'},
                        'description': {'type': 'string'},
                        'category_id': {'type': 'integer'}
                    }
                },
                'example': {
                    "name": "Refined Salt",
                    "sku": "SL-001",
                    "unit": "g",
                    "description": "Fine grain salt",
                    "category_id": 2
                }
            }
        }
    },
    'responses': {
        200: {'description': 'Product updated successfully'},
        400: {'description': 'Invalid or deleted category'},
        404: {'description': 'Product not found'}
    }
})
def update_product(id):
    product = Product.query.filter_by(id=id, is_deleted=False).first()
    if not product:
        return jsonify({"error": "Product not found"}), 404

    data = request.get_json()
    for field in ["name", "sku", "unit", "description", "category_id"]:
        if field in data:
            setattr(product, field, data[field])

    if "category_id" in data:
        new_category = Category.query.filter_by(id=data["category_id"], is_deleted=False).first()
        if not new_category:
            return jsonify({"error": "Invalid or deleted category"}), 400

    db.session.commit()
    return jsonify(product.to_dict()), 200


@product_bp.route("/products/<int:id>", methods=["DELETE"])
@swag_from({
    'tags': ['Products'],
    'summary': 'Soft-delete a product',
    'description': 'Marks a product as deleted instead of permanently removing it.',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'required': True,
            'schema': {'type': 'integer'},
            'description': 'Product ID'
        }
    ],
    'responses': {
        200: {'description': 'Product soft-deleted successfully'},
        404: {'description': 'Product not found or already deleted'}
    }
})
def delete_product(id):
    product = Product.query.filter_by(id=id, is_deleted=False).first()
    if not product:
        return jsonify({"error": "Product not found or already deleted"}), 404

    product.is_deleted = True
    db.session.commit()
    return jsonify({"message": f"Product #{id} soft-deleted"}), 200
