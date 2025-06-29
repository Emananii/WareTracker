from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_, false
from flasgger import swag_from
from ..models import db, Supplier

suppliers_bp = Blueprint("suppliers", __name__, url_prefix="/suppliers")


# -------------------- GET ALL SUPPLIERS --------------------
@suppliers_bp.route("", methods=["GET"])
@suppliers_bp.route("/", methods=["GET"])
@swag_from({
    'tags': ['Suppliers'],
    'summary': 'Get all active (non-deleted) suppliers',
    'responses': {
        200: {
            'description': 'List of suppliers',
            'content': {
                'application/json': {
                    'example': [
                        {
                            "id": 1,
                            "name": "Acme Supplies",
                            "contact": "acme@example.com",
                            "address": "123 Nairobi Street",
                            "notes": "Preferred partner",
                            "is_deleted": False
                        }
                    ]
                }
            }
        }
    }
})
def get_suppliers():
    suppliers = Supplier.query.filter(
        or_(Supplier.is_deleted == false(), Supplier.is_deleted == None)
    ).all()
    return jsonify([s.to_dict() for s in suppliers]), 200


# -------------------- GET SINGLE SUPPLIER --------------------
@suppliers_bp.route("/<int:id>", methods=["GET"])
@swag_from({
    'tags': ['Suppliers'],
    'summary': 'Get a specific supplier by ID',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'required': True,
            'schema': {'type': 'integer'}
        }
    ],
    'responses': {
        200: {'description': 'Supplier found'},
        404: {'description': 'Supplier not found or soft-deleted'}
    }
})
def get_supplier(id):
    supplier = Supplier.query.get_or_404(id)

    if supplier.is_deleted:
        return jsonify({"error": f"Supplier #{id} not found"}), 404

    return jsonify(supplier.to_dict()), 200


# -------------------- CREATE SUPPLIER --------------------
@suppliers_bp.route("", methods=["POST"])
@swag_from({
    'tags': ['Suppliers'],
    'summary': 'Create a new supplier',
    'requestBody': {
        'required': True,
        'content': {
            'application/json': {
                'example': {
                    "name": "New Supplier",
                    "contact": "contact@example.com",
                    "address": "Mombasa Road",
                    "notes": "Bulk supplier"
                }
            }
        }
    },
    'responses': {
        201: {'description': 'Supplier created successfully'},
        400: {'description': 'Missing required field or bad request'},
        500: {'description': 'Internal server error'}
    }
})
def create_supplier():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    try:
        supplier = Supplier(
            name=data["name"],
            contact=data.get("contact", ""),
            address=data.get("address", ""),
            notes=data.get("notes", ""),
            is_deleted=False
        )
        db.session.add(supplier)
        db.session.commit()
        return jsonify(supplier.to_dict()), 201

    except KeyError:
        return jsonify({"error": "Missing required field: name"}), 400

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# -------------------- UPDATE SUPPLIER --------------------
@suppliers_bp.route("/<int:id>", methods=["PUT"])
@swag_from({
    'tags': ['Suppliers'],
    'summary': 'Update an existing supplier',
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
                    "name": "Updated Supplier Name",
                    "contact": "newcontact@example.com",
                    "address": "New Location",
                    "notes": "Changed supplier details"
                }
            }
        }
    },
    'responses': {
        200: {'description': 'Supplier updated'},
        400: {'description': 'Bad request or validation error'},
        404: {'description': 'Supplier not found'},
        500: {'description': 'Database commit error'}
    }
})
def update_supplier(id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    supplier = Supplier.query.get_or_404(id)

    if supplier.is_deleted:
        return jsonify({"error": f"Supplier #{id} not found"}), 404

    try:
        supplier.name = data.get("name", supplier.name)
        supplier.contact = data.get("contact", supplier.contact)
        supplier.address = data.get("address", supplier.address)
        supplier.notes = data.get("notes", supplier.notes)

        db.session.commit()
        return jsonify(supplier.to_dict()), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# -------------------- DELETE SUPPLIER (Soft) --------------------
@suppliers_bp.route("/<int:id>", methods=["DELETE"])
@swag_from({
    'tags': ['Suppliers'],
    'summary': 'Soft delete a supplier',
    'parameters': [
        {
            'name': 'id',
            'in': 'path',
            'required': True,
            'schema': {'type': 'integer'}
        }
    ],
    'responses': {
        200: {'description': 'Supplier soft-deleted'},
        400: {'description': 'Supplier already deleted'},
        500: {'description': 'Database error'}
    }
})
def delete_supplier(id):
    supplier = Supplier.query.get_or_404(id)

    if supplier.is_deleted:
        return jsonify({"message": f"Supplier #{id} already deleted"}), 400

    try:
        supplier.is_deleted = True
        db.session.commit()
        return jsonify({"message": f"Supplier #{id} soft-deleted"}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
