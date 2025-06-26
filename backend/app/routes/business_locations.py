from flask import Blueprint, request, jsonify
from ..models import db, BusinessLocation

business_location_bp = Blueprint("business_location_bp", __name__)

@business_location_bp.route("/business_locations", methods=["GET"])
def get_business_locations():
    locations = BusinessLocation.query.all()
    return jsonify([location.to_dict() for location in locations]), 200

@business_location_bp.route("/business_locations/<int:id>", methods=["GET"])
def get_business_location(id):
    location = BusinessLocation.query.get(id)
    if not location:
        return jsonify({"error": "Business location not found"}), 404
    return jsonify(location.to_dict()), 200

@business_location_bp.route("/business_locations", methods=["POST"])
def create_business_location():
    data = request.get_json()
    try:
        name = data["name"]
        address = data.get("address")
        contact_person = data.get("contact_person")
        phone = data.get("phone")
        notes = data.get("notes")

        # We must check for duplicate name before we post
        if BusinessLocation.query.filter_by(name=name).first():
            return jsonify({"error": "A business location with this name already exists"}), 400

        location = BusinessLocation(
            name=name,
            address=address,
            contact_person=contact_person,
            phone=phone,
            notes=notes
        )
        db.session.add(location)
        db.session.commit()
        return jsonify(location.to_dict()), 201

    except KeyError as e:
        return jsonify({"error": f"Missing required field: {str(e)}"}), 400

@business_location_bp.route("/business_locations/<int:id>", methods=["PUT"])
def update_business_location(id):
    location = BusinessLocation.query.get(id)
    if not location:
        return jsonify({"error": "Business location not found"}), 404

    data = request.get_json()

    for field in ["name", "address", "contact_person", "phone", "notes"]:
        if field in data:
            setattr(location, field, data[field])

    db.session.commit()
    return jsonify(location.to_dict()), 200

@business_location_bp.route("/business_locations/<int:id>", methods=["DELETE"])
def delete_business_location(id):
    location = BusinessLocation.query.get(id)
    if not location:
        return jsonify({"error": "Business location not found"}), 404

    if location.stock_transfers and len(location.stock_transfers) > 0:
        return jsonify({"error": "Cannot delete location with existing stock transfers"}), 400

    db.session.delete(location)
    db.session.commit()
    return jsonify({"message": f"Business location #{id} deleted"}), 200
