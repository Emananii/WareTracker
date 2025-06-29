from flask import Blueprint, jsonify
from ..models import db, Product, Purchase, StockTransfer, Supplier
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from sqlalchemy import func
from flasgger import swag_from

dashboard_bp = Blueprint("dashboard_routes", __name__)

# Define East Africa Timezone
EAT = ZoneInfo("Africa/Nairobi")


@dashboard_bp.route("/dashboard/summary", methods=["GET"])
@swag_from({
    'tags': ['Dashboard'],
    'summary': 'Get a dashboard summary with inventory, stock, purchases, and trends',
    'description': 'Provides a high-level summary of inventory stats, recent activities, and top supplier trends.',
    'responses': {
        200: {
            'description': 'Dashboard summary data',
            'content': {
                'application/json': {
                    'example': {
                        "total_items": 10,
                        "total_stock": 265,
                        "low_stock_count": 2,
                        "out_of_stock_count": 1,
                        "inventory_value": 4523.75,
                        "total_purchase_value": 12000.0,
                        "low_stock_items": [...],
                        "out_of_stock_items": [...],
                        "recent_purchases": [...],
                        "recent_transfers": [...],
                        "supplier_spending_trends": [...]
                    }
                }
            }
        }
    }
})
def dashboard_summary():
    products = Product.query.all()

    total_items = len(products)
    total_stock = sum(p.stock_level for p in products)

    # Identify products with low or no stock
    low_stock_items = [p for p in products if 0 < p.stock_level <= 5]
    out_of_stock_items = [p for p in products if p.stock_level == 0]

    now = datetime.now(EAT)
    seven_days_ago = now - timedelta(days=7)

    # Get recent purchases and transfers (last 7 days)
    purchases = Purchase.query.filter(
        Purchase.purchase_date >= seven_days_ago,
        Purchase.is_deleted == False
    ).order_by(Purchase.purchase_date.desc()).limit(5).all()

    transfers = StockTransfer.query.filter(
        StockTransfer.date >= seven_days_ago,
        StockTransfer.is_deleted == False
    ).order_by(StockTransfer.date.desc()).limit(5).all()

    # Calculate current inventory value based on latest non-deleted purchase
    inventory_value = 0.0
    for product in products:
        latest_purchase_item = None
        for pi in sorted(
            product.purchase_items,
            key=lambda x: x.purchase.purchase_date if x.purchase else datetime.min,
            reverse=True
        ):
            if pi.purchase and not pi.purchase.is_deleted:
                latest_purchase_item = pi
                break
        if latest_purchase_item:
            inventory_value += product.stock_level * latest_purchase_item.unit_cost

    # Get total value of all non-deleted purchases
    total_purchase_value = db.session.query(
        db.func.sum(Purchase.total_cost)
    ).filter(Purchase.is_deleted == False).scalar() or 0.0

    # Aggregate supplier spending
    supplier_spending = (
        db.session.query(
            Supplier.id,
            Supplier.name,
            func.sum(Purchase.total_cost).label('total_spent')
        )
        .join(Purchase, Supplier.id == Purchase.supplier_id)
        .filter(Purchase.is_deleted == False)
        .group_by(Supplier.id)
        .order_by(func.sum(Purchase.total_cost).desc())
        .limit(5)
        .all()
    )

    supplier_spending_trends = [
        {
            "supplier_id": s.id,
            "supplier_name": s.name,
            "total_spent": float(s.total_spent)
        } for s in supplier_spending
    ]

    return jsonify({
        "total_items": total_items,
        "total_stock": total_stock,
        "low_stock_count": len(low_stock_items),
        "out_of_stock_count": len(out_of_stock_items),
        "inventory_value": round(inventory_value, 2),
        "total_purchase_value": round(total_purchase_value, 2),
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
        "recent_purchases": [
            {
                **p.to_dict(),
                "purchase_date": p.purchase_date.replace(tzinfo=EAT).isoformat()
            } for p in purchases
        ],
        "recent_transfers": [
            {
                **t.to_dict(),
                "date": t.date.replace(tzinfo=EAT).isoformat()
            } for t in transfers
        ],
        "supplier_spending_trends": supplier_spending_trends
    }), 200


@dashboard_bp.route("/dashboard/movements", methods=["GET"])
@swag_from({
    'tags': ['Dashboard'],
    'summary': 'Get recent inventory movements (purchases and transfers)',
    'description': 'Returns a list of inventory movement activities in the past 7 days',
    'responses': {
        200: {
            'description': 'List of movements',
            'content': {
                'application/json': {
                    'example': [
                        {
                            "id": 12,
                            "date": "2025-06-28T14:30:00+03:00",
                            "type": "PURCHASE",
                            "quantity": 150,
                            "notes": "Weekly restock",
                            "source_or_destination": "Fresh Market"
                        },
                        {
                            "id": 9,
                            "date": "2025-06-27T10:00:00+03:00",
                            "type": "OUT",
                            "quantity": 45,
                            "notes": "",
                            "source_or_destination": "From Warehouse B"
                        }
                    ]
                }
            }
        }
    }
})
def dashboard_movements():
    now = datetime.now(EAT)
    seven_days_ago = now - timedelta(days=7)

    # Get all recent purchases and transfers
    recent_purchases = Purchase.query.filter(
        Purchase.purchase_date >= seven_days_ago,
        Purchase.is_deleted == False
    ).order_by(Purchase.purchase_date.desc()).all()

    recent_transfers = StockTransfer.query.filter(
        StockTransfer.date >= seven_days_ago,
        StockTransfer.is_deleted == False
    ).order_by(StockTransfer.date.desc()).all()

    movement_data = []

    # Format purchase data into movement records
    for p in recent_purchases:
        total_quantity = sum(i.quantity for i in p.items)
        movement_data.append({
            "id": p.id,
            "date": p.purchase_date.replace(tzinfo=EAT).isoformat(),
            "type": "PURCHASE",
            "quantity": total_quantity,
            "notes": p.notes or "",
            "source_or_destination": p.supplier.name if p.supplier else "Unknown Supplier"
        })

    # Format transfer data into movement records
    for t in recent_transfers:
        total_quantity = sum(i.quantity for i in t.items)
        label = f"{'To' if t.transfer_type == 'IN' else 'From'} {t.location.name}" if t.location else "No location"
        movement_data.append({
            "id": t.id,
            "date": t.date.replace(tzinfo=EAT).isoformat(),
            "type": t.transfer_type,
            "quantity": total_quantity,
            "notes": t.notes or "",
            "source_or_destination": label
        })

    # Return the 10 most recent movement events
    movement_data.sort(key=lambda x: x["date"], reverse=True)
    return jsonify(movement_data[:10]), 200
