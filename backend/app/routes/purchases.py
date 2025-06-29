from flask import Blueprint, request, jsonify
from ..models import db, Purchase, PurchaseItem, Product
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

purchases_bp = Blueprint("purchases", __name__, url_prefix="/purchases")

# Define Nairobi timezone
EAT = ZoneInfo("Africa/Nairobi")

# ✅ GET all non-deleted purchases
@purchases_bp.route("/", methods=["GET"])
def get_purchases():
    purchases = (
        Purchase.query
        .filter(Purchase.is_deleted == False)
        .order_by(Purchase.purchase_date.desc())
        .all()
    )
    return jsonify([p.to_dict() for p in purchases]), 200

# ✅ GET single purchase if not deleted
@purchases_bp.route("/<int:id>", methods=["GET"])
def get_single_purchase(id):
    purchase = Purchase.query.filter_by(id=id, is_deleted=False).first()
    if not purchase:
        return jsonify({"error": "Purchase not found or has been deleted"}), 404
    return jsonify(purchase.to_dict()), 200

# ✅ POST: Create a new purchase with items
# ✅ POST: Create a new purchase with items
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
            purchase_date=datetime.now(EAT),  # Use Nairobi time
            is_deleted=False
        )
        db.session.add(new_purchase)
        db.session.flush()  # So new_purchase.id is available

        for item_data in items:
            product_id = item_data["product_id"]
            quantity = int(item_data["quantity"])
            unit_cost = float(item_data["unit_cost"])

            product = Product.query.get(product_id)
            if not product or product.is_deleted:
                db.session.rollback()
                return jsonify({"error": f"Product ID {product_id} is invalid or deleted."}), 400

            # ❌ REMOVE THIS:
            # product.stock_level += quantity

            # ✅ Just create the PurchaseItem
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


# ✅ PUT: Update purchase metadata (not items)
@purchases_bp.route("/<int:id>", methods=["PUT"])
def update_purchase(id):
    purchase = Purchase.query.filter_by(id=id, is_deleted=False).first()
    if not purchase:
        return jsonify({"error": "Purchase not found or already deleted."}), 404

    if datetime.now(EAT) - purchase.purchase_date > timedelta(days=30):  # 🕒 Updated
        return jsonify({"error": "Cannot edit a purchase older than 30 days."}), 403

    data = request.get_json()
    try:
        if "supplier_id" in data:
            purchase.supplier_id = data["supplier_id"]

        if "total_cost" in data:
            purchase.total_cost = float(data["total_cost"])

        if "notes" in data:
            purchase.notes = data["notes"]

        # Note: Editing items is NOT handled here.
        db.session.commit()
        return jsonify(purchase.to_dict()), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# ✅ DELETE: Soft delete purchase (no stock reversal required anymore)
@purchases_bp.route("/<int:id>", methods=["DELETE"])
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
