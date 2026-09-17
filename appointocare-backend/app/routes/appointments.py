from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from app.models import db, Appointment, AppointmentTransaction
from datetime import datetime

appointment_bp = Blueprint("appointment_bp", __name__)

ALLOWED_ROLES = [
    "Admin", "SuperAdmin", "Organization", "Manager", "Staff",
    "Doctor", "Therapist", "Stylist", "Advisor", "Analyst", "Underwriter",
    "Broker", "Consultant", "Specialist", "Counselor", "Partner",
    "Receptionist", "Agent", "Lawyer", "Nurse", "Accountant", "Assistant"
]


def _is_authorized(role, claims):
    return (
        role in ALLOWED_ROLES or
        role in ["Admin", "SuperAdmin"] or
        bool(claims.get("organization_id"))
    )


# -------------------------------
# Create Appointment
# -------------------------------
@appointment_bp.route("", methods=["POST"])
@appointment_bp.route("/create", methods=["POST"])
@jwt_required()
def create_appointment():
    claims = get_jwt()
    role = claims.get("role")
    if not _is_authorized(role, claims):
        return jsonify({"msg": "Unauthorized"}), 403

    data = request.json or {}
    if role in ["Admin", "SuperAdmin"]:
        target_org = data.get("organization_id")
        if target_org:
            org_id = int(target_org)
        elif claims.get("organization_id"):
            org_id = int(claims.get("organization_id"))
        else:
            org_id = 1
        user_id = int(get_jwt_identity())
    else:
        org_id = int(claims.get("organization_id") or data.get("organization_id") or get_jwt_identity())
        user_id = int(get_jwt_identity())

    required_fields = ["customer_name", "customer_phone", "appointment_date"]
    for field in required_fields:
        if field not in data:
            return jsonify({"msg": f"Missing field: {field}"}), 400

    try:
        date_str = data["appointment_date"].replace("Z", "+00:00") if isinstance(data["appointment_date"], str) else str(data["appointment_date"])
        appointment_date = datetime.fromisoformat(date_str)
    except Exception:
        appointment_date = datetime.utcnow()

    amount = float(data.get("amount") or 0.0)

    appointment = Appointment(
        customer_name=data["customer_name"],
        customer_phone=data["customer_phone"],
        appointment_date=appointment_date,
        status=data.get("status", "Booked"),
        payment_status=data.get("payment_status", "Pending"),
        organization_id=org_id,
        service_name=data.get("service_name"),
        staff_name=data.get("staff_name"),
        notes=data.get("notes")
    )
    db.session.add(appointment)
    db.session.flush()

    transaction = AppointmentTransaction(
        appointment_id=appointment.id,
        organization_id=org_id,
        amount=amount,
        transaction_type=data.get("transaction_type", "Payment"),
        payment_method=data.get("payment_method", "Unknown"),
        processed_by_type=role,
        processed_by_id=user_id,
        status=data.get("transaction_status", "Pending")
    )
    db.session.add(transaction)
    db.session.commit()

    return jsonify({
        "msg": "Appointment created successfully",
        "appointment_id": appointment.id,
        "transaction_id": transaction.id,
        "id": appointment.id,
        "customer_name": appointment.customer_name,
        "service_name": appointment.service_name,
        "staff_name": appointment.staff_name,
        "notes": appointment.notes,
        "appointment_date": appointment.appointment_date.isoformat(),
        "status": appointment.status,
        "payment_status": appointment.payment_status,
        "organization_id": appointment.organization_id
    }), 201


# -------------------------------
# Update Appointment
# -------------------------------
@appointment_bp.route("/<int:appointment_id>", methods=["PATCH", "PUT"])
@jwt_required()
def update_appointment(appointment_id):
    claims = get_jwt()
    role = claims.get("role")
    if not _is_authorized(role, claims):
        return jsonify({"msg": "Unauthorized"}), 403

    appointment = Appointment.query.get_or_404(appointment_id)
    if role not in ["Admin", "SuperAdmin"]:
        org_id = int(claims.get("organization_id") or get_jwt_identity())
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

    if "service_name" in data:
        appointment.service_name = data["service_name"]

    if "notes" in data:
        appointment.notes = data["notes"]

    db.session.commit()

    return jsonify({
        "msg": "Appointment updated successfully",
        "appointment": {
            "id": appointment.id,
            "customer_name": appointment.customer_name,
            "service_name": appointment.service_name,
            "staff_name": appointment.staff_name,
            "notes": appointment.notes,
            "appointment_date": appointment.appointment_date.isoformat(),
            "status": appointment.status,
            "payment_status": appointment.payment_status,
            "organization_id": appointment.organization_id
        }
    })


# -------------------------------
# Delete Appointment
# -------------------------------
@appointment_bp.route("/<int:appointment_id>", methods=["DELETE"])
@jwt_required()
def delete_appointment(appointment_id):
    claims = get_jwt()
    role = claims.get("role")
    if not _is_authorized(role, claims):
        return jsonify({"msg": "Unauthorized"}), 403

    appointment = Appointment.query.get_or_404(appointment_id)
    if role not in ["Admin", "SuperAdmin"]:
        org_id = int(claims.get("organization_id") or get_jwt_identity())
        if int(appointment.organization_id) != org_id:
            return jsonify({"msg": "Unauthorized"}), 403

    # Delete associated transactions first (FK constraint)
    AppointmentTransaction.query.filter_by(appointment_id=appointment_id).delete()
    db.session.delete(appointment)
    db.session.commit()
    return jsonify({"msg": "Appointment deleted successfully"})


# -------------------------------
# Get Appointments
# -------------------------------
@appointment_bp.route("", methods=["GET"])
@appointment_bp.route("/all", methods=["GET"])
@jwt_required()
def get_appointments():
    claims = get_jwt()
    role = claims.get("role")
    if not _is_authorized(role, claims):
        return jsonify({"msg": "Unauthorized"}), 403

    query = Appointment.query

    if role in ["Admin", "SuperAdmin"]:
        org_param = request.args.get("organization_id")
        if org_param and org_param != "all":
            query = query.filter_by(organization_id=int(org_param))
    else:
        org_id = int(claims.get("organization_id") or get_jwt_identity())
        query = query.filter_by(organization_id=org_id)

    status_filter = request.args.get("status")
    if status_filter and status_filter != "ALL":
        query = query.filter_by(status=status_filter)

    appointments = query.order_by(Appointment.appointment_date.desc()).all()

    result = []
    for a in appointments:
        txn = AppointmentTransaction.query.filter_by(appointment_id=a.id).order_by(
            AppointmentTransaction.created_at.desc()
        ).first()

        result.append({
            "id": a.id,
            "organization_id": a.organization_id,
            "customer_name": a.customer_name,
            "customer_phone": a.customer_phone,
            "service_name": a.service_name,
            "staff_name": a.staff_name,
            "notes": a.notes,
            "appointment_date": a.appointment_date.isoformat(),
            "status": a.status,
            "payment_status": a.payment_status,
            "amount": txn.amount if txn else None,
            "payment_method": txn.payment_method if txn else None,
            "transaction_status": txn.status if txn else None,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "updated_at": a.updated_at.isoformat() if a.updated_at else None
        })

    return jsonify(result)
