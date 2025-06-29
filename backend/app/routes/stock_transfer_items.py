from flask import Blueprint, request, jsonify
from ..models import db, StockTransferItem, StockTransfer, Product
from flasgger import swag_from

stock_transfer_item_bp = Blueprint("stock_transfer_item_bp", __name__)


@stock_transfer_item_bp.route("/stock_transfer_items", methods=["GET"])
@swag_from({
    'tags': ['Stock Transfer Items'],
    'summary': 'Get all stock transfer items',
    'responses': {
        200: {
            'description': 'A list of stock transfer items',
            'content': {
                'application/json': {
                    'example': [
                        {
                            "id": 1,
                            "stock_transfer_id": 2,
                            "product_id": 3,
                            "quantity": 50
                        }
                    ]
                }
            }
        }
    }
})
def get_stock_transfer_items():
    items = StockTransferItem.query.all()
    return jsonify([item.to_dict() for item in items]), 200


@stock_transfer_item_bp.route("/stock_transfer_items/<int:id>", methods=["GET"])
@swag_from({
    'tags': ['Stock Transfer Items'],
    'summary': 'Get a specific stock transfer item',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'required': True,
            'description': 'Stock transfer item ID',
            'schema': {'type': 'integer'}
        }
    ],
    'responses': {
        200: {
            'description': 'The requested stock transfer item',
            'content': {
                'application/json': {
                    'example': {
                        "id": 1,
                        "stock_transfer_id": 2,
                        "product_id": 3,
                        "quantity": 50
                    }
                }
            }
        },
        404: {
            'description': 'Item not found'
        }
    }
})
def get_stock_transfer_item(id):
    item = StockTransferItem.query.get(id)
    if not item:
        return jsonify({"error": "Stock transfer item not found"}), 404
    return jsonify(item.to_dict()), 200


@stock_transfer_item_bp.route("/stock_transfer_items", methods=["POST"])
@swag_from({
    'tags': ['Stock Transfer Items'],
    'summary': 'Create a stock transfer item',
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'example': {
                    "stock_transfer_id": 1,
                    "product_id": 5,
                    "quantity": 100
                }
            }
        }
    },
    'responses': {
        201: {
            'description': 'Item created successfully'
        },
        400: {
            'description': 'Missing fields or invalid foreign keys'
        }
    }
})
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
@swag_from({
    'tags': ['Stock Transfer Items'],
    'summary': 'Update a stock transfer item',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'description': 'ID of the item to update',
            'required': True,
            'schema': {'type': 'integer'}
        }
    ],
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'example': {
                    "quantity": 75,
                    "product_id": 6
                }
            }
        }
    },
    'responses': {
        200: {
            'description': 'Item updated successfully'
        },
        400: {
            'description': 'Invalid product ID or bad input'
        },
        404: {
            'description': 'Item not found'
        }
    }
})
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
@swag_from({
    'tags': ['Stock Transfer Items'],
    'summary': 'Delete a stock transfer item',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'description': 'ID of the stock transfer item to delete',
            'required': True,
            'schema': {'type': 'integer'}
        }
    ],
    'responses': {
        200: {
            'description': 'Item deleted successfully'
        },
        404: {
            'description': 'Item not found'
        }
    }
})
def delete_stock_transfer_item(id):
    item = StockTransferItem.query.get(id)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": f"Item #{id} deleted"}), 200
