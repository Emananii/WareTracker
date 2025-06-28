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
            purchase_date=datetime.utcnow()
        )
        db.session.add(new_purchase)
        db.session.flush()  # Needed to get new_purchase.id

        for item_data in items:
            product_id = item_data["product_id"]
            quantity = int(item_data["quantity"])
            unit_cost = float(item_data["unit_cost"])

            product = Product.query.get(product_id)
            if not product:
                db.session.rollback()
                return jsonify({"error": f"Product with ID {product_id} not found."}), 404

            product.stock_level += quantity

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

        # NOTE: We are not supporting editing items directly here because
        # it would require re-calculating stock_level deltas. Handle that via a separate route if needed.

        db.session.commit()
        return jsonify(purchase.to_dict()), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400


@purchases_bp.route("/<int:id>", methods=["DELETE"])
def delete_purchase(id):
    purchase = Purchase.query.get_or_404(id)

    try:
        # Reverse all product stock changes
        for item in purchase.items:
            product = Product.query.get(item.product_id)
            if not product:
                continue

            if product.stock_level < item.quantity:
                return jsonify({
                    "error": f"Cannot delete purchase. Product '{product.name}' has insufficient stock to reverse this purchase."
                }), 400

            product.stock_level -= item.quantity

        db.session.delete(purchase)
        db.session.commit()
        return jsonify({"message": "Purchase deleted and stock levels reverted."}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
