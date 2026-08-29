from datetime import datetime
from time import sleep
from app import create_app
from app.celery import make_celery
from app.models import db, MessageLog, Appointment, Organization

app = create_app()
celery = make_celery(app)


@celery.task(bind=True)
def send_whatsapp_message(self, organization_id, recipient_number, message_content):
    org = Organization.query.get(organization_id)
    if not org:
        return {"status": "organization_not_found"}

    # Example async logging for WhatsApp messages; extend with Meta Cloud API integration later.
    log = MessageLog(
        organization_id=organization_id,
        recipient_number=recipient_number,
        message_type="WhatsApp",
        message_content=message_content,
        status="Scheduled",
        related_appointment_id=None,
        remarks="Scheduled via Celery task"
    )
    db.session.add(log)
    db.session.commit()

    sleep(1)
    log.status = "Sent"
    log.sent_at = datetime.utcnow()
    db.session.commit()

    return {"status": "sent", "recipient": recipient_number}


@celery.task(bind=True)
def appointment_reminder(self, appointment_id):
    appointment = Appointment.query.get(appointment_id)
    if not appointment:
        return {"status": "appointment_not_found"}

    # Placeholder logic for appointment reminders.
    return {
        "status": "reminder_sent",
        "appointment_id": appointment.id,
        "customer_name": appointment.customer_name
    }
