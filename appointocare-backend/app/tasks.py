from datetime import datetime
from app import create_app
from app.celery import make_celery
from app.models import Appointment, Organization
from app.services.notifications import send_notification
from app.providers.base import ProviderError

app = create_app()
celery = make_celery(app)


@celery.task(bind=True)
def send_whatsapp_message(self, organization_id, recipient_number, message_content):
    org = Organization.query.get(organization_id)
    if not org:
        return {"status": "organization_not_found"}

    try:
        result = send_notification("whatsapp", organization_id, recipient_number, message_content)
    except ProviderError as exc:
        raise self.retry(exc=exc, countdown=60, max_retries=3)
    return {"status": result.status or "sent", "recipient": recipient_number, "provider": result.provider}


@celery.task(bind=True)
def appointment_reminder(self, appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return {"status": "appointment_not_found"}

    if not app.config.get("REMINDERS_ENABLED", True):
        return {"status": "disabled", "appointment_id": appointment.id}
    try:
        result = send_notification("whatsapp", appointment.organization_id, appointment.customer_phone, f"Reminder: your appointment is scheduled for {appointment.appointment_date.isoformat()}.")
    except ProviderError as exc:
        raise self.retry(exc=exc, countdown=300, max_retries=3)
    return {"status": result.status or "sent", "appointment_id": appointment.id, "provider": result.provider}


@celery.task(bind=True, autoretry_for=(ProviderError,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def send_email_task(self, organization_id, recipient, subject, message):
    result = send_notification("email", organization_id, recipient, message, subject=subject)
    return {"status": result.status, "provider": result.provider}


@celery.task(bind=True, autoretry_for=(ProviderError,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def send_sms_task(self, organization_id, recipient, message):
    result = send_notification("sms", organization_id, recipient, message)
    return {"status": result.status, "provider": result.provider}
