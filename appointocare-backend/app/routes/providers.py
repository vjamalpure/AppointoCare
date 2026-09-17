import hashlib
import hmac
import logging

from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import get_jwt

from app.providers.base import ProviderError
from app.providers.whatsapp import get_whatsapp_provider
from app.security import get_organization_id, require_roles
from app.services import payments

logger = logging.getLogger(__name__)
provider_bp = Blueprint("provider_bp", __name__)


@provider_bp.get("/status")
@require_roles("Admin", "Organization", "Manager", "Staff")
def provider_status():
    from app.providers.notifications import get_notification_provider
    from app.providers.payment import get_payment_provider
    whatsapp = get_whatsapp_provider()
    return jsonify({
        "payment": {"provider": get_payment_provider().name, "state": get_payment_provider().state.value},
        "whatsapp": {"provider": "whatsapp", "state": whatsapp.state.value},
        "email": {"provider": current_app.config.get("EMAIL_PROVIDER", "mock"), "state": get_notification_provider("email").state.value},
        "sms": {"provider": current_app.config.get("SMS_PROVIDER", "mock"), "state": get_notification_provider("sms").state.value},
    })


@provider_bp.post("/payments/orders")
@require_roles("Admin", "Organization", "Manager", "Staff")
def create_payment_order():
    data = request.get_json() or {}
    organization_id = get_organization_id()
    if get_jwt().get("role") == "Admin":
        organization_id = data.get("organization_id")
    if not organization_id:
        return jsonify({"msg": "organization_id is required"}), 400
    amount = data.get("amount")
    if amount is None or float(amount) <= 0:
        return jsonify({"msg": "A positive amount is required"}), 400
    try:
        order, result = payments.create_order(int(organization_id), float(amount), data.get("currency", "INR"), data.get("receipt"), data.get("appointment_id"), data.get("notes"))
    except ProviderError as exc:
        return jsonify({"msg": str(exc), "provider_state": exc.state.value}), 503
    return jsonify({"id": order.id, "provider": result.provider, "order_id": result.reference, "status": order.status, "amount": order.amount, "currency": order.currency}), 201


@provider_bp.get("/payments/orders/<provider_order_id>")
@require_roles("Admin", "Organization", "Manager", "Staff")
def get_payment_order(provider_order_id):
    from app.models import PaymentOrder
    order = PaymentOrder.query.filter_by(provider_order_id=provider_order_id).first_or_404()
    if get_jwt().get("role") != "Admin" and order.organization_id != get_organization_id():
        return jsonify({"msg": "Unauthorized"}), 403
    try:
        result = payments.get_order_status(order)
    except ProviderError as exc:
        return jsonify({"msg": str(exc), "provider_state": exc.state.value}), 503
    return jsonify({"id": order.id, "order_id": order.provider_order_id, "status": result.status or order.status, "provider": result.provider, "data": result.data or {}})


@provider_bp.post("/payments/verify")
@require_roles("Admin", "Organization", "Manager", "Staff")
def verify_payment():
    data = request.get_json() or {}
    if not data.get("order_id") or not data.get("payment_id"):
        return jsonify({"msg": "order_id and payment_id are required"}), 400
    try:
        order, result = payments.verify_payment(data["order_id"], data["payment_id"], data.get("signature", ""))
    except ProviderError as exc:
        return jsonify({"msg": str(exc), "provider_state": exc.state.value}), 400
    if get_organization_id() != order.organization_id and get_jwt().get("role") != "Admin":
        return jsonify({"msg": "Unauthorized"}), 403
    return jsonify({"order_id": order.provider_order_id, "status": order.status, "payment_id": result.reference})


@provider_bp.post("/webhooks/razorpay")
def razorpay_webhook():
    raw = request.get_data()
    secret = current_app.config.get("RAZORPAY_WEBHOOK_SECRET", "")
    signature = request.headers.get("X-Razorpay-Signature", "")
    if not secret or not hmac.compare_digest(hmac.new(secret.encode(), raw, hashlib.sha256).hexdigest(), signature):
        return jsonify({"msg": "Invalid webhook signature"}), 401
    payload = request.get_json(silent=True) or {}
    event_id = request.headers.get("X-Razorpay-Event-Id") or payload.get("id")
    if not event_id or not payload.get("event"):
        return jsonify({"msg": "Invalid webhook payload"}), 400
    _, created = payments.process_webhook("razorpay", event_id, payload["event"], payload)
    return jsonify({"status": "processed" if created else "duplicate"}), 200


@provider_bp.get("/webhooks/whatsapp")
def whatsapp_webhook_verify():
    verify_token = request.args.get("hub.verify_token") or request.args.get("hub_verify_token")
    challenge = request.args.get("hub.challenge") or request.args.get("hub_challenge", "")
    if verify_token != current_app.config.get("WHATSAPP_WEBHOOK_VERIFY_TOKEN", ""):
        return jsonify({"msg": "Invalid verify token"}), 403
    return challenge, 200


@provider_bp.post("/webhooks/whatsapp")
def whatsapp_webhook():
    raw = request.get_data()
    provider = get_whatsapp_provider()
    if current_app.config.get("WHATSAPP_APP_SECRET") and not provider.verify_signature(raw, request.headers.get("X-Hub-Signature-256")):
        return jsonify({"msg": "Invalid webhook signature"}), 401
    payload = request.get_json(silent=True) or {}
    event_id = payload.get("id") or (payload.get("entry") or [{}])[0].get("id")
    if not event_id:
        return jsonify({"status": "ignored"}), 200
    _, created = payments.process_webhook("whatsapp", event_id, "message.update", payload)
    return jsonify({"status": "processed" if created else "duplicate"}), 200
