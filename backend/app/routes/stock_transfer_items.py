from flask import Blueprint, request, jsonify
from ..models import db, StockTransferItem, StockTransfer, Product

stock_transfer_item_bp = Blueprint("stock_transfer_item_bp", __name__)

@stock_transfer_item_bp.route("/stock_transfer_items", methods=["GET"])
def get_stock_transfer_items():
    items = StockTransferItem.query.all()
    return jsonify([item.to_dict() for item in items]), 200

@stock_transfer_item_bp.route("/stock_transfer_items/<int:id>", methods=["GET"])
def get_stock_transfer_item(id):
    item = StockTransferItem.query.get(id)
    if not item:
        return jsonify({"error": "Stock transfer item not found"}), 404
    return jsonify(item.to_dict()), 200

@stock_transfer_item_bp.route("/stock_transfer_items", methods=["POST"])
def create_stock_transfer_item():
    data = request.get_json()
    try:
        transfer_id = data["stock_transfer_id"]
        product_id = data["product_id"]
        quantity = int(data.get("quantity", 1))

        if not StockTransfer.query.get(transfer_id):
            return jsonify({"error": "Invalid stock_transfer_id"}), 400
        if not Product.query.get(product_id):
            return jsonify({"error": "Invalid product_id"}), 400

        item = StockTransferItem(
            stock_transfer_id=transfer_id,
            product_id=product_id,
            quantity=quantity
        )
        db.session.add(item)
        db.session.commit()
        return jsonify(item.to_dict()), 201
    except KeyError as e:
        return jsonify({"error": f"Missing field: {str(e)}"}), 400

@stock_transfer_item_bp.route("/stock_transfer_items/<int:id>", methods=["PUT"])
def update_stock_transfer_item(id):
    item = StockTransferItem.query.get(id)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    data = request.get_json()
    if "quantity" in data:
        item.quantity = data["quantity"]
    if "product_id" in data:
        if not Product.query.get(data["product_id"]):
            return jsonify({"error": "Invalid product_id"}), 400
        item.product_id = data["product_id"]

    db.session.commit()
    return jsonify(item.to_dict()), 200

@stock_transfer_item_bp.route("/stock_transfer_items/<int:id>", methods=["DELETE"])
def delete_stock_transfer_item(id):
    item = StockTransferItem.query.get(id)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": f"Item #{id} deleted"}), 200
