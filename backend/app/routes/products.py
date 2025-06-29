from flask import Blueprint, request, jsonify
from ..models import db, Product, Category
from sqlalchemy.exc import IntegrityError

product_bp = Blueprint("product_routes", __name__)

# ✅ GET all non-deleted products with valid (non-deleted) categories
@product_bp.route("/products", methods=["GET"])
def get_products():
    products = (
        Product.query
        .filter(Product.is_deleted == False)  # Exclude soft-deleted products
        .join(Product.category)
        .filter(Category.is_deleted == False)  # Exclude products from deleted categories
        .all()
    )
    return jsonify([p.to_dict() for p in products]), 200

# ✅ GET a single product by ID, only if not deleted
@product_bp.route("/products/<int:id>", methods=["GET"])
def get_product(id):
    product = Product.query.filter_by(id=id, is_deleted=False).first()
    if not product or (product.category and product.category.is_deleted):
        return jsonify({"error": "Product not found or category is deleted"}), 404
    return jsonify(product.to_dict()), 200

# ✅ Create a product
@product_bp.route("/products", methods=["POST"])
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

        # Validate category exists and is not deleted
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

# ✅ Update a product
@product_bp.route("/products/<int:id>", methods=["PUT"])
def update_product(id):
    product = Product.query.filter_by(id=id, is_deleted=False).first()
    if not product:
        return jsonify({"error": "Product not found"}), 404

    data = request.get_json()
    for field in ["name", "sku", "unit", "description", "category_id"]:
        if field in data:
            setattr(product, field, data[field])

    # Optionally validate updated category
    if "category_id" in data:
        new_category = Category.query.filter_by(id=data["category_id"], is_deleted=False).first()
        if not new_category:
            return jsonify({"error": "Invalid or deleted category"}), 400

    db.session.commit()
    return jsonify(product.to_dict()), 200

# ✅ Soft delete a product
@product_bp.route("/products/<int:id>", methods=["DELETE"])
def delete_product(id):
    product = Product.query.filter_by(id=id, is_deleted=False).first()
    if not product:
        return jsonify({"error": "Product not found or already deleted"}), 404

    product.is_deleted = True
    db.session.commit()
    return jsonify({"message": f"Product #{id} soft-deleted"}), 200
