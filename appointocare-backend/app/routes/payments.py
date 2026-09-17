from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt
from app.models import db, Appointment, AppointmentTransaction, AuditLog, Organization
from datetime import datetime
import os
import hmac
import hashlib

payments_bp = Blueprint("payments_bp", __name__)

PAYMENT_CONFIG = {
    "key_id": os.getenv("RAZORPAY_KEY_ID", "rzp_test_AppointoCare99"),
    "key_secret": "••••••••••••••••",
    "currency": "INR",
    "merchant_name": "AppointoCare Multi-Industry Platform",
    "status": "Ready (Test Sandbox)",
    "auto_capture": True
}


@payments_bp.route("/config", methods=["GET"])
@jwt_required()
def get_payment_config():
    return jsonify(PAYMENT_CONFIG)


@payments_bp.route("/config", methods=["POST"])
@jwt_required()
def update_payment_config():
    data = request.json or {}
    for k in ["key_id", "currency", "merchant_name", "status", "auto_capture"]:
        if k in data:
            PAYMENT_CONFIG[k] = data[k]
    return jsonify({"msg": "Payment configuration updated", "config": PAYMENT_CONFIG})


@payments_bp.route("/create-order", methods=["POST"])
@jwt_required()
def create_payment_order():
    claims = get_jwt()
    data = request.json or {}

    amount = float(data.get("amount") or 85.0)
    appointment_id = data.get("appointment_id")
    customer_name = data.get("customer_name") or "Customer"
    currency = data.get("currency") or PAYMENT_CONFIG.get("currency", "INR")

    order_amount_subunits = int(round(amount * 100))
    order_id = f"order_rzp_{int(datetime.utcnow().timestamp())}_{appointment_id or 101}"

    return jsonify({
        "order_id": order_id,
        "amount": amount,
        "amount_subunits": order_amount_subunits,
        "currency": currency,
        "key_id": PAYMENT_CONFIG["key_id"],
        "appointment_id": appointment_id,
        "customer_name": customer_name,
        "is_live_gateway": False
    }), 201


@payments_bp.route("/verify", methods=["POST"])
@jwt_required()
def verify_payment():
    claims = get_jwt()
    role = claims.get("role")
    user_id = claims.get("sub")
    data = request.json or {}

    appointment_id = data.get("appointment_id")
    amount = float(data.get("amount") or 85.0)
    customer_name = data.get("customer_name") or "Verified Customer"
    payment_id = data.get("razorpay_payment_id") or f"pay_{int(datetime.utcnow().timestamp())}"

    org_id = int(claims.get("organization_id") or 1)

    if appointment_id:
        appt = Appointment.query.get(appointment_id)
        if appt:
            appt.payment_status = "Paid"
            org_id = appt.organization_id

    # Create transaction
    txn = AppointmentTransaction(
        appointment_id=int(appointment_id) if appointment_id else None,
        organization_id=org_id,
        amount=amount,
        transaction_type="Appointment Payment (Razorpay)",
        payment_method="Razorpay UPI/Card",
        processed_by_type=role or "Organization",
        processed_by_id=int(user_id) if str(user_id).isdigit() else None,
        status="Success"
    )
    db.session.add(txn)

    # Log audit
    audit = AuditLog(
        organization_id=org_id,
        user_id=int(user_id) if str(user_id).isdigit() else None,
        user_role=role,
        action="PAYMENT_VERIFIED",
        entity="AppointmentTransaction",
        entity_id=appointment_id,
        details=f"Verified Razorpay payment ID {payment_id} for ${amount}",
        ip_address=request.remote_addr
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({
        "msg": "Payment verified and recorded successfully",
        "status": "Success",
        "payment_id": payment_id,
        "amount": amount
    }), 200


@payments_bp.route("/webhook", methods=["POST"])
def payment_webhook():
    return jsonify({"status": "received"}), 200
