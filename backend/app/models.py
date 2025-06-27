from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import relationship
from datetime import datetime

db = SQLAlchemy()


class Category(db.Model, SerializerMixin):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)

    products = db.relationship(
        "Product", backref="category", cascade="all, delete-orphan")

    serialize_rules = ("-products.category",)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
        }


class Supplier(db.Model, SerializerMixin):
    __tablename__ = "suppliers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100))
    address = db.Column(db.String(255))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    is_deleted = db.Column(db.Boolean, default=False)

    serialize_rules = ("-purchases",)


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

    # New field for tracking current inventory level
    stock_level = db.Column(db.Integer, nullable=False, default=0)

    purchase_items = db.relationship(
        "PurchaseItem", backref="product", cascade="all, delete-orphan")
    stock_transfer_items = db.relationship(
        "StockTransferItem", backref="product", cascade="all, delete-orphan")

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
            "stock_level": self.stock_level,
            "category": self.category.to_dict() if self.category else None
        }


class Purchase(db.Model, SerializerMixin):
    __tablename__ = 'purchases'

    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(
        db.Integer,
        db.ForeignKey("suppliers.id", name="fk_purchases_supplier_id"),
        nullable=False
    )
    total_cost = db.Column(db.Float, nullable=False, default=0.0)
    purchase_date = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow)
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


class BusinessLocation(db.Model, SerializerMixin):
    __tablename__ = "business_locations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    address = db.Column(db.String(255))
    contact_person = db.Column(db.String(100))
    phone = db.Column(db.String(50))
    notes = db.Column(db.Text)

    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_deleted = db.Column(db.Boolean, default=False)

    # ✅ FIXED RELATIONSHIP: use back_populates instead of backref
    stock_transfers = db.relationship(
        "StockTransfer",
        back_populates="location",  # 👈 no more circular backref
        cascade="all, delete-orphan"
    )

    serialize_rules = ("-stock_transfers.location",)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "contact_person": self.contact_person,
            "phone": self.phone,
            "notes": self.notes,
            "is_active": self.is_active,
        }


class StockTransfer(db.Model, SerializerMixin):
    __tablename__ = "stock_transfers"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    transfer_type = db.Column(db.String(10), nullable=False)

    location_id = db.Column(
        db.Integer,
        db.ForeignKey("business_locations.id", name="fk_stock_transfers_location_id"),
        nullable=True
    )

    # ✅ FIXED RELATIONSHIP: use back_populates instead of defining backref
    location = db.relationship("BusinessLocation", back_populates="stock_transfers")

    notes = db.Column(db.Text)
    is_deleted = db.Column(db.Boolean, default=False)

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
            "transfer_type": self.transfer_type,
            "location_id": self.location_id,
            "location": self.location.to_dict() if self.location else None,
            "notes": self.notes,
            "is_deleted": self.is_deleted,
            "items": [item.to_dict() for item in self.items]
        }


class StockTransferItem(db.Model, SerializerMixin):
    __tablename__ = "stock_transfer_items"

    id = db.Column(db.Integer, primary_key=True)
    stock_transfer_id = db.Column(
        db.Integer,
        db.ForeignKey("stock_transfers.id",
                      name="fk_stock_transfer_items_transfer_id", ondelete="CASCADE"),
        nullable=False
    )
    product_id = db.Column(
        db.Integer,
        db.ForeignKey(
            "products.id", name="fk_stock_transfer_items_product_id"),
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
