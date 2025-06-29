from app import create_app
from app.models import (
    db, Supplier, Product,
    Category, BusinessLocation,
)
from datetime import datetime
import pytz

EAT = pytz.timezone("Africa/Nairobi")

app = create_app()

with app.app_context():
    print("🔄 Clearing existing data...")

    # Delete in reverse dependency order
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
        BusinessLocation(name="Flea Bottomers", address="Flea Bottom, King's Landing", contact_person="Gendry", phone="0711223344"),
        BusinessLocation(name="Winterfell Storehouse", address="Winterfell Keep", contact_person="Bran Stark", phone="0722334455"),
        BusinessLocation(name="Dragonstone Depot", address="Dragonstone Island", contact_person="Davos Seaworth", phone="0733445566"),
    ]
    db.session.add_all(locations)
    db.session.commit()

    print("🌱 Seeding suppliers...")
    suppliers = [
        Supplier(name="Jon Snow", contact="The Bastard of Winterfell", address="Castle Black, The Wall"),
        Supplier(name="Daenerys Targaryen", contact="Mother of Dragons", address="Meereen, Slaver's Bay"),
        Supplier(name="Tyrion Lannister", contact="Hand of the Queen", address="Red Keep, King's Landing"),
        Supplier(name="Arya Stark", contact="Faceless One", address="Braavos"),
        Supplier(name="Cersei Lannister", contact="Queen Regent", address="Red Keep, King's Landing"),
    ]
    db.session.add_all(suppliers)
    db.session.commit()

    print("📦 Seeding products (inventory)...")
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

    print("✅ Done seeding basic setup — categories, suppliers, inventory, and business locations.")
