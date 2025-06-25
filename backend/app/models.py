from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import relationship  # ✅ You were missing this
from datetime import datetime

db = SQLAlchemy()

class Supplier(db.Model, SerializerMixin):
    __tablename__ = "suppliers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact = db.Column(db.String(100))  # Could be contact person or phone/email
    address = db.Column(db.String(255))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Optional: Automatically load related purchases if needed
    # purchases = db.relationship("Purchase", backref="supplier", lazy=True)

    serialize_rules = ("-purchases",)  # Avoid recursion


class Purchase(db.Model, SerializerMixin):
    __tablename__ = 'purchases'

    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.Integer, db.ForeignKey("suppliers.id"), nullable=False)
    total_cost = db.Column(db.Float, nullable=False, default=0.0)
    purchase_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    notes = db.Column(db.Text)

    # ✅ This line requires the `relationship` import
    supplier = relationship("Supplier", backref="purchases")

    serialize_rules = ('-supplier.purchases',)

    def to_dict(self):
        return {
            "id": self.id,
            "supplier_id": self.supplier_id,
            "total_cost": float(self.total_cost) if self.total_cost is not None else 0.0,
            "purchase_date": self.purchase_date.isoformat() if self.purchase_date else None,
            "notes": self.notes,
            "supplier": self.supplier.to_dict() if self.supplier else None,
        }
