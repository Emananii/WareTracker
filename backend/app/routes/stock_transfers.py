from flask import Blueprint, request, jsonify
from ..models import db, StockTransfer, BusinessLocation

stock_transfer_bp = Blueprint("stock_transfer_bp", __name__)

@stock_transfer_bp.route("/stock_transfers", methods=["GET"])
def get_stock_transfers():
    transfers = StockTransfer.query.all()
    return jsonify([transfer.to_dict() for transfer in transfers]), 200


@stock_transfer_bp.route("/stock_transfers/<int:id>", methods=["GET"])
def get_stock_transfer(id):
    transfer = StockTransfer.query.get(id)
    if not transfer:
        return jsonify({"error": "Stock transfer not found"}), 404
    return jsonify(transfer.to_dict()), 200

@stock_transfer_bp.route("/stock_transfers", methods=["POST"])
def create_stock_transfer():
    data = request.get_json()
    try:
        location_id = data["location_id"]
        notes = data.get("notes", "")
        date = data.get("date")

        location = BusinessLocation.query.get(location_id)
        if not location:
            return jsonify({"error": "Invalid location_id"}), 400

        transfer = StockTransfer(
            location_id=location_id,
            notes=notes
        )

        db.session.add(transfer)
        db.session.commit()
        return jsonify(transfer.to_dict()), 201
    except KeyError as e:
        return jsonify({"error": f"Missing field: {str(e)}"}), 400

@stock_transfer_bp.route("/stock_transfers/<int:id>", methods=["PUT"])
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

@stock_transfer_bp.route("/stock_transfers/<int:id>", methods=["DELETE"])
def delete_stock_transfer(id):
    transfer = StockTransfer.query.get(id)
    if not transfer:
        return jsonify({"error": "Stock transfer not found"}), 404

    db.session.delete(transfer)
    db.session.commit()
    return jsonify({"message": f"Stock transfer #{id} deleted"}), 200
