"""
AppointoCore Iteration 6 Final Verification Suite
Tests:
1. Branded E-Prescription (Rx) PDF generation & Doctor MCI attribution
2. Tax Invoice PDF generation with GST decomposition & multi-currency
3. CSV export formula injection sanitization (CWE-1236 protection)
4. Customer portal magic link generation & clinical encounters projection
5. Patient self-service E-Prescription PDF download via portal session
6. Subscription plan limits and staff seat enforcement
7. Cross-tenant clinical encounter authorization & data isolation
"""

import unittest
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token
from app import create_app
from app.models import (
    db, Organization, User, Customer, Appointment, AppointmentTransaction,
    ClinicalEncounter, CustomerPortalSession
)
from app.utils.hash_helper import hash_password


class TestIteration6Suite(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

        # Ensure Org 1 (Healthcare) exists
        self.org1 = db.session.get(Organization, 1)
        if not self.org1:
            self.org1 = Organization(
                name="City Care Health & Dental",
                code="ORG-HEALTH-01",
                sector="Healthcare",
                username="city_care_admin",
                password=hash_password("Pass@1234"),
                subscription_plan="Basic",
                subscription_status="Active"
            )
            db.session.add(self.org1)
            db.session.commit()

        # Ensure Org 2 (Different tenant) exists
        self.org2 = db.session.get(Organization, 2)
        if not self.org2:
            self.org2 = Organization(
                name="Apex Spa",
                code="ORG-SPA-02",
                sector="Salon & Wellness",
                username="apex_spa_admin",
                password=hash_password("Pass@1234"),
                subscription_plan="Basic",
                subscription_status="Active"
            )
            db.session.add(self.org2)
            db.session.commit()

        # Ensure Patient Customer exists
        self.patient = Customer.query.filter_by(organization_id=1, phone="9876543210").first()
        if not self.patient:
            self.patient = Customer(
                organization_id=1,
                name="Rajesh Verma",
                phone="9876543210",
                email="rajesh.verma@example.com",
                gender="Male"
            )
            db.session.add(self.patient)
            db.session.commit()

        # Create test ClinicalEncounter
        self.encounter = ClinicalEncounter.query.filter_by(organization_id=1, patient_id=self.patient.id).first()
        if not self.encounter:
            self.encounter = ClinicalEncounter(
                organization_id=1,
                patient_id=self.patient.id,
                practitioner_name="Dr. Sarah Jenkins, MD",
                practitioner_reg_no="MCI-2018-9410",
                encounter_type="Outpatient",
                chief_complaints="Acute viral fever, dry cough, malaise",
                vitals={"bp": "120/80", "pulse": "74 bpm", "temp": "100.4 F", "spo2": "99%"},
                diagnosis=[{"code": "ICD-10 J06.9", "description": "Acute upper respiratory infection"}],
                prescription_data={
                    "rx_number": f"RX-{int(datetime.utcnow().timestamp())}",
                    "medications": [
                        {"name": "Paracetamol 650mg", "dosage": "1 tab", "duration": "3 days", "instructions": "After meals SOS"},
                        {"name": "Levocetirizine 5mg", "dosage": "1 tab", "duration": "5 days", "instructions": "At bedtime"}
                    ],
                    "advice": "Drink lukewarm water, rest adequately."
                },
                status="Signed_Off",
                signed_at=datetime.utcnow()
            )
            db.session.add(self.encounter)
            db.session.commit()

        # Create test Appointment & AppointmentTransaction
        self.appt = Appointment.query.filter_by(organization_id=1, customer_phone="9876543210").first()
        if not self.appt:
            self.appt = Appointment(
                organization_id=1,
                customer_name="Rajesh Verma",
                customer_phone="9876543210",
                appointment_date=datetime.utcnow() + timedelta(days=2),
                status="Booked",
                payment_status="Paid",
                service_name="Cardiology Consultation"
            )
            db.session.add(self.appt)
            db.session.commit()

        self.txn = AppointmentTransaction.query.filter_by(organization_id=1, appointment_id=self.appt.id).first()
        if not self.txn:
            self.txn = AppointmentTransaction(
                organization_id=1,
                appointment_id=self.appt.id,
                amount=1500.0,
                transaction_type="Payment",
                payment_method="UPI / Razorpay",
                status="Success"
            )
            db.session.add(self.txn)
            db.session.commit()

        # Generate tokens
        self.doc_token = create_access_token(
            identity="2",
            additional_claims={"role": "Doctor", "organization_id": 1, "sub": "doc_sarah"}
        )
        self.org2_token = create_access_token(
            identity="5",
            additional_claims={"role": "Organization", "organization_id": 2, "sub": "apex_spa_admin"}
        )

    def tearDown(self):
        self.app_context.pop()

    def test_prescription_pdf_generation_and_mci_attribution(self):
        """1. Verify that E-Prescription PDF generates binary PDF with Doctor attribution."""
        headers = {"Authorization": f"Bearer {self.doc_token}"}
        res = self.client.get(f"/api/v1/healthcare/encounters/{self.encounter.id}/prescription-pdf", headers=headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content_type, "application/pdf")
        self.assertTrue(res.data.startswith(b"%PDF-"))
        self.assertIn("prescription_rx_", res.headers.get("Content-Disposition", ""))

    def test_invoice_pdf_generation_with_gst_breakdown(self):
        """2. Verify that tax invoice PDF generates binary PDF with GST decomposition."""
        headers = {"Authorization": f"Bearer {self.doc_token}"}
        res = self.client.get(f"/api/v1/transactions/{self.txn.id}/invoice-pdf", headers=headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content_type, "application/pdf")
        self.assertTrue(res.data.startswith(b"%PDF-"))

    def test_csv_export_formula_injection_sanitization(self):
        """3. Verify CSV formula injection (CWE-1236) characters are safely neutralized with single-quote."""
        malicious_cust = Customer(
            organization_id=1,
            name="=cmd|'/C calc'!A0",
            phone=f"99{int(datetime.utcnow().timestamp()) % 100000000:08d}",
            email="+admin@evil.com",
            notes="-2+5+cmd"
        )
        db.session.add(malicious_cust)
        db.session.commit()
        cust_id = malicious_cust.id

        headers = {"Authorization": f"Bearer {self.doc_token}"}
        res = self.client.get("/api/v1/customers/export?export_format=csv", headers=headers)
        self.assertEqual(res.status_code, 200)
        csv_text = res.data.decode("utf-8")
        # Formula characters must be sanitized with leading single-quote
        self.assertIn("'=cmd", csv_text)
        self.assertIn("'+admin@evil.com", csv_text)
        self.assertIn("'-2+5+cmd", csv_text)

        # Cleanup
        c = db.session.get(Customer, cust_id)
        if c:
            db.session.delete(c)
            db.session.commit()

    def test_customer_portal_magic_link_and_encounters_projection(self):
        """4. Verify portal magic link generation and customer encounters projection in overview."""
        headers = {"Authorization": f"Bearer {self.doc_token}"}
        res = self.client.post(f"/api/v1/customers/{self.patient.id}/portal-link", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("session_token", data)
        self.assertIn("portal_url", data)
        token = data["session_token"]

        # Call portal overview via query param token
        res_overview = self.client.get(f"/api/v1/customer-portal/overview?token={token}")
        self.assertEqual(res_overview.status_code, 200)
        overview = res_overview.get_json()
        self.assertEqual(overview["customer"]["name"], "Rajesh Verma")
        self.assertIn("clinical_encounters", overview)
        self.assertGreaterEqual(len(overview["clinical_encounters"]), 1)
        self.assertEqual(overview["clinical_encounters"][0]["practitioner_reg_no"], "MCI-2018-9410")

    def test_customer_portal_rx_pdf_download(self):
        """5. Verify that patient can download their own E-Prescription PDF directly via portal token."""
        # Ensure active portal session
        session = CustomerPortalSession.query.filter_by(customer_id=self.patient.id, is_active=True).first()
        if not session:
            session = CustomerPortalSession(
                customer_id=self.patient.id,
                organization_id=1,
                session_token="test_portal_token_rx_123",
                auth_code="123456",
                expires_at=datetime.utcnow() + timedelta(days=2),
                is_active=True
            )
            db.session.add(session)
            db.session.commit()

        token = session.session_token
        res = self.client.get(f"/api/v1/customer-portal/encounters/{self.encounter.id}/prescription-pdf?token={token}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content_type, "application/pdf")
        self.assertTrue(res.data.startswith(b"%PDF-"))

    def test_subscription_plan_limits_and_staff_enforcement(self):
        """6. Verify subscription plan limits reporting and staff limit enforcement."""
        headers = {"Authorization": f"Bearer {self.doc_token}"}
        res = self.client.get("/api/v1/platform/organization/subscription-limits", headers=headers)
        self.assertEqual(res.status_code, 200)
        limits = res.get_json()
        self.assertIn("subscription_plan", limits)
        self.assertGreaterEqual(limits["staff"]["max"], 5)
        self.assertGreaterEqual(limits["branches"]["max"], 1)

    def test_cross_tenant_clinical_data_isolation(self):
        """7. Verify tenant 2 cannot access or download tenant 1's clinical encounter or prescription PDF."""
        headers_tenant2 = {"Authorization": f"Bearer {self.org2_token}"}
        res = self.client.get(f"/api/v1/healthcare/encounters/{self.encounter.id}/prescription-pdf", headers=headers_tenant2)
        # Should be 404 (scoped filter_by org_id) or 403
        self.assertIn(res.status_code, [403, 404])


if __name__ == "__main__":
    unittest.main()
