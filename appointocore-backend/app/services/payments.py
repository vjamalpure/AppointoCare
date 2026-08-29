from datetime import datetime

from app.models import PaymentOrder, ProviderEvent, db
from app.providers.base import ProviderError
from app.providers.payment import get_payment_provider


def create_order(organization_id, amount, currency="INR", receipt=None, appointment_id=None, notes=None):
    provider = get_payment_provider()
    result = provider.create_order(amount, currency, receipt or f"org_{organization_id}", notes)
    order = PaymentOrder(
        organization_id=organization_id, appointment_id=appointment_id, provider=result.provider,
        provider_order_id=result.reference, amount=amount, currency=currency,
        status=result.status or "created", metadata=result.data or {},
    )
    db.session.add(order)
    db.session.commit()
    return order, result


def verify_payment(provider_order_id, payment_id, signature):
    order = PaymentOrder.query.filter_by(provider_order_id=provider_order_id).first()
    if not order:
        raise ProviderError("Payment order not found.")
    result = get_payment_provider().verify_payment(provider_order_id, payment_id, signature)
    order.status = result.status or "verified"
    order.updated_at = datetime.utcnow()
    db.session.commit()
    return order, result


def get_order_status(order):
    result = get_payment_provider().fetch_order(order.provider_order_id)
    order.status = result.status or order.status
    db.session.commit()
    return result


def process_webhook(provider_name, event_id, event_type, payload):
    existing = ProviderEvent.query.filter_by(provider=provider_name, event_id=event_id).first()
    if existing:
        return existing, False
    event = ProviderEvent(provider=provider_name, event_id=event_id, event_type=event_type, payload=payload, status="processed", processed_at=datetime.utcnow())
    db.session.add(event)
    if provider_name == "razorpay":
        provider_order_id = ((payload.get("payload") or {}).get("order") or {}).get("entity", {}).get("id")
        if provider_order_id:
            order = PaymentOrder.query.filter_by(provider_order_id=provider_order_id).first()
            if order:
                order.status = "captured" if event_type.endswith("captured") else "failed" if event_type.endswith("failed") else order.status
    db.session.commit()
    return event, True
