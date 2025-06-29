from flask import Blueprint, request, jsonify
from ..models import db, PurchaseItem, Product, Purchase
from flasgger import swag_from

purchase_item_bp = Blueprint("purchase_item_bp", __name__)


@purchase_item_bp.route("/purchase_items", methods=["GET"])
@swag_from({
    'tags': ['Purchase Items'],
    'summary': 'Get all purchase items',
    'description': 'Returns a list of all purchase items from the database.',
    'responses': {
        200: {
            'description': 'List of purchase items',
            'content': {
                'application/json': {
                    'example': [
                        {
                            "id": 1,
                            "product_id": 2,
                            "purchase_id": 1,
                            "quantity": 20,
                            "unit_cost": 45.50
                        }
                    ]
                }
            }
        }
    }
})
def get_purchase_items():
    items = PurchaseItem.query.all()
    return jsonify([item.to_dict() for item in items]), 200


@purchase_item_bp.route("/purchase_items/<int:id>", methods=["GET"])
@swag_from({
    'tags': ['Purchase Items'],
    'summary': 'Get a purchase item by ID',
    'description': 'Retrieve a specific purchase item by its unique ID.',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'description': 'ID of the purchase item',
            'required': True,
            'schema': {'type': 'integer'}
        }
    ],
    'responses': {
        200: {
            'description': 'Purchase item found',
            'content': {
                'application/json': {
                    'example': {
                        "id": 1,
                        "product_id": 2,
                        "purchase_id": 1,
                        "quantity": 20,
                        "unit_cost": 45.50
                    }
                }
            }
        },
        404: {
            'description': 'Purchase item not found'
        }
    }
})
def get_purchase_item(id):
    item = PurchaseItem.query.get(id)
    if not item:
        return jsonify({"error": "Purchase item not found"}), 404
    return jsonify(item.to_dict()), 200


@purchase_item_bp.route("/purchase_items", methods=["POST"])
@swag_from({
    'tags': ['Purchase Items'],
    'summary': 'Create a new purchase item',
    'description': 'Adds a new purchase item with associated purchase and product references.',
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'example': {
                    "purchase_id": 1,
                    "product_id": 2,
                    "quantity": 10,
                    "unit_cost": 55.00
                }
            }
        }
    },
    'responses': {
        201: {
            'description': 'Purchase item created successfully'
        },
        400: {
            'description': 'Missing field or invalid data format'
        },
        404: {
            'description': 'Referenced purchase or product not found'
        }
    }
})
def create_purchase_item():
    data = request.get_json()
    print("Incoming data:", data)
    try:
        purchase_id = data["purchase_id"]
        product_id = data["product_id"]
        quantity = int(data.get("quantity", 1))
        unit_cost = float(data.get("unit_cost", 0))

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


@purchase_item_bp.route("/purchase_items/<int:id>", methods=["PUT"])
@swag_from({
    'tags': ['Purchase Items'],
    'summary': 'Update a purchase item',
    'description': 'Update fields like quantity, cost, product, or purchase reference for a purchase item.',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'required': True,
            'description': 'Purchase item ID',
            'schema': {'type': 'integer'}
        }
    ],
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'example': {
                    "quantity": 15,
                    "unit_cost": 50.00,
                    "product_id": 2,
                    "purchase_id": 1
                }
            }
        }
    },
    'responses': {
        200: {
            'description': 'Purchase item updated successfully'
        },
        404: {
            'description': 'Purchase item not found'
        }
    }
})
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


@purchase_item_bp.route("/purchase_items/<int:id>", methods=["DELETE"])
@swag_from({
    'tags': ['Purchase Items'],
    'summary': 'Delete a purchase item',
    'description': 'Permanently deletes a purchase item record.',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'required': True,
            'description': 'Purchase item ID',
            'schema': {'type': 'integer'}
        }
    ],
    'responses': {
        200: {
            'description': 'Purchase item deleted successfully'
        },
        404: {
            'description': 'Purchase item not found'
        }
    }
})
def delete_purchase_item(id):
    item = PurchaseItem.query.get(id)
    if not item:
        return jsonify({"error": "Purchase item not found"}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": f"Purchase item #{id} deleted"}), 200
