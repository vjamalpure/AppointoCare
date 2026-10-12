import io
import unittest
from app import create_app
from app.models import db, Organization, IndustryRecord, Appointment, AppointmentTransaction
from app.services.pdf_service import generate_prescription_pdf, generate_invoice_pdf, _safe_text
from app.utils.jwt_helper import generate_access_token


class PDFServiceTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def test_safe_text_escaping(self):
        """Ensures special characters are escaped to prevent ReportLab XML parser errors."""
        self.assertEqual(_safe_text("Amoxicillin <500mg> & Clavulanate"), "Amoxicillin &lt;500mg&gt; &amp; Clavulanate")
        self.assertEqual(_safe_text(None), "")
        self.assertEqual(_safe_text("Normal Text"), "Normal Text")

    def test_generate_prescription_pdf_produces_valid_pdf_stream(self):
        """Ensures generate_prescription_pdf outputs a valid PDF starting with %PDF."""
        org_data = {
            "name": "City Care Health & Dental",
            "code": "ORG1",
            "sector": "Healthcare",
            "address": "100 Medical Center Blvd",
            "phone": "+1 555-0101",
            "email": "care@citycare.com"
        }
        record_data = {
            "title": "Dr. Sarah Rx - Post-Op Antibiotic",
            "data": {
                "prescriber": "Dr. Sarah Jenkins, MD",
                "rx_number": "RX-2026-HC-001",
                "diagnosis": "Acute maxillary sinusitis",
                "vitals": {"bp": "120/80 mmHg", "pulse": "72 bpm", "spo2": "99%"},
                "medications": [
                    {"name": "Amoxicillin 500mg", "dosage": "1 tab 3x daily", "duration": "7 days", "instructions": "After food"}
                ],
                "advice": "Hydrate well and rest."
            }
        }
        appt_data = {
            "customer_name": "Michael Harrison",
            "customer_phone": "+1 555-1101",
            "staff_name": "Dr. Sarah Jenkins"
        }

        pdf_bytes = generate_prescription_pdf(org_data, record_data, appt_data)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"), "Generated stream must be a valid PDF format")
        self.assertGreater(len(pdf_bytes), 1000, "PDF must contain substantive layout elements")

    def test_generate_invoice_pdf_produces_valid_pdf_stream(self):
        """Ensures generate_invoice_pdf outputs a valid PDF starting with %PDF."""
        org_data = {
            "name": "Apex Aesthetics & Wellness Spa",
            "code": "ORG2",
            "sector": "Salon & Wellness",
            "address": "450 Westside Ave",
            "phone": "+1 555-0102",
            "email": "desk@apexaesthetics.com"
        }
        txn_data = {
            "id": 101,
            "amount": 180.0,
            "payment_method": "Razorpay UPI",
            "transaction_type": "Service Payment",
            "status": "Success",
            "created_at": "12 Oct 2026, 10:30 AM"
        }
        appt_data = {
            "customer_name": "Sarah Connor",
            "customer_phone": "+1 555-1102",
            "service_name": "Comprehensive Facial & Hydrotherapy"
        }

        pdf_bytes = generate_invoice_pdf(org_data, txn_data, appt_data)
        self.assertIsInstance(pdf_bytes, bytes)
        self.assertTrue(pdf_bytes.startswith(b"%PDF"), "Generated stream must be a valid PDF format")
        self.assertGreater(len(pdf_bytes), 1000)

    def test_cross_tenant_prescription_download_is_denied(self):
        """Ensures an organization cannot download prescription PDFs belonging to another tenant."""
        with self.app.app_context():
            # Get record belonging to ORG1
            rec = IndustryRecord.query.filter_by(organization_id=1).first()
            if not rec:
                self.skipTest("No seeded IndustryRecord found for org 1")

            # Generate token for ORG2 (Tenant ID 2)
            org2_token = generate_access_token(
                2,
                "Organization",
                extra_claims={"organization_id": "2", "role": "Organization", "username": "org2"}
            )

            headers = {"Authorization": f"Bearer {org2_token}"}
            res = self.client.get(f"/api/v1/industry-suite/records/{rec.id}/download-pdf", headers=headers)
            self.assertEqual(res.status_code, 403, "Cross-tenant record PDF access must return 403 Forbidden")

    def test_authorized_prescription_download_succeeds(self):
        """Ensures the owning organization can successfully download their own prescription PDF."""
        with self.app.app_context():
            rec = IndustryRecord.query.filter_by(organization_id=1).first()
            if not rec:
                self.skipTest("No seeded IndustryRecord found for org 1")

            org1_token = generate_access_token(
                1,
                "Organization",
                extra_claims={"organization_id": "1", "role": "Organization", "username": "org1"}
            )

            headers = {"Authorization": f"Bearer {org1_token}"}
            res = self.client.get(f"/api/v1/industry-suite/records/{rec.id}/download-pdf", headers=headers)
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.mimetype, "application/pdf")
            self.assertTrue(res.data.startswith(b"%PDF"))

    def test_authorized_invoice_download_succeeds(self):
        """Ensures an organization can download their appointment transaction receipt PDF."""
        with self.app.app_context():
            txn = AppointmentTransaction.query.filter_by(organization_id=1).first()
            if not txn:
                self.skipTest("No seeded AppointmentTransaction found for org 1")

            org1_token = generate_access_token(
                1,
                "Organization",
                extra_claims={"organization_id": "1", "role": "Organization", "username": "org1"}
            )
            headers = {"Authorization": f"Bearer {org1_token}"}
            res = self.client.get(f"/transactions/{txn.id}/download-pdf", headers=headers)
            self.assertEqual(res.status_code, 200)
            self.assertEqual(res.mimetype, "application/pdf")
            self.assertTrue(res.data.startswith(b"%PDF"))

    def test_cross_tenant_invoice_download_is_denied(self):
        """Ensures cross-tenant invoice download returns 403 Forbidden."""
        with self.app.app_context():
            txn = AppointmentTransaction.query.filter_by(organization_id=1).first()
            if not txn:
                self.skipTest("No seeded AppointmentTransaction found for org 1")

            org2_token = generate_access_token(
                2,
                "Organization",
                extra_claims={"organization_id": "2", "role": "Organization", "username": "org2"}
            )
            headers = {"Authorization": f"Bearer {org2_token}"}
            res = self.client.get(f"/transactions/{txn.id}/download-pdf", headers=headers)
            self.assertEqual(res.status_code, 403)


if __name__ == "__main__":
    unittest.main()

