from flask import Blueprint, request, jsonify
from ..models import db, StockTransfer, StockTransferItem, BusinessLocation, Product
from datetime import datetime

stock_transfer_bp = Blueprint("stock_transfer_bp", __name__)

# -------------------- GET All Transfers --------------------
@stock_transfer_bp.route("/stock_transfers", methods=["GET"])
def get_stock_transfers():
    transfers = StockTransfer.query.filter_by(is_deleted=False).all()
    return jsonify([transfer.to_dict() for transfer in transfers]), 200


# -------------------- GET Single Transfer --------------------
@stock_transfer_bp.route("/stock_transfers/<int:id>", methods=["GET"])
def get_stock_transfer(id):
    transfer = StockTransfer.query.get(id)
    if not transfer or transfer.is_deleted:
        return jsonify({"error": "Stock transfer not found"}), 404
    return jsonify(transfer.to_dict()), 200


# -------------------- POST Create Transfer --------------------
@stock_transfer_bp.route("/stock_transfers", methods=["POST"])
def create_stock_transfer():
    data = request.get_json()
    try:
        transfer_type = data["transfer_type"]
        location_id = data.get("location_id")
        notes = data.get("notes", "")
        items = data["items"]
        date = data.get("date")

        if transfer_type not in ("IN", "OUT"):
            return jsonify({"error": "transfer_type must be 'IN' or 'OUT'"}), 400

        if location_id:
            location = BusinessLocation.query.get(location_id)
            if not location:
                return jsonify({"error": "Invalid location_id"}), 400

        transfer = StockTransfer(
            transfer_type=transfer_type,
            location_id=location_id,
            notes=notes,
            date=datetime.fromisoformat(date) if date else datetime.utcnow()
        )
        db.session.add(transfer)
        db.session.flush()  # Ensure we can access transfer.id

        for item in items:
            product_id = item.get("product_id")
            quantity = item.get("quantity")

            if product_id is None or quantity is None:
                return jsonify({"error": "Each item must have product_id and quantity"}), 400

            product = Product.query.get(product_id)
            if not product:
                return jsonify({"error": f"Product ID {product_id} not found"}), 404

            if quantity < 0:
                return jsonify({"error": f"Invalid quantity for product {product.name}"}), 400

            # Adjust warehouse stock
            if transfer_type == "IN":
                product.quantity += quantity
            else:
                if product.quantity < quantity:
                    return jsonify({
                        "error": f"Not enough stock for product {product.name}. Available: {product.quantity}, Needed: {quantity}"
                    }), 400
                product.quantity -= quantity

            transfer_item = StockTransferItem(
                stock_transfer_id=transfer.id,
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(transfer_item)

        db.session.commit()
        return jsonify(transfer.to_dict()), 201

    except KeyError as e:
        return jsonify({"error": f"Missing required field: {str(e)}"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# -------------------- PUT Update Transfer (metadata only) --------------------
@stock_transfer_bp.route("/stock_transfers/<int:id>", methods=["PUT"])
def update_stock_transfer(id):
    transfer = StockTransfer.query.get(id)
    if not transfer or transfer.is_deleted:
        return jsonify({"error": "Stock transfer not found"}), 404

    data = request.get_json()

    if "location_id" in data:
        location = BusinessLocation.query.get(data["location_id"])
        if not location:
            return jsonify({"error": "Invalid location_id"}), 400
        transfer.location_id = data["location_id"]

    if "notes" in data:
        transfer.notes = data["notes"]

    db.session.commit()
    return jsonify(transfer.to_dict()), 200


# -------------------- DELETE Soft Delete with Reversal --------------------
@stock_transfer_bp.route("/stock_transfers/<int:id>", methods=["DELETE"])
def delete_stock_transfer(id):
    transfer = StockTransfer.query.get(id)
    if not transfer or transfer.is_deleted:
        return jsonify({"error": "Stock transfer not found or already deleted"}), 404

    try:
        for item in transfer.items:
            product = Product.query.get(item.product_id)
            if not product:
                continue  # silently skip

            if transfer.transfer_type == "IN":
                # Remove the stock that was previously added
                if product.quantity < item.quantity:
                    return jsonify({
                        "error": f"Cannot delete: insufficient stock to reverse IN transfer for product {product.name}"
                    }), 400
                product.quantity -= item.quantity
            elif transfer.transfer_type == "OUT":
                # Add the stock that was previously removed
                product.quantity += item.quantity

        transfer.is_deleted = True
        db.session.commit()
        return jsonify({"message": f"Stock transfer #{id} marked as deleted and reversed"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
