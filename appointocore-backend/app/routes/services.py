from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.models import db, Service

service_bp = Blueprint("service_bp", __name__)


@service_bp.route("/all", methods=["GET"])
@jwt_required()
def get_services():
    claims = get_jwt()
    role = claims.get("role")
    organization_id = request.args.get("organization_id")

    if role == "Admin":
        if organization_id:
            services = Service.query.filter_by(organization_id=int(organization_id)).all()
        else:
            services = Service.query.all()
    else:
        org_id = int(claims.get("organization_id") or 0)
        services = Service.query.filter_by(organization_id=org_id).all()

    return jsonify([
        {
            "id": s.id,
            "organization_id": s.organization_id,
            "name": s.name,
            "description": s.description,
            "category": s.category,
            "price": s.price,
            "duration_minutes": s.duration_minutes,
            "active": s.active,
            "created_at": s.created_at.isoformat(),
            "updated_at": s.updated_at.isoformat() if s.updated_at else None,
        }
        for s in services
    ])


@service_bp.route("/create", methods=["POST"])
@jwt_required()
def create_service():
    claims = get_jwt()
    role = claims.get("role")
    data = request.json or {}

    if role == "Admin":
        if not data.get("organization_id"):
            return jsonify({"msg": "organization_id is required for admin-created services"}), 400
        organization_id = int(data["organization_id"])
    else:
        organization_id = int(claims.get("organization_id") or 0)

    if not data.get("name"):
        return jsonify({"msg": "name is required"}), 400

    service = Service(
        organization_id=organization_id,
        name=data["name"],
        description=data.get("description"),
        category=data.get("category"),
        price=float(data.get("price", 0.0)),
        duration_minutes=int(data.get("duration_minutes", 30)),
        active=data.get("active", True)
    )
    db.session.add(service)
    db.session.commit()

    return jsonify({"msg": "Service created successfully", "service_id": service.id}), 201


@service_bp.route("/<int:service_id>", methods=["PATCH"])
@jwt_required()
def update_service(service_id):
    claims = get_jwt()
    role = claims.get("role")
    data = request.json or {}

    service = Service.query.get_or_404(service_id)
    if role != "Admin" and service.organization_id != int(claims.get("organization_id") or 0):
        return jsonify({"msg": "Unauthorized"}), 403

    if "name" in data:
        service.name = data["name"]
    if "description" in data:
        service.description = data["description"]
    if "category" in data:
        service.category = data["category"]
    if "price" in data:
        service.price = float(data["price"])
    if "duration_minutes" in data:
        service.duration_minutes = int(data["duration_minutes"])
    if "active" in data:
        service.active = bool(data["active"])

    db.session.commit()
    return jsonify({"msg": "Service updated successfully"})


@service_bp.route("/<int:service_id>", methods=["DELETE"])
@jwt_required()
def delete_service(service_id):
    claims = get_jwt()
    role = claims.get("role")
    service = Service.query.get_or_404(service_id)

    if role != "Admin" and service.organization_id != int(claims.get("organization_id") or 0):
        return jsonify({"msg": "Unauthorized"}), 403

    db.session.delete(service)
    db.session.commit()
    return jsonify({"msg": "Service deleted successfully"})
