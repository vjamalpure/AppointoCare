import unittest
from datetime import datetime, timedelta
from app import create_app
from app.models import db, Organization, Appointment, MessageLog
from app.tasks import appointment_reminder


class AppointmentRemindersTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()

    def test_reminder_skips_cancelled_appointment(self):
        """Ensures cancelled appointments are not sent reminders."""
        with self.app.app_context():
            appt = Appointment(
                customer_name="Test Cancelled User",
                customer_phone="+919876543210",
                appointment_date=datetime.utcnow() + timedelta(days=1),
                status="Cancelled",
                organization_id=1
            )
            db.session.add(appt)
            db.session.commit()

            res = appointment_reminder.apply(args=[appt.id]).get()
            self.assertEqual(res["status"], "skipped_cancelled")

            db.session.delete(appt)
            db.session.commit()

    def test_reminder_idempotent_duplicate_prevention(self):
        """Ensures duplicate reminder is rejected if a MessageLog already exists for the appointment."""
        with self.app.app_context():
            appt = Appointment(
                customer_name="Test Idempotent User",
                customer_phone="+919876543211",
                appointment_date=datetime.utcnow() + timedelta(days=1),
                status="Booked",
                organization_id=1
            )
            db.session.add(appt)
            db.session.commit()

            # Pre-populate existing sent MessageLog linked to this appointment
            log = MessageLog(
                organization_id=1,
                recipient_number=appt.customer_phone,
                message_type="WhatsApp",
                message_content="Prior reminder",
                status="Sent",
                related_appointment_id=appt.id,
                sent_at=datetime.utcnow()
            )
            db.session.add(log)
            db.session.commit()

            # Calling appointment_reminder should hit the idempotency guard
            res = appointment_reminder.apply(args=[appt.id]).get()
            self.assertEqual(res["status"], "already_sent")
            self.assertEqual(res["message_id"], log.id)

            db.session.delete(log)
            db.session.commit()
            db.session.delete(appt)
            db.session.commit()

    def test_reminder_respects_tenant_opt_out(self):
        """Ensures reminders are not sent if organization.reminders_enabled is False."""
        with self.app.app_context():
            org = Organization.query.get(1)
            original_setting = org.reminders_enabled
            try:
                org.reminders_enabled = False
                db.session.commit()

                appt = Appointment(
                    customer_name="Test OptOut User",
                    customer_phone="+919876543212",
                    appointment_date=datetime.utcnow() + timedelta(days=1),
                    status="Booked",
                    organization_id=1
                )
                db.session.add(appt)
                db.session.commit()

                res = appointment_reminder.apply(args=[appt.id]).get()
                self.assertEqual(res["status"], "tenant_reminders_disabled")

                db.session.delete(appt)
                db.session.commit()
            finally:
                org.reminders_enabled = original_setting
                db.session.commit()


if __name__ == "__main__":
    unittest.main()
