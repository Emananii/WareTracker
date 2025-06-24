from flask import Blueprint, request, jsonify
from app import db
from app.models import Business, QuantityType, Currency

api = Blueprint('api', __name__)

# ---------- Business Routes ----------
@api.route('/businesses', methods=['GET'])
def get_businesses():
    businesses = Business.query.all()
    return jsonify([{'id': b.id, 'name': b.name, 'address': b.address} for b in businesses])

@api.route('/businesses', methods=['POST'])
def add_business():
    data = request.get_json()
    new_biz = Business(name=data['name'], address=data.get('address', ''))
    db.session.add(new_biz)
    db.session.commit()
    return jsonify({'message': 'Business added'}), 201

# ---------- Quantity Type Routes ----------
@api.route('/quantities', methods=['GET'])
def get_quantities():
    quantities = QuantityType.query.all()
    return jsonify([{'id': q.id, 'name': q.name} for q in quantities])

@api.route('/quantities', methods=['POST'])
def add_quantity():
    data = request.get_json()
    new_quantity = QuantityType(name=data['name'])
    db.session.add(new_quantity)
    db.session.commit()
    return jsonify({'message': 'Quantity added'}), 201

# ---------- Currency Routes ----------
@api.route('/currencies', methods=['GET'])
def get_currencies():
    currencies = Currency.query.all()
    return jsonify([{'id': c.id, 'code': c.code, 'name': c.name} for c in currencies])

@api.route('/currencies', methods=['POST'])
def add_currency():
    data = request.get_json()
    new_currency = Currency(code=data['code'], name=data.get('name', ''))
    db.session.add(new_currency)
    db.session.commit()
    return jsonify({'message': 'Currency added'}), 201
