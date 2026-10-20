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


@celery.task(bind=True, max_retries=3)
def appointment_reminder(self, appointment_id):
    """
    Dispatches a privacy-safe appointment reminder.
    - Idempotent: checks MessageLog to prevent duplicate dispatches
    - Status-aware: skips Cancelled or Completed appointments
    - Privacy-safe: excludes clinical diagnoses or medication details
    - Exponential backoff on transient provider failures
    """
    from app.models import MessageLog, db

    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return {"status": "appointment_not_found"}

    if not app.config.get("REMINDERS_ENABLED", True):
        return {"status": "disabled", "appointment_id": appointment.id}

    org = Organization.query.get(appointment.organization_id)
    if org and getattr(org, "reminders_enabled", True) is False:
        return {"status": "tenant_reminders_disabled", "appointment_id": appointment.id}

    if (appointment.status or "").lower() in ["cancelled", "completed", "no-show"]:
        return {"status": f"skipped_{appointment.status.lower()}", "appointment_id": appointment.id}

    # Idempotency Guard: prevent duplicate reminder dispatches within 24 hours
    existing_log = MessageLog.query.filter_by(
        organization_id=appointment.organization_id,
        related_appointment_id=appointment.id,
        message_type="WhatsApp"
    ).filter(MessageLog.status.in_(["Sent", "Delivered"])).first()

    if existing_log:
        return {
            "status": "already_sent",
            "appointment_id": appointment.id,
            "message_id": existing_log.id,
            "sent_at": existing_log.sent_at.isoformat() if existing_log.sent_at else None
        }

    # Format privacy-safe reminder (no clinical/medical details exposed)
    date_str = appointment.appointment_date.strftime("%d %b %Y at %I:%M %p") if appointment.appointment_date else "your scheduled time"
    org_name = org.name if org else "our center"
    phone_contact = org.phone or "our front desk"
    reminder_msg = (
        f"Hello {appointment.customer_name}, this is a gentle reminder for your appointment at {org_name} "
        f"on {date_str}. Please contact {phone_contact} if you need to reschedule."
    )

    try:
        result = send_notification("whatsapp", appointment.organization_id, appointment.customer_phone, reminder_msg)
        # Update log to link with appointment for idempotency tracking
        last_log = MessageLog.query.filter_by(
            organization_id=appointment.organization_id,
            recipient_number=appointment.customer_phone
        ).order_by(MessageLog.id.desc()).first()
        if last_log and not last_log.related_appointment_id:
            last_log.related_appointment_id = appointment.id
            db.session.commit()
    except ProviderError as exc:
        countdown = 60 * (2 ** self.request.retries)  # 60s, 120s, 240s
        raise self.retry(exc=exc, countdown=countdown)

    return {
        "status": result.status or "sent",
        "appointment_id": appointment.id,
        "recipient": appointment.customer_phone,
        "provider": result.provider
    }


@celery.task
def dispatch_due_appointment_reminders(hours_ahead=24):
    """
    Batch cron/scheduled task:
    Finds upcoming 'Booked' appointments occurring within the next `hours_ahead` hours
    and enqueues appointment_reminder tasks idempotently.
    """
    from datetime import timedelta
    from app.models import Appointment

    now = datetime.utcnow()
    window_end = now + timedelta(hours=hours_ahead)

    due_appts = Appointment.query.filter(
        Appointment.status == "Booked",
        Appointment.appointment_date >= now,
        Appointment.appointment_date <= window_end
    ).all()

    enqueued = []
    for appt in due_appts:
        appointment_reminder.delay(appt.id)
        enqueued.append(appt.id)

    return {"status": "dispatched", "count": len(enqueued), "appointment_ids": enqueued}


@celery.task(bind=True, autoretry_for=(ProviderError,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def send_email_task(self, organization_id, recipient, subject, message):
    result = send_notification("email", organization_id, recipient, message, subject=subject)
    return {"status": result.status, "provider": result.provider}


@celery.task(bind=True, autoretry_for=(ProviderError,), retry_backoff=True, retry_kwargs={"max_retries": 3})
def send_sms_task(self, organization_id, recipient, message):
    result = send_notification("sms", organization_id, recipient, message)
    return {"status": result.status, "provider": result.provider}
