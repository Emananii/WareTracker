from flask import Blueprint, request, jsonify
from ..models import db, Product
from sqlalchemy.exc import IntegrityError

product_bp = Blueprint("product_routes", __name__)

@product_bp.route("/products", methods=["GET"])
def get_products():
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products]), 200

@product_bp.route("/products/<int:id>", methods=["GET"])
def get_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product.to_dict()), 200

@product_bp.route("/products", methods=["POST"])
def create_product():
    data = request.get_json()

    try:
        new_product = Product(
            name=data["name"],
            sku=data.get("sku"),
            unit=data.get("unit"),
            description=data.get("description"),
            category_id=data["category_id"]
        )
        db.session.add(new_product)
        db.session.commit()
        return jsonify(new_product.to_dict()), 201

    except KeyError as e:
        return jsonify({"error": f"Missing field: {str(e)}"}), 400
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Product with this name or SKU already exists"}), 409

@product_bp.route("/products/<int:id>", methods=["PUT"])
def update_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    data = request.get_json()
    for field in ["name", "sku", "unit", "description", "category_id"]:
        if field in data:
            setattr(product, field, data[field])

    db.session.commit()
    return jsonify(product.to_dict()), 200

@product_bp.route("/products/<int:id>", methods=["DELETE"])
def delete_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": f"Product #{id} deleted"}), 200