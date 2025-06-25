from flask import Blueprint, request, jsonify
from ..models import db, PurchaseItem, Product, Purchase

purchase_item_bp = Blueprint("purchase_item_bp", __name__)

# GET /purchase_items - List all purchase items
@purchase_item_bp.route("/purchase_items", methods=["GET"])
def get_purchase_items():
    items = PurchaseItem.query.all()
    return jsonify([item.to_dict() for item in items]), 200

# GET /purchase_items/<int:id> - Get a single purchase item
@purchase_item_bp.route("/purchase_items/<int:id>", methods=["GET"])
def get_purchase_item(id):
    item = PurchaseItem.query.get(id)
    if not item:
        return jsonify({"error": "Purchase item not found"}), 404
    return jsonify(item.to_dict()), 200

# POST /purchase_items - Create a new purchase item
@purchase_item_bp.route("/purchase_items", methods=["POST"])
def create_purchase_item():
    data = request.get_json()
    try:
        purchase_id = data["purchase_id"]
        product_id = data["product_id"]
        quantity = int(data.get("quantity", 1))
        unit_cost = float(data.get("unit_cost", 0))

        # Verify foreign keys exist
        if not Purchase.query.get(purchase_id):
            return jsonify({"error": "Purchase not found"}), 404
        if not Product.query.get(product_id):
            return jsonify({"error": "Product not found"}), 404

        new_item = PurchaseItem(
            purchase_id=purchase_id,
            product_id=product_id,
            quantity=quantity,
            unit_cost=unit_cost
        )

        db.session.add(new_item)
        db.session.commit()
        return jsonify(new_item.to_dict()), 201

    except KeyError as e:
        return jsonify({"error": f"Missing field: {str(e)}"}), 400
    except ValueError:
        return jsonify({"error": "Invalid number format for quantity or cost"}), 400

# PUT /purchase_items/<int:id> - Update a purchase item
@purchase_item_bp.route("/purchase_items/<int:id>", methods=["PUT"])
def update_purchase_item(id):
    item = PurchaseItem.query.get(id)
    if not item:
        return jsonify({"error": "Purchase item not found"}), 404

    data = request.get_json()
    for field in ["quantity", "unit_cost", "product_id", "purchase_id"]:
        if field in data:
            setattr(item, field, data[field])

    db.session.commit()
    return jsonify(item.to_dict()), 200

# DELETE /purchase_items/<int:id> - Delete a purchase item
@purchase_item_bp.route("/purchase_items/<int:id>", methods=["DELETE"])
def delete_purchase_item(id):
    item = PurchaseItem.query.get(id)
    if not item:
        return jsonify({"error": "Purchase item not found"}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": f"Purchase item #{id} deleted"}), 200
