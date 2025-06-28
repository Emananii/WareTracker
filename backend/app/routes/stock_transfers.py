from flask import Blueprint, request, jsonify
from ..models import db, StockTransfer, BusinessLocation, Product, StockTransferItem
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

stock_transfer_bp = Blueprint("stock_transfer_bp", __name__, url_prefix="/stock_transfers")


@stock_transfer_bp.route("/", methods=["GET"])
def get_stock_transfers():
    transfers = StockTransfer.query.order_by(StockTransfer.date.desc()).all()
    return jsonify([t.to_dict() for t in transfers]), 200


@stock_transfer_bp.route("/<int:id>", methods=["GET"])
def get_stock_transfer(id):
    transfer = StockTransfer.query.get(id)
    if not transfer:
        return jsonify({"error": "Stock transfer not found"}), 404
    return jsonify(transfer.to_dict()), 200


@stock_transfer_bp.route("/", methods=["POST"])
def create_stock_transfer():
    data = request.get_json()

    try:
        location_id = data["location_id"]
        notes = data.get("notes", "")
        items = data.get("items", [])
        date = datetime.utcnow()

        if not items or not isinstance(items, list):
            return jsonify({"error": "At least one item is required"}), 400

        location = BusinessLocation.query.get(location_id)
        if not location:
            return jsonify({"error": "Invalid location_id"}), 400

        new_transfer = StockTransfer(
            location_id=location_id,
            notes=notes,
            date=date
        )
        db.session.add(new_transfer)
        db.session.flush()  # get transfer ID

        for item in items:
            product_id = item.get("product_id")
            quantity = item.get("quantity")

            if not product_id or quantity is None or quantity <= 0:
                continue

            product = Product.query.get(product_id)
            if not product:
                db.session.rollback()
                return jsonify({"error": f"Product ID {product_id} not found"}), 404

            if product.stock_level < quantity:
                db.session.rollback()
                return jsonify({"error": f"Not enough stock for product '{product.name}'"}), 400

            # Subtract quantity from stock
            product.stock_level -= quantity

            transfer_item = StockTransferItem(
                transfer_id=new_transfer.id,
                product_id=product_id,
                quantity=quantity
            )
            db.session.add(transfer_item)

        db.session.commit()
        return jsonify(new_transfer.to_dict()), 201

    except KeyError as e:
        db.session.rollback()
        return jsonify({"error": f"Missing field: {str(e)}"}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@stock_transfer_bp.route("/<int:id>", methods=["PUT"])
def update_stock_transfer(id):
    transfer = StockTransfer.query.get(id)
    if not transfer:
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


@stock_transfer_bp.route("/<int:id>", methods=["DELETE"])
def delete_stock_transfer(id):
    transfer = StockTransfer.query.get(id)
    if not transfer:
        return jsonify({"error": "Stock transfer not found"}), 404

    try:
        db.session.delete(transfer)
        db.session.commit()
        return jsonify({"message": f"Stock transfer #{id} deleted"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

