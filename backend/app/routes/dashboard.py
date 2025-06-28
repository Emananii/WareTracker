from flask import Blueprint, jsonify
from ..models import db, Product, Purchase, StockTransfer
from datetime import datetime, timedelta

dashboard_bp = Blueprint("dashboard_routes", __name__)

# 📊 STOCK SUMMARY
@dashboard_bp.route("/dashboard/summary", methods=["GET"])
def dashboard_summary():
    products = Product.query.all()

    total_items = len(products)
    total_stock = sum(p.stock_level for p in products)
    low_stock_count = sum(1 for p in products if p.stock_level <= 5)
    out_of_stock_count = sum(1 for p in products if p.stock_level == 0)

    return jsonify({
        "total_items": total_items,
        "total_stock": total_stock,
        "low_stock_count": low_stock_count,
        "out_of_stock_count": out_of_stock_count
    }), 200


# 🔁 RECENT ACTIVITY (Last 7 Days)
@dashboard_bp.route("/dashboard/recent-activity", methods=["GET"])
def dashboard_recent_activity():
    seven_days_ago = datetime.utcnow() - timedelta(days=7)

    purchases = Purchase.query.filter(Purchase.purchase_date >= seven_days_ago).order_by(Purchase.purchase_date.desc()).all()
    transfers = StockTransfer.query.filter(StockTransfer.date >= seven_days_ago).order_by(StockTransfer.date.desc()).all()

    return jsonify({
        "recent_purchases": [p.to_dict() for p in purchases],
        "recent_transfers": [t.to_dict() for t in transfers]
    }), 200
