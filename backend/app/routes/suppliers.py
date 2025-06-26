from flask import Blueprint, request, jsonify
from ..models import db, Supplier
from sqlalchemy.exc import SQLAlchemyError

suppliers_bp = Blueprint("suppliers", __name__, url_prefix="/suppliers")

@suppliers_bp.route("/", methods=["GET"])
def get_suppliers():
    suppliers = Supplier.query.all()
    return jsonify([s.to_dict() for s in suppliers]), 200


@suppliers_bp.route("/", methods=["POST"])
def create_supplier():
    data = request.get_json()

    try:
        supplier = Supplier(
            name=data["name"],
            contact=data.get("contact"),
            address=data.get("address"),
            notes=data.get("notes"),
        )
        db.session.add(supplier)
        db.session.commit()
        return jsonify(supplier.to_dict()), 201
    except (KeyError, SQLAlchemyError) as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@suppliers_bp.route("/<int:id>", methods=["PUT"])
def update_supplier(id):
    data = request.get_json()
    supplier = Supplier.query.get_or_404(id)

    try:
        supplier.name = data.get("name", supplier.name)
        supplier.contact = data.get("contact", supplier.contact)
        supplier.address = data.get("address", supplier.address)
        supplier.notes = data.get("notes", supplier.notes)
        db.session.commit()
        return jsonify(supplier.to_dict()), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@suppliers_bp.route("/<int:id>", methods=["DELETE"])
def delete_supplier(id):
    supplier = Supplier.query.get_or_404(id)
    try:
        db.session.delete(supplier)
        db.session.commit()
        return jsonify({"message": "Supplier deleted"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
