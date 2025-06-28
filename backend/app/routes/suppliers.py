from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from ..models import db, Supplier

suppliers_bp = Blueprint("suppliers", __name__, url_prefix="/suppliers")


# GET all active suppliers (exclude soft-deleted)
from sqlalchemy import or_, false

@suppliers_bp.route("", methods=["GET"])
@suppliers_bp.route("/", methods=["GET"])
def get_suppliers():
    suppliers = Supplier.query.filter(
        or_(Supplier.is_deleted == false(), Supplier.is_deleted == None)
    ).all()
    return jsonify([s.to_dict() for s in suppliers]), 200


# GET a single supplier unless it's soft-deleted
@suppliers_bp.route("/<int:id>", methods=["GET"])
def get_supplier(id):
    supplier = Supplier.query.get_or_404(id)

    if supplier.is_deleted:
        return jsonify({"error": f"Supplier #{id} not found"}), 404

    return jsonify(supplier.to_dict()), 200


# CREATE a new supplier
@suppliers_bp.route("", methods=["POST"])
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
            is_deleted=False  # Explicitly set in case column default fails
        )
        db.session.add(supplier)
        db.session.commit()
        return jsonify(supplier.to_dict()), 201

    except KeyError:
        return jsonify({"error": "Missing required field: name"}), 400

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


# UPDATE an existing supplier (ignore soft-deleted)
@suppliers_bp.route("/<int:id>", methods=["PUT"])
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


# SOFT DELETE a supplier
@suppliers_bp.route("/<int:id>", methods=["DELETE"])
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
