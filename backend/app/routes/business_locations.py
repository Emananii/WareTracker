from flask import Blueprint, request, jsonify
from ..models import db, BusinessLocation

business_location_bp = Blueprint("business_location_bp", __name__)


# GET all active business locations
@business_location_bp.route("/business_locations", methods=["GET"])
def get_business_locations():
    locations = BusinessLocation.query.filter_by(is_deleted=False).all()
    return jsonify([location.to_dict() for location in locations]), 200


# GET a specific business location (active or not)
@business_location_bp.route("/business_locations/<int:id>", methods=["GET"])
def get_business_location(id):
    location = BusinessLocation.query.get(id)
    if not location:
        return jsonify({"error": "Business location not found"}), 404
    return jsonify(location.to_dict()), 200


# CREATE a new business location
@business_location_bp.route("/business_locations", methods=["POST"])
def create_business_location():
    data = request.get_json()
    try:
        name = data["name"]
        address = data.get("address")
        contact_person = data.get("contact_person")
        phone = data.get("phone")
        notes = data.get("notes")

        if BusinessLocation.query.filter_by(name=name).first():
            return jsonify({"error": "A business location with this name already exists"}), 400

        location = BusinessLocation(
            name=name,
            address=address,
            contact_person=contact_person,
            phone=phone,
            notes=notes,
            is_active=True
        )
        db.session.add(location)
        db.session.commit()
        return jsonify(location.to_dict()), 201

    except KeyError as e:
        return jsonify({"error": f"Missing required field: {str(e)}"}), 400


# UPDATE business location details
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


# TOGGLE is_active status
@business_location_bp.route("/business_locations/<int:id>/toggle_active", methods=["PATCH"])
def toggle_business_location_active(id):
    location = BusinessLocation.query.get(id)
    if not location:
        return jsonify({"error": "Business location not found"}), 404

    location.is_active = not location.is_active
    db.session.commit()
    status = "activated" if location.is_active else "deactivated"
    return jsonify({
        "message": f"Business location #{id} has been {status}.",
        "is_active": location.is_active,
        "location": location.to_dict()
    }), 200


# DELETE a business location
@business_location_bp.route("/business_locations/<int:id>/delete", methods=["PATCH"])
def soft_delete_business_location(id):
    location = BusinessLocation.query.get(id)
    if not location:
        return jsonify({"error": "Business location not found"}), 404

    location.is_deleted = True
    db.session.commit()
    return jsonify({
        "message": f"Business location #{id} has been deleted.",
        "is_deleted": location.is_deleted
    }), 200
