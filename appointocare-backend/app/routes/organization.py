from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt
from app.models import db, Organization, Appointment, AppointmentTransaction, OrganizationTransaction, MessageLog
from datetime import datetime
from sqlalchemy import extract

organization_bp = Blueprint("organization_bp", __name__)

# ------------------------------------------
# Monthly Transaction Summary (for charts)
# ------------------------------------------
@organization_bp.route("/transactions/summary", methods=["GET"])
@jwt_required()
def org_transactions_summary():
    claims = get_jwt()
    if claims.get("role") not in ["Organization", "Manager", "Staff"]:
        return jsonify({"msg": "Unauthorized"}), 403
    org_id = int(claims.get("organization_id") or claims.get("sub"))
    year = request.args.get("year", datetime.utcnow().year, type=int)

    org_monthly = db.session.query(
        extract('month', OrganizationTransaction.created_at).label('month'),
        db.func.sum(OrganizationTransaction.amount).label('total')
    ).filter(
        OrganizationTransaction.organization_id == org_id,
        extract('year', OrganizationTransaction.created_at) == year
    ).group_by('month').all()

    appt_monthly = db.session.query(
        extract('month', AppointmentTransaction.created_at).label('month'),
        db.func.sum(AppointmentTransaction.amount).label('total')
    ).filter(
        AppointmentTransaction.organization_id == org_id,
        extract('year', AppointmentTransaction.created_at) == year
    ).group_by('month').all()

    monthly_totals = {}
    for m, t in org_monthly:
        monthly_totals[m] = monthly_totals.get(m, 0) + (t or 0)
    for m, t in appt_monthly:
        monthly_totals[m] = monthly_totals.get(m, 0) + (t or 0)

    summary = [
        {"month": m, "total": monthly_totals[m]} for m in sorted(monthly_totals.keys())
    ]
    return jsonify(summary)

# ------------------------------------------
# Organization Dashboard API
# ------------------------------------------
@organization_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def org_dashboard():
    claims = get_jwt()

    if claims.get("role") not in ["Organization", "Manager", "Staff"]:
        return jsonify({"msg": "Unauthorized"}), 403

    org_id = int(claims.get("organization_id") or claims.get("sub"))
    org = Organization.query.get(org_id)
    if not org:
        return jsonify({"msg": "Organization not found"}), 404

    # ------------------------------------------
    # Fetch appointments for this organization
    # ------------------------------------------
    appointments = (
        Appointment.query.filter_by(organization_id=org_id)
        .order_by(Appointment.appointment_date.desc())
        .all()
    )

    appointments_list = []
    for appt in appointments:
        appointments_list.append({
            "id": appt.id,
            "customer_name": appt.customer_name,
            "customer_phone": appt.customer_phone,
            "appointment_date": appt.appointment_date.isoformat(),
            "status": appt.status,
            "payment_status": appt.payment_status,
            "created_at": appt.created_at.isoformat() if appt.created_at else None,
            "updated_at": appt.updated_at.isoformat() if appt.updated_at else None,
        })

    # ------------------------------------------
    # Fetch recent organization transactions
    # ------------------------------------------
    org_transactions = (
        OrganizationTransaction.query.filter_by(organization_id=org_id)
        .order_by(OrganizationTransaction.created_at.desc())
        .limit(10)
        .all()
    )

    org_txn_list = []
    for txn in org_transactions:
        org_txn_list.append({
            "id": txn.id,
            "amount": txn.amount,
            "transaction_type": txn.transaction_type,
            "payment_method": txn.payment_method,
            "status": txn.status,
            "remarks": txn.remarks,
            "processed_by_type": txn.processed_by_type,
            "created_at": txn.created_at.isoformat() if txn.created_at else None,
        })

    # ------------------------------------------
    # Fetch recent appointment transactions (optional display)
    # ------------------------------------------
    appt_transactions = (
        AppointmentTransaction.query.filter_by(organization_id=org_id)
        .order_by(AppointmentTransaction.created_at.desc())
        .limit(10)
        .all()
    )

    appt_txn_list = []
    for txn in appt_transactions:
        appt_txn_list.append({
            "id": txn.id,
            "appointment_id": txn.appointment_id,
            "amount": txn.amount,
            "transaction_type": txn.transaction_type,
            "payment_method": txn.payment_method,
            "status": txn.status,
            "processed_by_type": txn.processed_by_type,
            "created_at": txn.created_at.isoformat() if txn.created_at else None,
        })

    # ------------------------------------------
    # Build response for frontend
    # ------------------------------------------
    return jsonify({
        "organization": {
            "name": org.name,
            "sector": org.sector,
            "subscription": {
                "status": org.subscription_status,
                "plan": org.subscription_plan,
                "start_date": org.subscription_start.isoformat() if org.subscription_start else None,
                "end_date": org.subscription_end.isoformat() if org.subscription_end else None,
                "next_billing_date": org.next_billing_date.isoformat() if org.next_billing_date else None,
            },
        },
        "appointments_count": len(appointments_list),
        "appointments": appointments_list,
        "organization_transactions": org_txn_list,
        "appointment_transactions": appt_txn_list,
    })


# ------------------------------------------
# Organization Appointments
# ------------------------------------------
@organization_bp.route("/appointments", methods=["GET"])
@jwt_required()
def org_appointments():
    claims = get_jwt()
    if claims.get("role") not in ["Organization", "Manager", "Staff"]:
        return jsonify({"msg": "Unauthorized"}), 403

    org_id = int(claims.get("organization_id") or claims.get("sub"))
    appointments = Appointment.query.filter_by(organization_id=org_id).order_by(Appointment.appointment_date.desc()).all()

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


# ------------------------------------------
# Send Message / WhatsApp Logging
# ------------------------------------------
@organization_bp.route("/message/send", methods=["POST"])
@jwt_required()
def send_message():
    claims = get_jwt()
    if claims.get("role") not in ["Organization", "Manager", "Staff"]:
        return jsonify({"msg": "Unauthorized"}), 403

    org_id = int(claims.get("organization_id") or claims.get("sub"))
    data = request.json or {}
    recipient_number = data.get("recipient_number")
    message_content = data.get("message_content")
    message_type = data.get("message_type", "WhatsApp")
    related_appointment_id = data.get("related_appointment_id")

    if not recipient_number or not message_content:
        return jsonify({"msg": "recipient_number and message_content are required"}), 400

    msg = MessageLog(
        organization_id=org_id,
        recipient_number=recipient_number,
        message_type=message_type,
        message_content=message_content,
        related_appointment_id=related_appointment_id,
        status="Sent",
        remarks=data.get("remarks")
    )
    db.session.add(msg)
    db.session.commit()

    return jsonify({"msg": "Message logged successfully", "message_id": msg.id}), 201


# ------------------------------------------
# Update Organization Profile
# ------------------------------------------
@organization_bp.route("/update", methods=["PATCH"])
@jwt_required()
def update_org():
    claims = get_jwt()
    if claims.get("role") not in ["Organization", "Manager", "Staff"]:
        return jsonify({"msg": "Unauthorized"}), 403

    org_id = int(claims.get("organization_id") or claims.get("sub"))
    org = Organization.query.get(org_id)
    if not org:
        return jsonify({"msg": "Organization not found"}), 404

    data = request.get_json() or {}

    if "name" in data:
        org.name = data["name"]
    if "username" in data:
        org.username = data["username"]
    if "subscription_plan" in data:
        org.subscription_plan = data["subscription_plan"]
    if "subscription_status" in data:
        org.subscription_status = data["subscription_status"]

    org.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({"msg": "Organization updated successfully"})
