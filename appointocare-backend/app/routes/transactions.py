from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.models import db, OrganizationTransaction, AppointmentTransaction, Appointment, AuditLog

transaction_bp = Blueprint("transaction_bp", __name__)

# Record transaction
@transaction_bp.route("/create", methods=["POST"])
@jwt_required()
def create_transaction():
    claims = get_jwt()
    user_id = get_jwt_identity()
    if claims.get("role") not in ["Admin", "Organization", "Manager", "Staff"]:
        return jsonify({"msg": "Unauthorized"}), 403

    org_id = None
    if claims.get("role") != "Admin":
        org_id = int(claims.get("organization_id") or user_id)

    data = request.json or {}
    transaction_type = data.get("transaction_type")
    amount = data.get("amount")
    payment_method = data.get("payment_method", "Unknown")
    status = data.get("status", "Success")

    if not transaction_type or amount is None:
        return jsonify({"msg": "Missing required fields"}), 400

    if transaction_type.lower() == "appointment":
        appointment_id = data.get("appointment_id")
        if not appointment_id:
            return jsonify({"msg": "appointment_id required"}), 400

        appointment = Appointment.query.get(appointment_id)
        if not appointment:
            return jsonify({"msg": "Appointment not found"}), 404
        if org_id and appointment.organization_id != org_id:
            return jsonify({"msg": "Unauthorized"}), 403

        transaction = AppointmentTransaction(
            appointment_id=appointment.id,
            organization_id=appointment.organization_id,
            amount=amount,
            transaction_type=data.get("transaction_type_label", "Payment"),
            payment_method=payment_method,
            processed_by_type=claims.get("role"),
            processed_by_id=int(user_id) if str(user_id).isdigit() else None,
            status=status
        )
        db.session.add(transaction)
        if status.lower() == "success":
            appointment.payment_status = "Paid"
        elif status.lower() == "failed":
            appointment.payment_status = "Failed"

    elif transaction_type.lower() == "organization":
        organization_id = int(data.get("organization_id") or org_id or user_id)
        transaction = OrganizationTransaction(
            organization_id=int(organization_id),
            amount=amount,
            transaction_type=data.get("transaction_type_label", "Subscription"),
            payment_method=payment_method,
            processed_by_type=claims.get("role"),
            processed_by_id=int(user_id) if str(user_id).isdigit() else None,
            status=status
        )
        db.session.add(transaction)
    else:
        return jsonify({"msg": "Invalid transaction_type"}), 400

    db.session.commit()
    return jsonify({"msg": "Transaction recorded", "id": transaction.id}), 201


# Refund transaction
@transaction_bp.route("/<int:txn_id>/refund", methods=["POST"])
@jwt_required()
def refund_transaction(txn_id):
    claims = get_jwt()
    role = claims.get("role")
    user_id = get_jwt_identity()
    txn = AppointmentTransaction.query.get_or_404(txn_id)
    user_org_id = int(claims.get("organization_id") or 0)
    if role not in ["Admin", "SuperAdmin"] and txn.organization_id != user_org_id:
        return jsonify({"msg": "Unauthorized"}), 403

    if txn.transaction_type == "Refund":
        return jsonify({"msg": "Transaction is already a refund"}), 400

    data = request.json or {}
    refund_amount = float(data.get("amount") or txn.amount)
    reason = data.get("reason", "Patient consultation cancellation")

    refund_txn = AppointmentTransaction(
        appointment_id=txn.appointment_id,
        organization_id=txn.organization_id,
        amount=refund_amount,
        transaction_type="Refund",
        payment_method=txn.payment_method,
        processed_by_type=role,
        processed_by_id=int(user_id) if str(user_id).isdigit() else None,
        status="Success",
        remarks=f"Refund for Txn #{txn.id}: {reason}"
    )
    db.session.add(refund_txn)

    if txn.appointment_id:
        appt = Appointment.query.get(txn.appointment_id)
        if appt:
            appt.payment_status = "Refunded"

    try:
        audit = AuditLog(
            organization_id=txn.organization_id,
            user_id=int(user_id) if str(user_id).isdigit() else None,
            user_role=role,
            action="REFUND_TRANSACTION",
            entity="AppointmentTransaction",
            entity_id=txn.id,
            details=f"Processed refund of ₹{refund_amount} for transaction #{txn.id}. Reason: {reason}",
            ip_address=request.remote_addr
        )
        db.session.add(audit)
    except Exception:
        pass

    db.session.commit()
    return jsonify({
        "msg": f"Refund of ₹{refund_amount} processed successfully",
        "refund_transaction_id": refund_txn.id,
        "original_transaction_id": txn.id,
        "amount": refund_amount,
        "status": "Success"
    }), 201


# Get transactions
@transaction_bp.route("/all", methods=["GET"])
@jwt_required()
def get_transactions():
    claims = get_jwt()
    user_id = get_jwt_identity()
    if claims.get("role") not in ["Admin", "Organization", "Manager", "Staff"]:
        return jsonify({"msg": "Unauthorized"}), 403

    transaction_type = request.args.get("transaction_type")
    org_id = request.args.get("organization_id")

    results = []

    if claims.get("role") == "Admin":
        if transaction_type == "organization" or not transaction_type:
            org_txns = OrganizationTransaction.query
            if org_id:
                org_txns = org_txns.filter_by(organization_id=int(org_id))
            org_txns = org_txns.all()
            results += [
                {
                    "id": t.id,
                    "organization_id": t.organization_id,
                    "amount": t.amount,
                    "transaction_type": t.transaction_type,
                    "payment_method": t.payment_method,
                    "status": t.status,
                    "created_at": t.created_at.isoformat(),
                }
                for t in org_txns
            ]

        if transaction_type == "appointment" or not transaction_type:
            appt_txns = AppointmentTransaction.query
            if org_id:
                appt_txns = appt_txns.filter_by(organization_id=int(org_id))
            appt_txns = appt_txns.all()
            results += [
                {
                    "id": t.id,
                    "appointment_id": t.appointment_id,
                    "organization_id": t.organization_id,
                    "amount": t.amount,
                    "transaction_type": t.transaction_type,
                    "payment_method": t.payment_method,
                    "status": t.status,
                    "created_at": t.created_at.isoformat(),
                }
                for t in appt_txns
            ]

    else:
        org_id = int(claims.get("organization_id") or user_id)
        org_txns = OrganizationTransaction.query.filter_by(organization_id=org_id).all()
        results += [
            {
                "id": t.id,
                "organization_id": t.organization_id,
                "amount": t.amount,
                "transaction_type": t.transaction_type,
                "payment_method": t.payment_method,
                "status": t.status,
                "created_at": t.created_at.isoformat(),
            }
            for t in org_txns
        ]

        appt_txns = (
            db.session.query(AppointmentTransaction)
            .join(Appointment, Appointment.id == AppointmentTransaction.appointment_id)
            .filter(Appointment.organization_id == org_id)
            .all()
        )
        results += [
            {
                "id": t.id,
                "appointment_id": t.appointment_id,
                "organization_id": t.organization_id,
                "amount": t.amount,
                "transaction_type": t.transaction_type,
                "payment_method": t.payment_method,
                "status": t.status,
                "created_at": t.created_at.isoformat(),
            }
            for t in appt_txns
        ]

    return jsonify(results)


@transaction_bp.route("/<int:txn_id>/download-pdf", methods=["GET"])
@transaction_bp.route("/appointment/<int:txn_id>/download-pdf", methods=["GET"])
@jwt_required()
def download_transaction_pdf(txn_id):
    claims = get_jwt()
    role = claims.get("role")
    txn = AppointmentTransaction.query.get_or_404(txn_id)
    user_org_id = int(claims.get("organization_id") or 0)
    if role not in ["Admin", "SuperAdmin"] and txn.organization_id != user_org_id:
        return jsonify({"msg": "Unauthorized: Cross-tenant access denied"}), 403

    from app.services.pdf_service import generate_invoice_pdf
    from app.models import Organization
    from flask import Response

    org = Organization.query.get(txn.organization_id)
    org_data = {
        "name": org.name if org else "Service Provider",
        "code": org.code if org else "ORG",
        "sector": org.sector if org else "Commercial",
        "phone": getattr(org, "phone", "") or "+1 555-0100",
        "email": getattr(org, "email", "") or "billing@appointocare.com",
        "address": getattr(org, "address", "") or "Commercial City Center"
    }

    appt_data = {}
    if txn.appointment_id:
        appt = Appointment.query.get(txn.appointment_id)
        if appt:
            appt_data = {
                "customer_name": appt.customer_name,
                "customer_phone": appt.customer_phone,
                "service_name": appt.service_name or "Consultation Service",
                "appointment_date": appt.appointment_date.isoformat() if appt.appointment_date else ""
            }

    txn_dict = {
        "id": txn.id,
        "amount": txn.amount,
        "payment_method": txn.payment_method,
        "transaction_type": txn.transaction_type,
        "status": txn.status,
        "created_at": txn.created_at.strftime("%d %b %Y, %I:%M %p") if txn.created_at else ""
    }

    pdf_bytes = generate_invoice_pdf(org_data, txn_dict, appt_data)
    filename = f"invoice_{txn.id}.pdf"

    try:
        user_id_val = claims.get("sub")
        audit = AuditLog(
            organization_id=txn.organization_id,
            user_id=int(user_id_val) if user_id_val and str(user_id_val).isdigit() else None,
            user_role=role,
            action="DOWNLOAD_PDF",
            entity="AppointmentTransaction",
            entity_id=txn.id,
            details=f"Downloaded invoice PDF for transaction #{txn.id} (amount: {txn.amount})",
            ip_address=request.remote_addr
        )
        db.session.add(audit)
        db.session.commit()
    except Exception:
        db.session.rollback()

    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

