from app import create_app
from app.models import db, Supplier, Purchase
from datetime import datetime
import random

app = create_app()

with app.app_context():
    print("Clearing existing data...")
    Purchase.query.delete()
    Supplier.query.delete()

    print("Seeding suppliers...")
    suppliers = [
        Supplier(name="Acme Supplies Ltd", contact="Jane Doe", address="123 Industrial Area, Nairobi"),
        Supplier(name="Global Traders Co.", contact="John Smith", address="45 Warehouse Road, Mombasa"),
        Supplier(name="FreshFoods Warehouse", contact="Alice Wanjiru", address="789 Food Street, Kisumu"),
        Supplier(name="TechGear Importers", contact="Michael Otieno", address="Plot 66, Thika Highway"),
        Supplier(name="Green Earth Suppliers", contact="Wambui Karanja", address="22 Green Valley, Eldoret"),
    ]

    db.session.add_all(suppliers)
    db.session.commit()

    print("Seeding purchases...")
    purchases = [
        Purchase(supplier_id=suppliers[0].id, total_cost=2300.00, notes="Bulk restock for Q2"),
        Purchase(supplier_id=suppliers[1].id, total_cost=4890.50, notes="Monthly electronics shipment"),
        Purchase(supplier_id=suppliers[2].id, total_cost=3100.75, notes="Fresh produce weekly restock"),
        Purchase(supplier_id=suppliers[3].id, total_cost=1200.00, notes="Urgent tech accessories order"),
        Purchase(supplier_id=suppliers[4].id, total_cost=800.25, notes="Sustainable goods pilot"),
    ]

    db.session.add_all(purchases)
    db.session.commit()

    print("Seeding complete ✅")
