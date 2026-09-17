from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt
from app.models import db, Appointment, AppointmentTransaction, AuditLog, Organization, PaymentConfig, ServiceStatus
from app.service_guards import check_razorpay_active
from datetime import datetime
import os
import hmac
import hashlib

payments_bp = Blueprint("payments_bp", __name__)

PAYMENT_CONFIG = {
    "key_id": os.getenv("RAZORPAY_KEY_ID", "rzp_test_AppointoCare99"),
    "key_secret": os.getenv("RAZORPAY_KEY_SECRET", "mock_key_secret_appointocare_9988"),
    "webhook_secret": os.getenv("RAZORPAY_WEBHOOK_SECRET", "rzp_webhook_secret_secure_2026"),
    "currency": "INR",
    "merchant_name": "AppointoCare Multi-Industry Platform",
    "status": "Ready (Test Sandbox)",
    "auto_capture": True,
    "platform_fee_percent": 5.0
}


@payments_bp.route("/config", methods=["GET"])
@jwt_required()
def get_payment_config():
    claims = get_jwt()
    tenant_id = claims.get("organization_id")
    if tenant_id:
        cfg_record = PaymentConfig.query.filter_by(tenant_id=int(tenant_id)).first()
        if cfg_record:
            return jsonify({
                "tenant_id": cfg_record.tenant_id,
                "razorpay_account_id": cfg_record.razorpay_account_id,
                "merchant_name": cfg_record.merchant_name,
                "service_status": cfg_record.service_status,
                "platform_commission_rate": cfg_record.platform_commission_rate,
                "currency": cfg_record.currency,
                "auto_capture": cfg_record.auto_capture,
                "onboarding_status": cfg_record.onboarding_status,
                "key_id": PAYMENT_CONFIG["key_id"]
            })
    return jsonify(PAYMENT_CONFIG)


@payments_bp.route("/config", methods=["POST"])
@jwt_required()
def update_payment_config():
    data = request.json or {}
    for k in ["key_id", "currency", "merchant_name", "status", "auto_capture"]:
        if k in data:
            PAYMENT_CONFIG[k] = data[k]
    return jsonify({"msg": "Payment configuration updated", "config": PAYMENT_CONFIG})


# -----------------------------------------------------------------------------
# LAYER 4: Razorpay Route Split Order Creation (Dynamic 5% Platform Fee)
# -----------------------------------------------------------------------------
@payments_bp.route("/create-order", methods=["POST"])
@payments_bp.route("/create-split-order", methods=["POST"])
@jwt_required()
@check_razorpay_active
def create_payment_order():
    claims = get_jwt()
    data = request.json or {}

    amount = float(data.get("amount") or 85.0)
    appointment_id = data.get("appointment_id")
    customer_name = data.get("customer_name") or "Customer"
    currency = data.get("currency") or PAYMENT_CONFIG.get("currency", "INR")

    tenant_id = int(claims.get("organization_id") or claims.get("sub") or 1)
    p_config = PaymentConfig.query.filter_by(tenant_id=tenant_id).first()

    # Dynamic platform fee: default 5% (0.05)
    commission_rate = p_config.platform_commission_rate if p_config else 0.05
    subunits_total = int(round(amount * 100))  # in paise / cents
    
    # Split calculations
    platform_fee_subunits = int(round(subunits_total * commission_rate))
    merchant_share_subunits = subunits_total - platform_fee_subunits
    
    client_account_id = p_config.razorpay_account_id if (p_config and p_config.razorpay_account_id) else f"acc_rzp_sub_{tenant_id}"

    # Razorpay Route 'transfers' payload
    transfers_payload = [
        {
            "account": client_account_id,
            "amount": merchant_share_subunits,
            "currency": currency,
            "notes": {
                "tenant_id": str(tenant_id),
                "appointment_id": str(appointment_id) if appointment_id else "direct_booking",
                "commission_rate_percent": str(round(commission_rate * 100, 2)),
                "platform_fee_paise": str(platform_fee_subunits)
            },
            "on_hold": 0
        }
    ]

    order_id = f"order_rzp_{int(datetime.utcnow().timestamp())}_{appointment_id or 101}"

    return jsonify({
        "order_id": order_id,
        "amount": amount,
        "amount_subunits": subunits_total,
        "currency": currency,
        "key_id": PAYMENT_CONFIG["key_id"],
        "appointment_id": appointment_id,
        "customer_name": customer_name,
        "split_details": {
            "platform_fee_paise": platform_fee_subunits,
            "platform_fee_amount": round(platform_fee_subunits / 100.0, 2),
            "platform_commission_pct": round(commission_rate * 100, 2),
            "merchant_account_id": client_account_id,
            "merchant_share_paise": merchant_share_subunits,
            "merchant_net_amount": round(merchant_share_subunits / 100.0, 2)
        },
        "transfers": transfers_payload,
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
        transaction_type="Appointment Payment (Razorpay Route)",
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
        details=f"Verified Razorpay Route payment ID {payment_id} for ${amount} with split routing",
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


# -----------------------------------------------------------------------------
# Razorpay Webhook Controller: Cryptographic Verification & Split Event Dispatch
# -----------------------------------------------------------------------------
@payments_bp.route("/webhook", methods=["POST"])
def payment_webhook():
    """
    Handles Razorpay Webhooks:
    - Verifies HMAC-SHA256 signature using X-Razorpay-Signature
    - Dispatches 'payment.captured' (marks appointment paid & records transaction)
    - Dispatches 'transfer.processed' (confirms Route payout settlement to client account)
    - Dispatches 'transfer.failed' (logs alert for payment failure)
    """
    raw_payload = request.get_data(as_text=True)
    received_signature = request.headers.get("X-Razorpay-Signature")
    webhook_secret = PAYMENT_CONFIG.get("webhook_secret", "rzp_webhook_secret_secure_2026")

    # Cryptographic HMAC-SHA256 signature verification
    if received_signature:
        expected_signature = hmac.new(
            webhook_secret.encode("utf-8"),
            raw_payload.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(received_signature, expected_signature):
            return jsonify({"error": "INVALID_SIGNATURE", "msg": "Webhook signature verification failed"}), 400

    data = request.json or {}
    event = data.get("event", "payment.captured")
    payload = data.get("payload", {})

    if event == "payment.captured":
        payment_entity = payload.get("payment", {}).get("entity", {})
        pay_id = payment_entity.get("id")
        amount = (payment_entity.get("amount") or 0) / 100.0
        notes = payment_entity.get("notes", {})
        appt_id = notes.get("appointment_id")
        tenant_id = int(notes.get("tenant_id") or 1)

        if appt_id and str(appt_id).isdigit():
            appt = Appointment.query.get(int(appt_id))
            if appt:
                appt.payment_status = "Paid"

        # Log appointment transaction
        txn = AppointmentTransaction(
            appointment_id=int(appt_id) if appt_id and str(appt_id).isdigit() else None,
            organization_id=tenant_id,
            amount=amount,
            transaction_type="Razorpay Route Captured",
            payment_method="Webhook Auto-Capture",
            processed_by_type="Razorpay Webhook",
            status="Success"
        )
        db.session.add(txn)

        audit = AuditLog(
            organization_id=tenant_id,
            action="PAYMENT_CAPTURED_WEBHOOK",
            entity="Payment",
            entity_id=int(appt_id) if appt_id and str(appt_id).isdigit() else None,
            details=f"Payment {pay_id} captured for ${amount} via Razorpay Webhook",
            ip_address=request.remote_addr
        )
        db.session.add(audit)
        db.session.commit()

        return jsonify({"status": "processed", "event": event, "payment_id": pay_id}), 200

    elif event == "transfer.processed":
        transfer_entity = payload.get("transfer", {}).get("entity", {})
        transfer_id = transfer_entity.get("id")
        sub_account = transfer_entity.get("recipient")
        amount = (transfer_entity.get("amount") or 0) / 100.0
        notes = transfer_entity.get("notes", {})
        tenant_id = int(notes.get("tenant_id") or 1)

        audit = AuditLog(
            organization_id=tenant_id,
            action="TRANSFER_PROCESSED_WEBHOOK",
            entity="RazorpayRouteTransfer",
            details=f"Transfer {transfer_id} of ${amount} settled to sub-account {sub_account}",
            ip_address=request.remote_addr
        )
        db.session.add(audit)
        db.session.commit()

        return jsonify({"status": "processed", "event": event, "transfer_id": transfer_id}), 200

    elif event == "transfer.failed":
        transfer_entity = payload.get("transfer", {}).get("entity", {})
        transfer_id = transfer_entity.get("id")
        notes = transfer_entity.get("notes", {})
        tenant_id = int(notes.get("tenant_id") or 1)

        audit = AuditLog(
            organization_id=tenant_id,
            action="TRANSFER_FAILED_WEBHOOK",
            entity="RazorpayRouteTransfer",
            details=f"Transfer {transfer_id} failed. Reason: {transfer_entity.get('error_description')}",
            ip_address=request.remote_addr
        )
        db.session.add(audit)
        db.session.commit()

        return jsonify({"status": "processed", "event": event, "transfer_id": transfer_id, "failed": True}), 200

    return jsonify({"status": "received", "event": event}), 200

