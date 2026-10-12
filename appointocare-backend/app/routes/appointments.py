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

    staff_name = data.get("staff_name")
    treatment_room = data.get("treatment_room") or data.get("room") or data.get("resource_id")
    check_conflict = data.get("check_conflict", False)
    if check_conflict and not data.get("allow_conflict", False):
        from datetime import timedelta
        slot_start = appointment_date - timedelta(minutes=29)
        slot_end = appointment_date + timedelta(minutes=29)
        if staff_name:
            conflict = Appointment.query.filter(
                Appointment.organization_id == org_id,
                Appointment.staff_name == staff_name,
                Appointment.status.notin_(["Cancelled", "Completed", "No-Show"]),
                Appointment.appointment_date >= slot_start,
                Appointment.appointment_date <= slot_end
            ).first()
            if conflict:
                return jsonify({
                    "msg": f"Practitioner '{staff_name}' already has a booking at this time",
                    "conflict_appointment_id": conflict.id,
                    "conflict_time": conflict.appointment_date.isoformat()
                }), 409

        if treatment_room:
            room_conflict = Appointment.query.filter(
                Appointment.organization_id == org_id,
                Appointment.notes.ilike(f"%[room:{treatment_room}]%"),
                Appointment.status.notin_(["Cancelled", "Completed", "No-Show"]),
                Appointment.appointment_date >= slot_start,
                Appointment.appointment_date <= slot_end
            ).first()
            if room_conflict:
                return jsonify({
                    "msg": f"Treatment room/resource '{treatment_room}' already has a booking at this time",
                    "conflict_appointment_id": room_conflict.id,
                    "conflict_time": room_conflict.appointment_date.isoformat()
                }), 409

    notes_val = data.get("notes") or ""
    if treatment_room and f"[room:{treatment_room}]" not in notes_val:
        notes_val = f"{notes_val} [room:{treatment_room}]".strip()

    appointment = Appointment(
        customer_name=data["customer_name"],
        customer_phone=data["customer_phone"],
        appointment_date=appointment_date,
        status=data.get("status", "Booked"),
        payment_status=data.get("payment_status", "Pending"),
        organization_id=org_id,
        service_name=data.get("service_name"),
        staff_name=staff_name,
        notes=notes_val or None
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

    VALID_STATUSES = ["Booked", "Confirmed", "Checked-In", "In-Consultation", "Completed", "Cancelled", "No-Show"]
    if "status" in data:
        if data["status"] not in VALID_STATUSES:
            return jsonify({"msg": f"Invalid status '{data['status']}'. Must be one of: {', '.join(VALID_STATUSES)}"}), 400
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
# Check-in Appointment
# -------------------------------
@appointment_bp.route("/<int:appointment_id>/check-in", methods=["POST"])
@jwt_required()
def check_in_appointment(appointment_id):
    claims = get_jwt()
    role = claims.get("role")
    if not _is_authorized(role, claims):
        return jsonify({"msg": "Unauthorized"}), 403

    appointment = Appointment.query.get_or_404(appointment_id)
    if role not in ["Admin", "SuperAdmin"]:
        org_id = int(claims.get("organization_id") or get_jwt_identity())
        if int(appointment.organization_id) != org_id:
            return jsonify({"msg": "Unauthorized"}), 403

    appointment.status = "Checked-In"
    db.session.commit()
    return jsonify({
        "msg": f"Patient {appointment.customer_name} checked in successfully",
        "appointment_id": appointment.id,
        "status": appointment.status
    })


# -------------------------------
# Cancel Appointment
# -------------------------------
@appointment_bp.route("/<int:appointment_id>/cancel", methods=["POST"])
@jwt_required()
def cancel_appointment(appointment_id):
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
    reason = data.get("reason", "Cancelled by clinic/patient")
    appointment.status = "Cancelled"
    appointment.notes = f"{appointment.notes or ''} [Cancelled: {reason}]".strip()
    db.session.commit()
    return jsonify({
        "msg": "Appointment cancelled successfully",
        "appointment_id": appointment.id,
        "status": appointment.status
    })


# -------------------------------
# Reschedule Appointment
# -------------------------------
@appointment_bp.route("/<int:appointment_id>/reschedule", methods=["POST"])
@jwt_required()
def reschedule_appointment(appointment_id):
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
    new_date_str = data.get("appointment_date")
    if not new_date_str:
        return jsonify({"msg": "appointment_date is required"}), 400

    try:
        new_date = datetime.fromisoformat(new_date_str.replace("Z", "+00:00") if isinstance(new_date_str, str) else str(new_date_str))
    except Exception:
        return jsonify({"msg": "Invalid appointment_date format"}), 400

    appointment.appointment_date = new_date
    appointment.status = "Booked"
    db.session.commit()
    return jsonify({
        "msg": "Appointment rescheduled successfully",
        "appointment_id": appointment.id,
        "new_date": appointment.appointment_date.isoformat(),
        "status": appointment.status
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
