from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from app.models import db, Appointment, AppointmentTransaction
from datetime import datetime

appointment_bp = Blueprint("appointment_bp", __name__)

# -------------------------------
# Create Appointment
# -------------------------------
@appointment_bp.route("/create", methods=["POST"])
@jwt_required()
def create_appointment():
    claims = get_jwt()
    if claims.get("role") not in ["Organization", "Manager", "Staff"]:
        return jsonify({"msg": "Unauthorized"}), 403
    org_id = int(claims.get("organization_id") or get_jwt_identity())
    user_id = int(get_jwt_identity())

    data = request.json or {}
    required_fields = ["customer_name", "customer_phone", "appointment_date", "amount"]

    for field in required_fields:
        if field not in data:
            return jsonify({"msg": f"Missing field: {field}"}), 400

    try:
        appointment_date = datetime.fromisoformat(data["appointment_date"])
    except ValueError:
        return jsonify({"msg": "Invalid date format"}), 400

    appointment = Appointment(
        customer_name=data["customer_name"],
        customer_phone=data["customer_phone"],
        appointment_date=appointment_date,
        status=data.get("status", "Booked"),
        payment_status=data.get("payment_status", "Pending"),
        organization_id=org_id
    )
    db.session.add(appointment)
    db.session.flush()

    transaction = AppointmentTransaction(
        appointment_id=appointment.id,
        organization_id=org_id,
        amount=data["amount"],
        transaction_type=data.get("transaction_type", "Payment"),
        payment_method=data.get("payment_method", "Unknown"),
        processed_by_type=claims.get("role"),
        processed_by_id=int(user_id),
        status=data.get("transaction_status", "Pending")
    )
    db.session.add(transaction)
    db.session.commit()

    return jsonify({
        "msg": "Appointment created successfully",
        "appointment_id": appointment.id,
        "transaction_id": transaction.id
    }), 201


# -------------------------------
# Update Appointment
# -------------------------------
@appointment_bp.route("/<int:appointment_id>", methods=["PATCH"])
@jwt_required()
def update_appointment(appointment_id):
    claims = get_jwt()
    user_id = get_jwt_identity()

    if claims.get("role") not in ["Organization", "Manager", "Staff"]:
        return jsonify({"msg": "Unauthorized"}), 403

    org_id = int(claims.get("organization_id") or get_jwt_identity())
    appointment = Appointment.query.get_or_404(appointment_id)

    if int(appointment.organization_id) != org_id:
        return jsonify({"msg": "Unauthorized"}), 403

    data = request.json or {}

    if "appointment_date" in data:
        try:
            appointment.appointment_date = datetime.fromisoformat(data["appointment_date"])
        except ValueError:
            return jsonify({"msg": "Invalid date format"}), 400

    if "status" in data:
        appointment.status = data["status"]

    if "payment_status" in data:
        appointment.payment_status = data["payment_status"]

    db.session.commit()

    return jsonify({
        "msg": "Appointment updated successfully",
        "appointment": {
            "id": appointment.id,
            "customer_name": appointment.customer_name,
            "appointment_date": appointment.appointment_date.isoformat(),
            "status": appointment.status,
            "payment_status": appointment.payment_status
        }
    })


# -------------------------------
# Get Appointments (Organization Only)
# -------------------------------
@appointment_bp.route("/all", methods=["GET"])
@jwt_required()
def get_appointments():
    claims = get_jwt()
    if claims.get("role") not in ["Organization", "Manager", "Staff"]:
        return jsonify({"msg": "Unauthorized"}), 403

    org_id = int(claims.get("organization_id") or get_jwt_identity())
    appointments = Appointment.query.filter_by(organization_id=org_id).all()

    result = []
    for a in appointments:
        txn = AppointmentTransaction.query.filter_by(appointment_id=a.id).order_by(
            AppointmentTransaction.created_at.desc()
        ).first()

        result.append({
            "id": a.id,
            "customer_name": a.customer_name,
            "customer_phone": a.customer_phone,
            "appointment_date": a.appointment_date.isoformat(),
            "status": a.status,
            "payment_status": a.payment_status,
            "amount": txn.amount if txn else None,
            "payment_method": txn.payment_method if txn else None,
            "transaction_status": txn.status if txn else None,
            "created_at": a.created_at.isoformat(),
            "updated_at": a.updated_at.isoformat() if a.updated_at else None
        })

    return jsonify(result)
