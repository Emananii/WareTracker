from flask import Blueprint, request, jsonify
from ..models import db, Purchase
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta

purchases_bp = Blueprint("purchases", __name__, url_prefix="/purchases")


# GET all purchases
@purchases_bp.route("/", methods=["GET"])
def get_purchases():
    purchases = Purchase.query.order_by(Purchase.purchase_date.desc()).all()
    return jsonify([p.to_dict() for p in purchases]), 200


# POST a new purchase
@purchases_bp.route("/", methods=["POST"])
def create_purchase():
    data = request.get_json()

    try:
        new_purchase = Purchase(
            supplier_id=data["supplier_id"],  # ✅ snake_case
            total_cost=float(data["total_cost"]),  # ✅ snake_case
            notes=data.get("notes"),
            purchase_date=datetime.utcnow()
        )

        db.session.add(new_purchase)
        db.session.commit()
        return jsonify(new_purchase.to_dict()), 201

    except (KeyError, SQLAlchemyError) as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


# PUT to update a purchase (only allowed within 30 days)
@purchases_bp.route("/<int:id>", methods=["PUT"])
def update_purchase(id):
    purchase = Purchase.query.get_or_404(id)
    data = request.get_json()

    # Disallow edits older than 30 days
    if datetime.utcnow() - purchase.purchase_date > timedelta(days=30):
        return jsonify({"error": "Cannot edit a purchase older than 30 days."}), 403

    try:
        # ✅ Expect snake_case field names from frontend
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


# DELETE a purchase
@purchases_bp.route("/<int:id>", methods=["DELETE"])
def delete_purchase(id):
    purchase = Purchase.query.get_or_404(id)

    try:
        db.session.delete(purchase)
        db.session.commit()
        return jsonify({"message": "Purchase deleted successfully."}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400