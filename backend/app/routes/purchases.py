from flask import Blueprint, request, jsonify
from ..models import db, Purchase, PurchaseItem, Product
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from flasgger import swag_from

purchases_bp = Blueprint("purchases", __name__, url_prefix="/purchases")

EAT = ZoneInfo("Africa/Nairobi")


@purchases_bp.route("/", methods=["GET"])
@swag_from({
    'tags': ['Purchases'],
    'summary': 'Get all purchases',
    'description': 'Retrieves a list of all non-deleted purchase records, sorted by date (most recent first).',
    'responses': {
        200: {
            'description': 'List of purchases',
            'content': {
                'application/json': {
                    'example': [
                        {
                            "id": 1,
                            "supplier_id": 1,
                            "total_cost": 10000.0,
                            "purchase_date": "2024-06-20T14:23:00+03:00",
                            "notes": "Sample purchase",
                            "items": []
                        }
                    ]
                }
            }
        }
    }
})
def get_purchases():
    purchases = (
        Purchase.query
        .filter(Purchase.is_deleted == False)
        .order_by(Purchase.purchase_date.desc())
        .all()
    )
    return jsonify([p.to_dict() for p in purchases]), 200


@purchases_bp.route("/<int:id>", methods=["GET"])
@swag_from({
    'tags': ['Purchases'],
    'summary': 'Get a single purchase by ID',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'description': 'The ID of the purchase',
            'required': True,
            'schema': {'type': 'integer'}
        }
    ],
    'responses': {
        200: {
            'description': 'The requested purchase',
            'content': {
                'application/json': {
                    'example': {
                        "id": 1,
                        "supplier_id": 1,
                        "total_cost": 10000.0,
                        "purchase_date": "2024-06-20T14:23:00+03:00",
                        "notes": "Sample purchase",
                        "items": []
                    }
                }
            }
        },
        404: {
            'description': 'Purchase not found or has been deleted'
        }
    }
})
def get_single_purchase(id):
    purchase = Purchase.query.filter_by(id=id, is_deleted=False).first()
    if not purchase:
        return jsonify({"error": "Purchase not found or has been deleted"}), 404
    return jsonify(purchase.to_dict()), 200


@purchases_bp.route("", methods=["POST"])
@swag_from({
    'tags': ['Purchases'],
    'summary': 'Create a new purchase',
    'description': 'Creates a new purchase with associated purchase items.',
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'example': {
                    "supplier_id": 1,
                    "total_cost": 5000.0,
                    "notes": "This is a new stock entry.",
                    "items": [
                        {
                            "product_id": 2,
                            "quantity": 20,
                            "unit_cost": 250.0
                        }
                    ]
                }
            }
        }
    },
    'responses': {
        201: {
            'description': 'Purchase created successfully'
        },
        400: {
            'description': 'Missing fields or invalid references'
        }
    }
})
def create_purchase():
    data = request.get_json()
    try:
        supplier_id = data["supplier_id"]
        total_cost = float(data["total_cost"])
        notes = data.get("notes", "")
        items = data.get("items", [])

        if not items:
            return jsonify({"error": "At least one purchase item is required."}), 400

        new_purchase = Purchase(
            supplier_id=supplier_id,
            total_cost=total_cost,
            notes=notes,
            purchase_date=datetime.now(EAT),
            is_deleted=False
        )
        db.session.add(new_purchase)
        db.session.flush()

        for item_data in items:
            product_id = item_data["product_id"]
            quantity = int(item_data["quantity"])
            unit_cost = float(item_data["unit_cost"])

            product = Product.query.get(product_id)
            if not product or product.is_deleted:
                db.session.rollback()
                return jsonify({"error": f"Product ID {product_id} is invalid or deleted."}), 400

            purchase_item = PurchaseItem(
                purchase_id=new_purchase.id,
                product_id=product_id,
                quantity=quantity,
                unit_cost=unit_cost
            )
            db.session.add(purchase_item)

        db.session.commit()
        return jsonify(new_purchase.to_dict()), 201

    except (KeyError, SQLAlchemyError, ValueError) as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@purchases_bp.route("/<int:id>", methods=["PUT"])
@swag_from({
    'tags': ['Purchases'],
    'summary': 'Update a purchase',
    'description': 'Update metadata for an existing purchase (supplier, cost, notes). Items not included.',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'required': True,
            'description': 'Purchase ID to update',
            'schema': {'type': 'integer'}
        }
    ],
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'example': {
                    "supplier_id": 2,
                    "total_cost": 5500.0,
                    "notes": "Updated supplier and cost"
                }
            }
        }
    },
    'responses': {
        200: {
            'description': 'Purchase updated'
        },
        403: {
            'description': 'Purchase too old to edit (over 30 days)'
        },
        404: {
            'description': 'Purchase not found'
        },
        400: {
            'description': 'Bad input data'
        }
    }
})
def update_purchase(id):
    purchase = Purchase.query.filter_by(id=id, is_deleted=False).first()
    if not purchase:
        return jsonify({"error": "Purchase not found or already deleted."}), 404

    if datetime.now(EAT) - purchase.purchase_date > timedelta(days=30):
        return jsonify({"error": "Cannot edit a purchase older than 30 days."}), 403

    data = request.get_json()
    try:
        if "supplier_id" in data:
            purchase.supplier_id = data["supplier_id"]
        if "total_cost" in data:
            purchase.total_cost = float(data["total_cost"])
        if "notes" in data:
            purchase.notes = data["notes"]

        db.session.commit()
        return jsonify(purchase.to_dict()), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@purchases_bp.route("/<int:id>", methods=["DELETE"])
@swag_from({
    'tags': ['Purchases'],
    'summary': 'Delete a purchase',
    'description': 'Soft deletes a purchase record (does not reverse stock changes).',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'required': True,
            'schema': {'type': 'integer'}
        }
    ],
    'responses': {
        200: {
            'description': 'Purchase soft-deleted successfully'
        },
        404: {
            'description': 'Purchase not found or already deleted'
        },
        400: {
            'description': 'Error deleting purchase'
        }
    }
})
def delete_purchase(id):
    purchase = Purchase.query.filter_by(id=id, is_deleted=False).first()
    if not purchase:
        return jsonify({"error": "Purchase not found or already deleted"}), 404

    try:
        purchase.is_deleted = True
        db.session.commit()
        return jsonify({"message": "Purchase soft-deleted successfully."}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
