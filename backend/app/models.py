from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import relationship
from datetime import datetime

db = SQLAlchemy()

# ✅ Category
class Category(db.Model, SerializerMixin):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)

    products = db.relationship("Product", backref="category", cascade="all, delete-orphan")

    serialize_rules = ("-products.category",)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
        }


# ✅ Supplier
class Supplier(db.Model, SerializerMixin):
    __tablename__ = "suppliers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100))
    address = db.Column(db.String(255))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    serialize_rules = ("-purchases",)


# ✅ Product
class Product(db.Model, SerializerMixin):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    sku = db.Column(db.String(50), unique=True)
    unit = db.Column(db.String(20))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id", name="fk_products_category_id"),
        nullable=False
    )

    purchase_items = db.relationship("PurchaseItem", backref="product", cascade="all, delete-orphan")
    stock_transfer_items = db.relationship("StockTransferItem", backref="product", cascade="all, delete-orphan")

    serialize_rules = (
        '-category.products',
        '-purchase_items.product',
        '-stock_transfer_items.product',
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "sku": self.sku,
            "unit": self.unit,
            "description": self.description,
            "category_id": self.category_id,
            "category": self.category.to_dict() if self.category else None
        }


# ✅ Purchase
class Purchase(db.Model, SerializerMixin):
    __tablename__ = 'purchases'

    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(
        db.Integer,
        db.ForeignKey("suppliers.id", name="fk_purchases_supplier_id"),
        nullable=False
    )
    total_cost = db.Column(db.Float, nullable=False, default=0.0)
    purchase_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notes = db.Column(db.Text)

    supplier = relationship("Supplier", backref="purchases")

    items = relationship(
        "PurchaseItem",
        backref="purchase",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    serialize_rules = ('-supplier.purchases',)

    def to_dict(self):
        return {
            "id": self.id,
            "supplier_id": self.supplier_id,
            "total_cost": float(self.total_cost) if self.total_cost else 0.0,
            "purchase_date": self.purchase_date.isoformat() if self.purchase_date else None,
            "notes": self.notes,
            "supplier": self.supplier.to_dict() if self.supplier else None,
            "items": [item.to_dict() for item in self.items]
        }


# ✅ PurchaseItem
class PurchaseItem(db.Model, SerializerMixin):
    __tablename__ = "purchase_items"

    id = db.Column(db.Integer, primary_key=True)
    purchase_id = db.Column(
        db.Integer,
        db.ForeignKey("purchases.id", name="fk_purchase_items_purchase_id"),
        nullable=False
    )
    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id", name="fk_purchase_items_product_id"),
        nullable=False
    )

    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_cost = db.Column(db.Float, nullable=False, default=0.0)

    serialize_rules = (
        '-purchase.items',
        '-product.purchase_items',
    )

    def to_dict(self):
        return {
            "id": self.id,
            "purchase_id": self.purchase_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "unit_cost": float(self.unit_cost),
            "product": self.product.to_dict() if self.product else None
        }


# ✅ BusinessLocation
class BusinessLocation(db.Model, SerializerMixin):
    __tablename__ = "business_locations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    address = db.Column(db.String(255))
    contact_person = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    notes = db.Column(db.Text)

    stock_transfers = db.relationship("StockTransfer", backref="location", cascade="all, delete-orphan")

    serialize_rules = ("-stock_transfers.location",)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "contact_person": self.contact_person,
            "phone": self.phone,
            "notes": self.notes,
        }


# ✅ StockTransfer
class StockTransfer(db.Model, SerializerMixin):
    __tablename__ = "stock_transfers"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    location_id = db.Column(
        db.Integer,
        db.ForeignKey("business_locations.id", name="fk_stock_transfers_location_id"),
        nullable=False
    )
    notes = db.Column(db.Text)

    items = db.relationship(
        "StockTransferItem",
        backref="stock_transfer",
        cascade="all, delete-orphan",
        passive_deletes=True
    )

    serialize_rules = ("-location.stock_transfers", "-items.stock_transfer")

    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date.isoformat() if self.date else None,
            "location_id": self.location_id,
            "notes": self.notes,
            "location": self.location.to_dict() if self.location else None,
            "items": [item.to_dict() for item in self.items]
        }


# ✅ StockTransferItem
class StockTransferItem(db.Model, SerializerMixin):
    __tablename__ = "stock_transfer_items"

    id = db.Column(db.Integer, primary_key=True)
    stock_transfer_id = db.Column(
        db.Integer,
        db.ForeignKey("stock_transfers.id", name="fk_stock_transfer_items_transfer_id", ondelete="CASCADE"),
        nullable=False
    )
    product_id = db.Column(
        db.Integer,
        db.ForeignKey("products.id", name="fk_stock_transfer_items_product_id"),
        nullable=False
    )
    quantity = db.Column(db.Integer, nullable=False, default=0)

    serialize_rules = (
        '-stock_transfer.items',
        '-product.stock_transfer_items',
    )

    def to_dict(self):
        return {
            "id": self.id,
            "stock_transfer_id": self.stock_transfer_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "product": self.product.to_dict() if self.product else None
        }