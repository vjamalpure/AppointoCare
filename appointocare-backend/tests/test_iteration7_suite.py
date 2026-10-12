"""
AppointoCare Iteration 7 Executive Analytics & Access Control Verification Suite
Tests:
1. Super Admin Executive Analytics endpoint authorization & financial segregation
2. Super Admin Executive Analytics payload schema & 9-sector distribution
3. Organization Executive Dashboard server-side aggregates & bounded pagination
4. Strict multi-tenant isolation on analytics endpoints
5. Access control guards: SuperAdmin vs Organization vs Staff access boundaries
"""

import unittest
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token
from app import create_app
from app.models import (
    db, Organization, User, Appointment, AppointmentTransaction,
    OrganizationTransaction, Admin
)
from app.utils.hash_helper import hash_password


class TestIteration7Suite(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

        # 1. SuperAdmin User
        self.admin = Admin.query.filter_by(username="superadmin").first()
        if not self.admin:
            self.admin = Admin(
                username="superadmin",
                password=hash_password("Admin@12345"),
                email="admin@appointocare.com",
                role="SuperAdmin"
            )
            db.session.add(self.admin)
            db.session.commit()

        # 2. Org 1 (Healthcare)
        self.org1 = db.session.get(Organization, 1)
        if not self.org1:
            self.org1 = Organization(
                name="City Health Hospital",
                code="ORG-HLTH-01",
                sector="Healthcare",
                username="city_health_admin",
                password=hash_password("Pass@1234"),
                subscription_plan="Enterprise",
                subscription_status="Active"
            )
            db.session.add(self.org1)
            db.session.commit()

        # 3. Org 2 (Salon & Wellness)
        self.org2 = db.session.get(Organization, 2)
        if not self.org2:
            self.org2 = Organization(
                name="Elite Glow Salon",
                code="ORG-GLOW-02",
                sector="Salon & Wellness",
                username="elite_glow_admin",
                password=hash_password("Pass@1234"),
                subscription_plan="Professional",
                subscription_status="Active"
            )
            db.session.add(self.org2)
            db.session.commit()

        # 4. Doctor User in Org 1
        self.doctor = User.query.filter_by(username="dr_sarah_iter7").first()
        if not self.doctor:
            self.doctor = User(
                organization_id=self.org1.id,
                username="dr_sarah_iter7",
                password=hash_password("Pass@1234"),
                role="Doctor",
                is_active=True
            )
            db.session.add(self.doctor)
            db.session.commit()

        # 5. Populate test appointments for Org 1
        appt1 = Appointment.query.filter_by(organization_id=self.org1.id, customer_phone="9998881111").first()
        if not appt1:
            appt1 = Appointment(
                organization_id=self.org1.id,
                customer_name="John Patient",
                customer_phone="9998881111",
                appointment_date=datetime.utcnow() - timedelta(days=2),
                status="Completed",
                payment_status="Paid",
                service_name="Consultation"
            )
            db.session.add(appt1)
            db.session.commit()

            txn1 = AppointmentTransaction(
                organization_id=self.org1.id,
                appointment_id=appt1.id,
                amount=1200.0,
                transaction_type="Payment",
                payment_method="Stripe",
                status="Success"
            )
            db.session.add(txn1)
            db.session.commit()

        # Generate tokens
        self.admin_token = create_access_token(
            identity=str(self.admin.id),
            additional_claims={"role": "SuperAdmin", "sub": "superadmin"}
        )
        self.org1_token = create_access_token(
            identity=str(self.org1.id),
            additional_claims={"role": "Organization", "organization_id": self.org1.id, "sub": str(self.org1.id)}
        )
        self.org2_token = create_access_token(
            identity=str(self.org2.id),
            additional_claims={"role": "Organization", "organization_id": self.org2.id, "sub": str(self.org2.id)}
        )
        self.doctor_token = create_access_token(
            identity=str(self.doctor.id),
            additional_claims={"role": "Doctor", "organization_id": self.org1.id, "sub": "dr_sarah_iter7"}
        )

    def tearDown(self):
        self.app_context.pop()

    # -------------------------------------------------------------
    # 1. Super Admin Executive Analytics Endpoint Security
    # -------------------------------------------------------------
    def test_admin_dashboard_analytics_unauthorized(self):
        """Unauthenticated calls to /api/v1/admin/dashboard-analytics must return 401."""
        res = self.client.get("/api/v1/admin/dashboard-analytics")
        self.assertEqual(res.status_code, 401)

    def test_admin_dashboard_analytics_forbidden_for_tenant(self):
        """Tenant organization token cannot access Super Admin executive analytics (returns 403)."""
        res = self.client.get(
            "/api/v1/admin/dashboard-analytics",
            headers={"Authorization": f"Bearer {self.org1_token}"}
        )
        self.assertEqual(res.status_code, 403)

    def test_admin_dashboard_analytics_success_for_admin(self):
        """Super Admin token receives 200 OK with fully structured analytics response."""
        res = self.client.get(
            "/api/v1/admin/dashboard-analytics",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        # Validate top-level response contracts
        self.assertIn("summary", data)
        self.assertIn("sector_distribution", data)
        self.assertIn("subscription_breakdown", data)
        self.assertIn("monthly_revenue_history", data)
        self.assertIn("payment_health", data)
        self.assertIn("integration_health", data)
        self.assertIn("recent_activity", data)

        # Validate Financial Segregation (Never conflate SaaS revenue with GMV)
        summary = data["summary"]
        self.assertIn("saas_revenue", summary)
        self.assertIn("tenant_gmv", summary)
        self.assertIn("platform_commission", summary)
        self.assertIn("refunds_total", summary)
        self.assertIsInstance(summary["saas_revenue"], (int, float))
        self.assertIsInstance(summary["tenant_gmv"], (int, float))
        self.assertIsInstance(summary["platform_commission"], (int, float))

        # Commission must be 5% of GMV
        expected_commission = round(summary["tenant_gmv"] * 0.05, 2)
        self.assertEqual(summary["platform_commission"], expected_commission)

        # Validate 12-month historical breakdown
        history = data["monthly_revenue_history"]
        self.assertEqual(len(history), 12)
        for m in history:
            self.assertIn("month_label", m)
            self.assertIn("saas_revenue", m)
            self.assertIn("tenant_gmv", m)
            self.assertIn("booking_volume", m)

    # -------------------------------------------------------------
    # 2. Organization Executive Dashboard Server-Side Aggregates
    # -------------------------------------------------------------
    def test_org_dashboard_unauthorized(self):
        """Unauthenticated requests to /organization/dashboard must return 401."""
        res = self.client.get("/organization/dashboard")
        self.assertEqual(res.status_code, 401)

    def test_org_dashboard_admin_token_rejected(self):
        """SuperAdmin token without org context receives 403 for tenant dashboard."""
        res = self.client.get(
            "/organization/dashboard",
            headers={"Authorization": f"Bearer {self.admin_token}"}
        )
        self.assertEqual(res.status_code, 403)

    def test_org_dashboard_server_aggregates_and_bounding(self):
        """Organization dashboard returns SQL aggregates in 'metrics' and bounds recent appointments."""
        res = self.client.get(
            "/organization/dashboard",
            headers={"Authorization": f"Bearer {self.org1_token}"}
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        # Validate backward-compatible fields
        self.assertIn("organization", data)
        self.assertIn("appointments", data)
        self.assertIn("appointments_count", data)

        # Validate server-side SQL metrics
        self.assertIn("metrics", data)
        metrics = data["metrics"]
        self.assertIn("total_appointments", metrics)
        self.assertIn("completed_count", metrics)
        self.assertIn("total_paid", metrics)
        self.assertIn("trend_30d", metrics)
        self.assertIsInstance(metrics["trend_30d"], list)

        # Appointments list must be bounded (<= 15 items)
        self.assertLessEqual(len(data["appointments"]), 15)

    def test_org_dashboard_doctor_staff_access(self):
        """Doctor staff member can access their organization's dashboard."""
        res = self.client.get(
            "/organization/dashboard",
            headers={"Authorization": f"Bearer {self.doctor_token}"}
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["organization"]["id"], self.org1.id)

    # -------------------------------------------------------------
    # 3. Cross-Tenant Analytics Isolation
    # -------------------------------------------------------------
    def test_tenant_isolation_org1_cannot_see_org2_data(self):
        """Org 2 dashboard returns strictly Org 2 data without leaking Org 1 records."""
        res2 = self.client.get(
            "/organization/dashboard",
            headers={"Authorization": f"Bearer {self.org2_token}"}
        )
        self.assertEqual(res2.status_code, 200)
        data2 = res2.get_json()
        self.assertEqual(data2["organization"]["id"], self.org2.id)

        # None of Org 1's appointments should appear in Org 2's list
        for appt in data2["appointments"]:
            self.assertNotEqual(appt.get("customer_phone"), "9998881111")


if __name__ == "__main__":
    unittest.main()
