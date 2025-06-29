from flask import Blueprint, request, jsonify
from ..models import db, StockTransfer, StockTransferItem, BusinessLocation, Product
from datetime import datetime
from zoneinfo import ZoneInfo
from flasgger import swag_from

stock_transfer_bp = Blueprint("stock_transfer_bp", __name__)
EAT = ZoneInfo("Africa/Nairobi")

# -------------------- GET All Transfers --------------------
@stock_transfer_bp.route("/stock_transfers", methods=["GET"])
@swag_from({
    'tags': ['Stock Transfers'],
    'summary': 'Get all stock transfers',
    'responses': {
        200: {
            'description': 'List of non-deleted stock transfers',
            'content': {
                'application/json': {
                    'example': [
                        {
                            "id": 1,
                            "transfer_type": "IN",
                            "location_id": 2,
                            "date": "2024-06-29T10:00:00+03:00",
                            "notes": "Restocking main branch"
                        }
                    ]
                }
            }
        }
    }
})
def get_stock_transfers():
    transfers = StockTransfer.query.filter_by(is_deleted=False).all()
    return jsonify([transfer.to_dict() for transfer in transfers]), 200


# -------------------- GET Single Transfer --------------------
@stock_transfer_bp.route("/stock_transfers/<int:id>", methods=["GET"])
@swag_from({
    'tags': ['Stock Transfers'],
    'summary': 'Get a specific stock transfer',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'required': True,
            'description': 'Stock transfer ID',
            'schema': {'type': 'integer'}
        }
    ],
    'responses': {
        200: {'description': 'Transfer found'},
        404: {'description': 'Transfer not found'}
    }
})
def get_stock_transfer(id):
    transfer = StockTransfer.query.get(id)
    if not transfer or transfer.is_deleted:
        return jsonify({"error": "Stock transfer not found"}), 404
    return jsonify(transfer.to_dict()), 200


# -------------------- POST Create Transfer --------------------
@stock_transfer_bp.route("/stock_transfers", methods=["POST"])
@swag_from({
    'tags': ['Stock Transfers'],
    'summary': 'Create a new stock transfer',
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'example': {
                    "transfer_type": "OUT",
                    "location_id": 1,
                    "notes": "Sending goods to warehouse",
                    "items": [
                        {
                            "product_id": 2,
                            "quantity": 10
                        }
                    ],
                    "date": "2025-06-29T13:00:00+03:00"
                }
            }
        }
    },
    'responses': {
        201: {'description': 'Transfer created successfully'},
        400: {'description': 'Bad input or invalid references'},
        500: {'description': 'Internal error'}
    }
})
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

        if not items or not isinstance(items, list):
            return jsonify({"error": "At least one item is required"}), 400

        transfer_date = datetime.fromisoformat(date).replace(tzinfo=EAT) if date else datetime.now(EAT)

        transfer = StockTransfer(
            transfer_type=transfer_type,
            location_id=location_id,
            notes=notes,
            date=transfer_date,
            is_deleted=False
        )
        db.session.add(transfer)
        db.session.flush()

        for item in items:
            product_id = item.get("product_id")
            quantity = item.get("quantity")

            if not product_id or quantity is None:
                return jsonify({"error": "Each item must have product_id and quantity"}), 400

            product = Product.query.get(product_id)
            if not product or product.is_deleted:
                return jsonify({"error": f"Invalid or deleted product ID {product_id}"}), 400

            if not isinstance(quantity, int) or quantity <= 0:
                return jsonify({"error": f"Invalid quantity: must be positive integer"}), 400

            if transfer_type == "OUT" and product.stock_level < quantity:
                return jsonify({
                    "error": f"Not enough stock for product '{product.name}'. Available: {product.stock_level}, Needed: {quantity}"
                }), 400

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


# -------------------- PUT Update Transfer --------------------
@stock_transfer_bp.route("/stock_transfers/<int:id>", methods=["PUT"])
@swag_from({
    'tags': ['Stock Transfers'],
    'summary': 'Update a stock transfer (metadata only)',
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
                    "location_id": 2,
                    "notes": "Updated destination"
                }
            }
        }
    },
    'responses': {
        200: {'description': 'Transfer updated'},
        400: {'description': 'Invalid input'},
        404: {'description': 'Transfer not found'}
    }
})
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


# -------------------- DELETE Soft Delete --------------------
@stock_transfer_bp.route("/stock_transfers/<int:id>", methods=["DELETE"])
@swag_from({
    'tags': ['Stock Transfers'],
    'summary': 'Soft delete a stock transfer',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'description': 'Stock transfer ID to delete',
            'required': True,
            'schema': {'type': 'integer'}
        }
    ],
    'responses': {
        200: {'description': 'Transfer marked as deleted'},
        404: {'description': 'Transfer not found or already deleted'},
        500: {'description': 'Database error'}
    }
})
def delete_stock_transfer(id):
    transfer = StockTransfer.query.get(id)
    if not transfer or transfer.is_deleted:
        return jsonify({"error": "Stock transfer not found or already deleted"}), 404

    try:
        transfer.is_deleted = True
        db.session.commit()
        return jsonify({"message": f"Stock transfer #{id} marked as deleted"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
