import os
import unittest
from app import create_app
from app.service_guards import _resolve_tenant_id, check_whatsapp_active, check_razorpay_active
from flask import Flask, jsonify


class SecurityGuardsTestCase(unittest.TestCase):
    def test_production_secret_guard_blocks_weak_secret(self):
        """SEC-02: create_app() must raise RuntimeError in production when SECRET_KEY is default or weak."""
        orig_env = os.environ.get("APP_ENV")
        orig_key = os.environ.get("SECRET_KEY")
        try:
            os.environ["APP_ENV"] = "production"
            os.environ["SECRET_KEY"] = "supersecretkey"
            os.environ["JWT_SECRET_KEY"] = "jwtsecretkey"
            with self.assertRaises(RuntimeError) as ctx:
                create_app()
            self.assertIn("Insecure or default SECRET_KEY in production", str(ctx.exception))
        finally:
            if orig_env:
                os.environ["APP_ENV"] = orig_env
            else:
                os.environ.pop("APP_ENV", None)
            if orig_key:
                os.environ["SECRET_KEY"] = orig_key
            else:
                os.environ.pop("SECRET_KEY", None)

    def test_resolve_tenant_id_returns_none_when_unauthenticated_and_no_params(self):
        """SEC-01: _resolve_tenant_id() must NOT default to tenant 1 when no context is provided."""
        app = Flask(__name__)
        with app.test_request_context("/api/v1/whatsapp/webhook"):
            tenant_id = _resolve_tenant_id()
            self.assertIsNone(tenant_id, "Tenant resolution must be None when no tenant context is provided")

    def test_service_guards_block_when_tenant_missing(self):
        """SEC-01: check_whatsapp_active & check_razorpay_active must return HTTP 400 when tenant is missing."""
        app = Flask(__name__)

        @app.route("/test-wa")
        @check_whatsapp_active
        def mock_wa():
            return jsonify({"ok": True})

        @app.route("/test-rzp")
        @check_razorpay_active
        def mock_rzp():
            return jsonify({"ok": True})

        client = app.test_client()
        res_wa = client.get("/test-wa")
        self.assertEqual(res_wa.status_code, 400)
        self.assertEqual(res_wa.json.get("error"), "TENANT_REQUIRED")

        res_rzp = client.get("/test-rzp")
        self.assertEqual(res_rzp.status_code, 400)
        self.assertEqual(res_rzp.json.get("error"), "TENANT_REQUIRED")


if __name__ == "__main__":
    unittest.main()
