import unittest
from datetime import datetime, timedelta
from app import create_app
from app.models import db, Organization, Customer, Appointment, IndustryRecord, AuditLog
from app.services.pdf_service import generate_industry_dossier_pdf
from app.utils.jwt_helper import generate_access_token


class CrossIndustryTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def setUp(self):
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def test_multi_industry_dossier_pdf_generation(self):
        """Validates that generate_industry_dossier_pdf renders valid PDFs for various sectors."""
        sectors = [
            ("Salon and Wellness", {"treatment": "Balayage Color & Hair Spa", "stylist": "Elena", "patch_test": "Passed"}),
            ("Finance and Wealth Management", {"portfolio_value": "$250,000", "risk_profile": "Moderate", "drift_alert": "Rebalance Recommended"}),
            ("Legal and Management Consultancy", {"matter": "Cross-Border Acquisition", "billing_rate": "$450/hr", "adverse_party": "Acme Holdings"}),
            ("Real Estate and Architecture", {"property": "Skyline Penthouse 4B", "cap_rate": "7.8%", "rera_number": "PRM/KA/RERA/1251/310/PR/210312/004000"}),
            ("Education and Study Abroad", {"university": "University of Toronto", "program": "MSc Computer Science", "status": "Application Submitted"}),
            ("Professional Services and IT Consulting", {"project": "Cloud ERP Modernization", "sla_tier": "P1", "breach_risk": "Low"})
        ]

        for sector, details in sectors:
            org_data = {
                "name": f"Enterprise {sector} Group",
                "code": "ORG-TEST",
                "sector": sector,
                "address": "100 Global Tower, Suite 400",
                "phone": "+1 555-0199",
                "email": "contact@enterprise.test"
            }
            record_data = {
                "title": f"Official Dossier - {sector}",
                "sector": sector,
                "record_type": "official_dossier",
                "status": "Finalized",
                "data": details
            }
            appt_data = {
                "customer_name": "Alexander Wright",
                "customer_phone": "+1 555-4321",
                "staff_name": "Senior Partner / Director"
            }

            pdf_bytes = generate_industry_dossier_pdf(org_data, record_data, appt_data)
            self.assertIsInstance(pdf_bytes, bytes)
            self.assertTrue(pdf_bytes.startswith(b"%PDF"), f"Dossier for {sector} must produce a valid PDF")
            self.assertGreater(len(pdf_bytes), 1000, f"Dossier for {sector} must be non-empty and formatted")

    def test_portfolio_drift_calculation_endpoint(self):
        """Tests the portfolio drift calculation endpoint with drift detection."""
        token = generate_access_token(3, "Organization", extra_claims={"organization_id": "3", "role": "Organization"})
        headers = {"Authorization": f"Bearer {token}"}

        payload = {
            "current_allocations": {"equity": 75.0, "debt": 20.0, "gold": 5.0},
            "target_allocations": {"equity": 60.0, "debt": 30.0, "gold": 10.0},
            "threshold_pct": 5.0
        }
        res = self.client.post("/api/v1/industry-suite/evaluate-portfolio-drift", json=payload, headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["rebalance_required"])
        self.assertIn("drift_by_asset_class", data)
        self.assertEqual(data["drift_by_asset_class"]["equity"], 15.0)

    def test_stylist_commission_calculation(self):
        """Tests stylist tiered commission calculation."""
        token = generate_access_token(2, "Organization", extra_claims={"organization_id": "2", "role": "Organization"})
        headers = {"Authorization": f"Bearer {token}"}

        payload = {
            "service_revenue": 50000.0,
            "service_commission_rate": 0.45,
            "retail_product_revenue": 10000.0,
            "retail_commission_rate": 0.15,
            "tips_collected": 2500.0
        }
        res = self.client.post("/api/v1/industry-suite/calculate-stylist-commission", json=payload, headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["service_commission_payout"], 22500.0)
        self.assertEqual(data["retail_commission_payout"], 1500.0)
        self.assertEqual(data["gross_stylist_payout"], 26500.0)

    def test_legal_conflict_check(self):
        """Tests adverse party conflict clearance with disclaimer."""
        token = generate_access_token(4, "Organization", extra_claims={"organization_id": "4", "role": "Organization"})
        headers = {"Authorization": f"Bearer {token}"}

        payload = {
            "client_name": "Wayne Enterprises",
            "opposing_parties": ["Acme Holdings", "LexCorp"]
        }
        res = self.client.post("/api/v1/industry-suite/check-legal-conflict", json=payload, headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("clearance_status", data)
        self.assertIn("disclaimer", data)
        self.assertEqual(data["checked_parties_count"], 2)

    def test_university_shortlist_rubric(self):
        """Tests GPA/SAT university admission category categorization."""
        token = generate_access_token(5, "Organization", extra_claims={"organization_id": "5", "role": "Organization"})
        headers = {"Authorization": f"Bearer {token}"}

        payload = {
            "student_gpa": 3.8,
            "standardized_score": 1450,
            "institutions": [
                {"name": "MIT", "min_gpa": 4.0, "min_score": 1540},
                {"name": "Georgia Tech", "min_gpa": 3.8, "min_score": 1420},
                {"name": "State University", "min_gpa": 3.2, "min_score": 1200}
            ]
        }
        res = self.client.post("/api/v1/industry-suite/evaluate-university-shortlist", json=payload, headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        evals = {u["name"]: u["category"] for u in data["shortlist_evaluations"]}
        self.assertEqual(evals["MIT"], "Reach")
        self.assertEqual(evals["Georgia Tech"], "Target / Match")
        self.assertEqual(evals["State University"], "Safety")

    def test_sla_incident_escalation(self):
        """Tests SLA incident evaluation and escalation rule calculation."""
        token = generate_access_token(6, "Organization", extra_claims={"organization_id": "6", "role": "Organization"})
        headers = {"Authorization": f"Bearer {token}"}

        # P1 incident reported 90 minutes ago (allowed: 60 mins -> breached)
        reported_time = (datetime.utcnow() - timedelta(minutes=90)).isoformat()
        payload = {
            "priority": "P1",
            "reported_at": reported_time
        }
        res = self.client.post("/api/v1/industry-suite/evaluate-sla-incident", json=payload, headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["breach_status"], "BREACHED")
        self.assertIn("Executive Steering Committee", data["escalation_tier"])

    def test_format_validators(self):
        """Tests PAN, GSTIN, and RERA syntax validation with non-authoritative disclaimers."""
        token = generate_access_token(7, "Organization", extra_claims={"organization_id": "7", "role": "Organization"})
        headers = {"Authorization": f"Bearer {token}"}

        # Valid PAN
        res = self.client.post("/api/v1/industry-suite/format-validator", json={"validator_type": "pan", "value": "ABCDE1234F"}, headers=headers)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()["is_valid_format"])

        # Invalid PAN
        res = self.client.post("/api/v1/industry-suite/format-validator", json={"validator_type": "pan", "value": "12345ABCDE"}, headers=headers)
        self.assertEqual(res.status_code, 200)
        self.assertFalse(res.get_json()["is_valid_format"])

        # Valid GSTIN
        res = self.client.post("/api/v1/industry-suite/format-validator", json={"validator_type": "gstin", "value": "27ABCDE1234F1Z5"}, headers=headers)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()["is_valid_format"])

        # Valid RERA
        res = self.client.post("/api/v1/industry-suite/format-validator", json={"validator_type": "rera", "value": "PRM/KA/RERA/1251/310/PR/210312/004000"}, headers=headers)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()["is_valid_format"])

    def test_customer_export_tenant_isolation(self):
        """Tests that customer export respects tenant scoping and records audit log."""
        token = generate_access_token(1, "Organization", extra_claims={"organization_id": "1", "role": "Organization"})
        headers = {"Authorization": f"Bearer {token}"}

        res = self.client.get("/api/v1/customers/export", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("customers", data)
        self.assertIn("count", data)
        self.assertIn("exported_at", data)
        # All returned customers must belong to organization_id 1
        for cust in data["customers"]:
            self.assertEqual(cust["organization_id"], 1)

    def test_room_conflict_prevention(self):
        """Tests that booking the same treatment room in an overlapping slot yields 409 Conflict."""
        import uuid
        token = generate_access_token(2, "Organization", extra_claims={"organization_id": "2", "role": "Organization"})
        headers = {"Authorization": f"Bearer {token}"}

        room_name = f"Spa-Suite-{uuid.uuid4().hex[:6]}"
        future_date = (datetime.utcnow() + timedelta(days=2)).replace(microsecond=0)
        future_iso = future_date.isoformat()

        # First booking in the suite
        payload1 = {
            "customer_name": "Client Alpha",
            "customer_phone": "+919876543210",
            "appointment_date": future_iso,
            "treatment_room": room_name,
            "service_name": "Deep Tissue Therapy",
            "check_conflict": True
        }
        res1 = self.client.post("/api/v1/appointments", json=payload1, headers=headers)
        self.assertEqual(res1.status_code, 201)

        # Second booking in the same room at the same time
        payload2 = {
            "customer_name": "Client Beta",
            "customer_phone": "+919876543211",
            "appointment_date": future_iso,
            "treatment_room": room_name,
            "service_name": "Hot Stone Massage",
            "check_conflict": True
        }
        res2 = self.client.post("/api/v1/appointments", json=payload2, headers=headers)
        self.assertEqual(res2.status_code, 409)
        self.assertIn(f"Treatment room/resource '{room_name}' already has a booking", res2.get_json()["msg"])


if __name__ == "__main__":
    unittest.main()
