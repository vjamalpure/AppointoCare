from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from app.models import db, Customer, Organization

customer_bp = Blueprint("customer_bp", __name__)


@customer_bp.route("/all", methods=["GET"])
@jwt_required()
def get_customers():
    claims = get_jwt()
    role = claims.get("role")
    org_id = request.args.get("organization_id")

    if role == "Admin":
        if org_id:
            customers = Customer.query.filter_by(organization_id=int(org_id)).all()
        else:
            customers = Customer.query.all()
    else:
        org_id = int(claims.get("organization_id") or 0)
        customers = Customer.query.filter_by(organization_id=org_id).all()

    return jsonify([
        {
            "id": c.id,
            "organization_id": c.organization_id,
            "name": c.name,
            "phone": c.phone,
            "email": c.email,
            "gender": c.gender,
            "dob": c.dob.isoformat() if c.dob else None,
            "address": c.address,
            "tags": c.tags,
            "notes": c.notes,
            "source": c.source,
            "created_at": c.created_at.isoformat(),
            "updated_at": c.updated_at.isoformat() if c.updated_at else None,
        }
        for c in customers
    ])


@customer_bp.route("/create", methods=["POST"])
@jwt_required()
def create_customer():
    claims = get_jwt()
    role = claims.get("role")
    data = request.json or {}

    if role == "Admin":
        organization_id = data.get("organization_id")
        if not organization_id:
            return jsonify({"msg": "organization_id is required for admin-created customers"}), 400
    else:
        organization_id = int(claims.get("organization_id") or 0)

    if not data.get("name") or not data.get("phone"):
        return jsonify({"msg": "name and phone are required"}), 400

    customer = Customer(
        organization_id=int(organization_id),
        name=data["name"],
        phone=data["phone"],
        email=data.get("email"),
        gender=data.get("gender"),
        dob=data.get("dob"),
        address=data.get("address"),
        tags=data.get("tags"),
        notes=data.get("notes"),
        source=data.get("source")
    )
    db.session.add(customer)
    db.session.commit()

    return jsonify({"msg": "Customer created successfully", "customer_id": customer.id}), 201


@customer_bp.route("/<int:customer_id>", methods=["PATCH"])
@jwt_required()
def update_customer(customer_id):
    claims = get_jwt()
    role = claims.get("role")
    data = request.json or {}

    customer = Customer.query.get_or_404(customer_id)
    if role != "Admin" and customer.organization_id != int(claims.get("organization_id") or 0):
        return jsonify({"msg": "Unauthorized"}), 403

    if "name" in data:
        customer.name = data["name"]
    if "phone" in data:
        customer.phone = data["phone"]
    if "email" in data:
        customer.email = data["email"]
    if "gender" in data:
        customer.gender = data["gender"]
    if "dob" in data:
        customer.dob = data["dob"]
    if "address" in data:
        customer.address = data["address"]
    if "tags" in data:
        customer.tags = data["tags"]
    if "notes" in data:
        customer.notes = data["notes"]
    if "source" in data:
        customer.source = data["source"]

    db.session.commit()
    return jsonify({"msg": "Customer updated successfully"})


@customer_bp.route("/<int:customer_id>", methods=["DELETE"])
@jwt_required()
def delete_customer(customer_id):
    claims = get_jwt()
    role = claims.get("role")
    customer = Customer.query.get_or_404(customer_id)

    if role != "Admin" and customer.organization_id != int(claims.get("organization_id") or 0):
        return jsonify({"msg": "Unauthorized"}), 403

    db.session.delete(customer)
    db.session.commit()
    return jsonify({"msg": "Customer deleted successfully"})
