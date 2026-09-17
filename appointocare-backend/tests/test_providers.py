import hashlib
import hmac
import json
import os
import unittest

os.environ["DATABASE_URL"] = "sqlite:///provider-test.db"
os.environ["SECRET_KEY"] = "test-secret"
os.environ["JWT_SECRET_KEY"] = "test-jwt-secret"
os.environ["RAZORPAY_WEBHOOK_SECRET"] = "webhook-secret"
os.environ["WHATSAPP_WEBHOOK_VERIFY_TOKEN"] = "verify-token"

from app import create_app, db
from app.models import ProviderEvent
from app.providers.payment import get_payment_provider
from app.providers.base import ProviderState


class ProviderTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config.update(TESTING=True)

    def setUp(self):
        self.app.config.update(
            RAZORPAY_WEBHOOK_SECRET="webhook-secret",
            WHATSAPP_WEBHOOK_VERIFY_TOKEN="verify-token",
        )
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()
        try:
            os.remove("provider-test.db")
        except FileNotFoundError:
            pass

    def test_mock_payment_provider_is_available_without_credentials(self):
        with self.app.app_context():
            self.assertEqual(get_payment_provider().state, ProviderState.CONFIGURED)
            self.assertEqual(get_payment_provider().name, "mock")

    def test_razorpay_webhook_is_idempotent(self):
        payload = {"id": "evt_1", "event": "payment.captured", "payload": {}}
        raw = json.dumps(payload).encode()
        signature = hmac.new(b"webhook-secret", raw, hashlib.sha256).hexdigest()
        first = self.client.post("/api/v1/providers/webhooks/razorpay", data=raw, content_type="application/json", headers={"X-Razorpay-Signature": signature})
        second = self.client.post("/api/v1/providers/webhooks/razorpay", data=raw, content_type="application/json", headers={"X-Razorpay-Signature": signature})
        self.assertEqual(first.json["status"], "processed")
        self.assertEqual(second.json["status"], "duplicate")
        with self.app.app_context():
            self.assertEqual(ProviderEvent.query.count(), 1)

    def test_whatsapp_verification(self):
        response = self.client.get("/api/v1/providers/webhooks/whatsapp?hub.verify_token=verify-token&hub.challenge=challenge")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "challenge")


if __name__ == "__main__":
    unittest.main()
