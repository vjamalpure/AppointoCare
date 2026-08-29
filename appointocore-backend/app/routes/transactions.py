from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.models import db, OrganizationTransaction, AppointmentTransaction, Appointment

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
            processed_by_id=int(user_id),
            status=status
        )
        db.session.add(transaction)

    elif transaction_type.lower() == "organization":
        organization_id = int(data.get("organization_id") or org_id or user_id)
        transaction = OrganizationTransaction(
            organization_id=int(organization_id),
            amount=amount,
            transaction_type=data.get("transaction_type_label", "Subscription"),
            payment_method=payment_method,
            processed_by_type=claims.get("role"),
            processed_by_id=int(user_id),
            status=status
        )
        db.session.add(transaction)
    else:
        return jsonify({"msg": "Invalid transaction_type"}), 400

    db.session.commit()
    return jsonify({"msg": "Transaction recorded", "id": transaction.id}), 201


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
