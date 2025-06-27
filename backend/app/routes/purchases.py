from flask import Blueprint, request, jsonify
from ..models import db, Purchase, PurchaseItem, Product
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta

purchases_bp = Blueprint("purchases", __name__, url_prefix="/purchases")


@purchases_bp.route("/", methods=["GET"])
def get_purchases():
    purchases = Purchase.query.order_by(Purchase.purchase_date.desc()).all()
    return jsonify([p.to_dict() for p in purchases]), 200

@purchases_bp.route("/<int:id>", methods=["GET"])
def get_single_purchase(id):
    purchase = Purchase.query.get(id)
    if not purchase:
        return jsonify({"error": "Purchase not found"}), 404

    return jsonify(purchase.to_dict()), 200


@purchases_bp.route("", methods=["POST"])
def create_purchase():
    data = request.get_json()

    try:
        items = data.get("items", [])
        if not items or not isinstance(items, list):
            return jsonify({"error": "At least one purchase item is required."}), 400

        # Create the Purchase record
        new_purchase = Purchase(
            supplier_id=data["supplier_id"],
            notes=data.get("notes"),
            purchase_date=datetime.utcnow(),
        )
        db.session.add(new_purchase)
        db.session.flush()  # to get the new purchase.id

        total_cost = 0.0

        for item in items:
            product_id = item.get("product_id")
            quantity = item.get("quantity", 0)
            unit_cost = item.get("unit_cost", 0.0)

            if not product_id or quantity <= 0:
                continue  # skip invalid items

            # Create PurchaseItem
            purchase_item = PurchaseItem(
                purchase_id=new_purchase.id,
                product_id=product_id,
                quantity=quantity,
                unit_cost=unit_cost
            )
            db.session.add(purchase_item)

            # Update product stock level
            product = Product.query.get(product_id)
            if product:
                product.stock_level += quantity

            total_cost += quantity * unit_cost

        new_purchase.total_cost = total_cost
        db.session.commit()

        return jsonify(new_purchase.to_dict()), 201

    except (KeyError, SQLAlchemyError) as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@purchases_bp.route("/<int:id>", methods=["PUT"])
def update_purchase(id):
    purchase = Purchase.query.get_or_404(id)
    data = request.get_json()

    if datetime.utcnow() - purchase.purchase_date > timedelta(days=30):
        return jsonify({"error": "Cannot edit a purchase older than 30 days."}), 403

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
def delete_purchase(id):
    purchase = Purchase.query.get_or_404(id)

    try:
        db.session.delete(purchase)
        db.session.commit()
        return jsonify({"message": "Purchase deleted successfully."}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400