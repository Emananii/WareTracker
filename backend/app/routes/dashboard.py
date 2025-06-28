from flask import Blueprint, jsonify
from ..models import db, Product, Purchase, StockTransfer
from datetime import datetime, timedelta

dashboard_bp = Blueprint("dashboard_routes", __name__)

@dashboard_bp.route("/dashboard/summary", methods=["GET"])
def dashboard_summary():
    # 🔢 Product Metrics
    products = Product.query.all()

    total_items = len(products)
    total_stock = sum(p.stock_level for p in products)
    
    low_stock_items = [p for p in products if 0 < p.stock_level <= 5]
    out_of_stock_items = [p for p in products if p.stock_level == 0]

    # 🔁 Recent Activity
    seven_days_ago = datetime.utcnow() - timedelta(days=7)

    purchases = Purchase.query.filter(
        Purchase.purchase_date >= seven_days_ago
    ).order_by(Purchase.purchase_date.desc()).limit(5).all()

    transfers = StockTransfer.query.filter(
        StockTransfer.date >= seven_days_ago,
        StockTransfer.is_deleted == False
    ).order_by(StockTransfer.date.desc()).limit(5).all()

    # ✨ Respond with summarized + detailed low stock data
    return jsonify({
        "total_items": total_items,
        "total_stock": total_stock,
        "low_stock_count": len(low_stock_items),
        "out_of_stock_count": len(out_of_stock_items),
        "low_stock_items": [
            {
                "id": p.id,
                "name": p.name,
                "stock_level": p.stock_level,
                "category": p.category.name if p.category else None
            } for p in low_stock_items
        ],
        "out_of_stock_items": [
            {
                "id": p.id,
                "name": p.name,
                "stock_level": p.stock_level,
                "category": p.category.name if p.category else None
            } for p in out_of_stock_items
        ],
        "recent_purchases": [p.to_dict() for p in purchases],
        "recent_transfers": [t.to_dict() for t in transfers],
    }), 200
