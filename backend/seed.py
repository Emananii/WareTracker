from app import create_app
from app.models import (
    db, Supplier, Purchase, Product, PurchaseItem,
    Category, BusinessLocation, StockTransfer, StockTransferItem
)
from datetime import datetime, timedelta
import random

app = create_app()

with app.app_context():
    print("🔄 Clearing existing data...")

    StockTransferItem.query.delete()
    StockTransfer.query.delete()
    PurchaseItem.query.delete()
    Purchase.query.delete()
    Product.query.delete()
    Supplier.query.delete()
    Category.query.delete()
    BusinessLocation.query.delete()
    db.session.commit()

    print("📚 Seeding categories...")
    categories = [
        Category(name="Groceries", description="Fresh food and produce"),
        Category(name="Electronics", description="Electronic gadgets and accessories"),
        Category(name="Stationery", description="Office and school supplies"),
        Category(name="Cleaning Supplies", description="Household and industrial cleaners"),
        Category(name="Agriculture", description="Farming inputs and supplies"),
    ]
    db.session.add_all(categories)
    db.session.commit()

    print("🏢 Seeding business locations...")
    locations = [
        BusinessLocation(name="Downtown Outlet", address="1st Avenue, Nairobi", contact_person="Mark", phone="0712345678"),
        BusinessLocation(name="Uptown Branch", address="Westlands, Nairobi", contact_person="Linda", phone="0722456789"),
        BusinessLocation(name="Industrial Area Depot", address="Mombasa Road", contact_person="Brian", phone="0733567890"),
    ]
    db.session.add_all(locations)
    db.session.commit()

    print("🌱 Seeding suppliers...")
    suppliers = [
        Supplier(name="Acme Supplies Ltd", contact="Jane Doe", address="123 Industrial Area, Nairobi"),
        Supplier(name="Global Traders Co.", contact="John Smith", address="45 Warehouse Road, Mombasa"),
        Supplier(name="FreshFoods Warehouse", contact="Alice Wanjiru", address="789 Food Street, Kisumu"),
        Supplier(name="TechGear Importers", contact="Michael Otieno", address="Plot 66, Thika Highway"),
        Supplier(name="Green Earth Suppliers", contact="Wambui Karanja", address="22 Green Valley, Eldoret"),
    ]
    db.session.add_all(suppliers)
    db.session.commit()

    print("📦 Seeding products...")
    products = [
        Product(name="Tomatoes", sku="TMT-001", unit="kg", description="Fresh red tomatoes", category_id=categories[0].id),
        Product(name="USB Cable", sku="USB-123", unit="pcs", description="USB 2.0 high-speed data cable", category_id=categories[1].id),
        Product(name="Detergent", sku="CLN-321", unit="ltr", description="5L multi-purpose cleaner", category_id=categories[3].id),
        Product(name="Notebook", sku="NTBK-456", unit="pcs", description="200-page ruled notebook", category_id=categories[2].id),
        Product(name="Fertilizer", sku="FRT-789", unit="kg", description="Organic compost fertilizer", category_id=categories[4].id),
        Product(name="LED Bulb", sku="LED-001", unit="pcs", description="Warm white 9W LED bulb", category_id=categories[1].id),
        Product(name="Cooking Oil", sku="COOK-002", unit="ltr", description="1L sunflower oil", category_id=categories[0].id),
        Product(name="Backpack", sku="BPK-101", unit="pcs", description="15-inch laptop backpack", category_id=categories[2].id),
        Product(name="Apples", sku="APL-202", unit="kg", description="Juicy red apples", category_id=categories[0].id),
        Product(name="Ink Cartridge", sku="INK-303", unit="box", description="Black ink for HP printers", category_id=categories[2].id)
    ]
    db.session.add_all(products)
    db.session.commit()

    print("🧾 Seeding purchases...")
    purchases = []

    for i in range(8):
        
        if i < 3:
            days_ago = random.randint(31, 90)
        else:
            days_ago = random.randint(0, 29)

        purchase = Purchase(
            supplier_id=suppliers[i % len(suppliers)].id,
            purchase_date=datetime.utcnow() - timedelta(days=days_ago),
            total_cost=0.0,
            notes=f"Generated purchase {i+1}"
        )
        db.session.add(purchase)
        purchases.append(purchase)

    db.session.commit()

    print("📋 Seeding purchase items...")
    for purchase in purchases:
        selected_products = random.sample(products, random.randint(2, 4))
        total_cost = 0.0

        for product in selected_products:
            quantity = random.randint(1, 10)
            unit_cost = round(random.uniform(50, 500), 2)

            item = PurchaseItem(
                purchase_id=purchase.id,
                product_id=product.id,
                quantity=quantity,
                unit_cost=unit_cost
            )
            db.session.add(item)
            total_cost += quantity * unit_cost

        purchase.total_cost = round(total_cost, 2)

    db.session.commit()

    print("🚚 Seeding stock transfers...")
    stock_transfers = []
    for i in range(3):
        transfer = StockTransfer(
            location_id=random.choice(locations).id,
            date=datetime.utcnow() - timedelta(days=random.randint(1, 10)),
            notes=f"Stock transfer #{i+1}"
        )
        db.session.add(transfer)
        stock_transfers.append(transfer)

    db.session.commit()

    print("📦 Seeding stock transfer items...")
    for transfer in stock_transfers:
        selected_products = random.sample(products, random.randint(2, 5))

        for product in selected_products:
            quantity = random.randint(1, 20)
            item = StockTransferItem(
                stock_transfer_id=transfer.id,
                product_id=product.id,
                quantity=quantity
            )
            db.session.add(item)

    db.session.commit()

    print("✅ Done seeding categories, suppliers, products, purchases, business locations, and stock transfers!")
