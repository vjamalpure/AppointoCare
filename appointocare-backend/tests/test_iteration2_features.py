import unittest
from datetime import datetime, timedelta
from app import create_app
from app.models import db, Organization, Customer, Appointment, IndustryRecord, AuditLog
from app.utils.jwt_helper import generate_access_token


class Iteration2FeaturesTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def setUp(self):
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        self.ctx.pop()

    def test_crm_export_csv(self):
        """Validates that customer export supports CSV format with appropriate headers."""
        token = generate_access_token(1, "Organization", extra_claims={"organization_id": "1", "role": "Organization"})
        headers = {"Authorization": f"Bearer {token}"}

        res = self.client.get("/api/v1/customers/export?format=csv", headers=headers)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content_type, "text/csv; charset=utf-8")
        self.assertIn("attachment; filename=customers_export_1.csv", res.headers.get("Content-Disposition", ""))
        csv_text = res.get_data(as_text=True)
        self.assertTrue(csv_text.startswith("ID,Name,Phone,Email"))

    def test_salon_session_credit_redemption(self):
        """Zenoti / Fresha benchmark: Package session credit debit and balance accounting."""
        token = generate_access_token(2, "Organization", extra_claims={"organization_id": "2", "role": "Organization"})
        headers = {"Authorization": f"Bearer {token}"}

        # Find or create a record for Org 2
        rec = IndustryRecord.query.filter_by(organization_id=2).first()
        self.assertIsNotNone(rec, "Should find a record for Org 2")

        # Initial seed with 5 credits
        rec_data = dict(rec.data or {})
        rec_data["total_sessions"] = 5
        rec_data["remaining_sessions"] = 5
        rec.data = rec_data
        db.session.commit()

        # Redeem 2 credits
        payload = {
            "sessions_to_redeem": 2,
            "service_name": "Aromatherapy Massage",
            "staff_name": "Olivia Spa Lead",
            "notes": "Client requested lavender oil"
        }
        res = self.client.post(f"/api/v1/industry-suite/records/{rec.id}/redeem-session-credit", json=payload, headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["remaining_credits"], 3)
        self.assertEqual(data["sessions_redeemed"], 2)

        # Attempt to overdraw with 10 credits -> 400
        res_over = self.client.post(f"/api/v1/industry-suite/records/{rec.id}/redeem-session-credit", json={"sessions_to_redeem": 10}, headers=headers)
        self.assertEqual(res_over.status_code, 400)
        self.assertIn("Insufficient session credits", res_over.get_json()["msg"])

    def test_legal_log_billable_time(self):
        """Clio benchmark: Billable time tracking and retainer depletion alerts."""
        token = generate_access_token(7, "Organization", extra_claims={"organization_id": "7", "role": "Organization"})
        headers = {"Authorization": f"Bearer {token}"}

        rec = IndustryRecord.query.filter_by(organization_id=7).first()
        self.assertIsNotNone(rec, "Should find a record for Org 7")

        rec_data = dict(rec.data or {})
        rec_data["retainer_hours_remaining"] = 3.0
        rec.data = rec_data
        db.session.commit()

        # Log 2.0 billable hours (leaving 1.0 hour -> alerts depletion!)
        payload = {
            "hours": 2.0,
            "hourly_rate": 15000.0,
            "activity_description": "Merger agreement review and indemnification clauses",
            "lawyer_name": "Senior Partner Eleanor"
        }
        res = self.client.post(f"/api/v1/industry-suite/records/{rec.id}/log-billable-time", json=payload, headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["billable_amount"], 30000.0)
        self.assertEqual(data["retainer_hours_remaining"], 1.0)
        self.assertTrue(data["retainer_depleted_alert"])

    def test_insurance_claim_transition(self):
        """Applied Epic benchmark: Claim lifecycle transition machine."""
        token = generate_access_token(4, "Organization", extra_claims={"organization_id": "4", "role": "Organization"})
        headers = {"Authorization": f"Bearer {token}"}

        rec = IndustryRecord.query.filter_by(organization_id=4).first()
        self.assertIsNotNone(rec, "Should find a record for Org 4")

        # Invalid transition status -> 400
        res_bad = self.client.post(f"/api/v1/industry-suite/records/{rec.id}/transition-claim-status", json={"new_status": "NonExistentStatus"}, headers=headers)
        self.assertEqual(res_bad.status_code, 400)

        # Valid transition to Approved
        payload = {
            "new_status": "Approved",
            "adjuster_notes": "Surveyor documentation verified. Critical illness diagnosis confirmed.",
            "approved_amount": 750000.0
        }
        res = self.client.post(f"/api/v1/industry-suite/records/{rec.id}/transition-claim-status", json=payload, headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["current_status"], "Approved")
        self.assertEqual(data["approved_amount"], 750000.0)

    def test_retail_alteration_stage(self):
        """Shopify POS / Clienteling benchmark: Alteration stage progression with ready notification."""
        token = generate_access_token(5, "Organization", extra_claims={"organization_id": "5", "role": "Organization"})
        headers = {"Authorization": f"Bearer {token}"}

        rec = IndustryRecord.query.filter_by(organization_id=5).first()
        self.assertIsNotNone(rec, "Should find a record for Org 5")

        # Advance to Ready_For_Fitting
        payload = {
            "stage": "Ready_For_Fitting",
            "tailor_notes": "Tuxedo lapel adjustments complete. Pressed and hung in VIP fitting suite.",
            "fitting_suite": "Platinum Lounge 1"
        }
        res = self.client.post(f"/api/v1/industry-suite/records/{rec.id}/update-alteration-stage", json=payload, headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["current_stage"], "Ready_For_Fitting")
        self.assertTrue(data["ready_for_fitting"])
        self.assertTrue(data["notification_dispatched"])

    def test_education_application_milestone(self):
        """Naviance / Teachmint benchmark: Student application milestone advancement."""
        token = generate_access_token(6, "Organization", extra_claims={"organization_id": "6", "role": "Organization"})
        headers = {"Authorization": f"Bearer {token}"}

        rec = IndustryRecord.query.filter_by(organization_id=6).first()
        self.assertIsNotNone(rec, "Should find a record for Org 6")

        payload = {
            "milestone": "Interview_Scheduled",
            "institution_name": "University of Oxford",
            "deadline_date": "2026-11-15",
            "counselor_notes": "Admissions interview confirmed with department chair."
        }
        res = self.client.post(f"/api/v1/industry-suite/records/{rec.id}/update-application-milestone", json=payload, headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["current_milestone"], "Interview_Scheduled")
        self.assertEqual(data["institution"], "University of Oxford")

    def test_healthcare_followup_scheduling(self):
        """Practo Ray benchmark: Automatic follow-up appointment booking."""
        token = generate_access_token(1, "Organization", extra_claims={"organization_id": "1", "role": "Organization"})
        headers = {"Authorization": f"Bearer {token}"}

        parent_appt = Appointment.query.filter_by(organization_id=1).first()
        self.assertIsNotNone(parent_appt, "Should find an appointment for Org 1")

        followup_date = (datetime.utcnow() + timedelta(days=7)).replace(microsecond=0).isoformat()
        payload = {
            "followup_date": followup_date,
            "service_name": "Post-Op Wound Check & Stitch Removal",
            "notes": "Bring prior prescription"
        }
        res = self.client.post(f"/api/v1/industry-suite/appointments/{parent_appt.id}/schedule-followup", json=payload, headers=headers)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertEqual(data["parent_appointment_id"], parent_appt.id)
        self.assertIn("followup_appointment_id", data)

    def test_realestate_tour_itinerary(self):
        """Dotloop / Sell.do benchmark: Tour itinerary with map navigation URLs."""
        token = generate_access_token(8, "Organization", extra_claims={"organization_id": "8", "role": "Organization"})
        headers = {"Authorization": f"Bearer {token}"}

        rec = IndustryRecord.query.filter_by(organization_id=8).first()
        self.assertIsNotNone(rec, "Should find a record for Org 8")

        payload = {
            "tour_date": "2026-10-15",
            "agent_name": "Marcus Luxury Realtor",
            "tour_stops": [
                {"address": "100 Skyline Tower, Penthouse 40", "time": "10:00 AM", "lockbox": "1234"},
                {"address": "45 Oceanfront Boulevard, Villa 2", "time": "12:30 PM", "lockbox": "5678"}
            ]
        }
        res = self.client.post(f"/api/v1/industry-suite/records/{rec.id}/create-tour-itinerary", json=payload, headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["stops_count"], 2)
        self.assertIn("https://www.google.com/maps", data["itinerary"][0]["navigation_url"])

    def test_professional_services_milestone_approval(self):
        """Jira SM / Odoo benchmark: Client deliverable milestone sign-off."""
        token = generate_access_token(9, "Organization", extra_claims={"organization_id": "9", "role": "Organization"})
        headers = {"Authorization": f"Bearer {token}"}

        rec = IndustryRecord.query.filter_by(organization_id=9).first()
        self.assertIsNotNone(rec, "Should find a record for Org 9")

        payload = {
            "milestone_id": "MS-03",
            "milestone_name": "Cloud Security Architecture Final Delivery",
            "approved_by": "Dr. Aris Thorne",
            "approval_role": "Chief Information Security Officer",
            "comments": "Meets SOC2 requirements and passes all penetration tests."
        }
        res = self.client.post(f"/api/v1/industry-suite/records/{rec.id}/approve-milestone", json=payload, headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["milestone_name"], "Cloud Security Architecture Final Delivery")
        self.assertEqual(data["approved_by"], "Dr. Aris Thorne")

    def test_finance_rebalance_plan(self):
        """Wealthbox / Zoho Books benchmark: Portfolio rebalancing trade order sheet."""
        token = generate_access_token(3, "Organization", extra_claims={"organization_id": "3", "role": "Organization"})
        headers = {"Authorization": f"Bearer {token}"}

        payload = {
            "portfolio_value": 1000000.0,
            "current_weights": {"equity": 70.0, "debt": 25.0, "gold": 5.0},
            "target_weights": {"equity": 50.0, "debt": 40.0, "gold": 10.0},
            "fee_bps": 15.0
        }
        res = self.client.post("/api/v1/industry-suite/generate-rebalance-plan", json=payload, headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        # Equity: shift -200,000 (SELL), Debt: shift +150,000 (BUY), Gold: shift +50,000 (BUY)
        # Total turnover: 400,000. Fees: 400,000 * 0.0015 = 600.0
        self.assertEqual(data["total_turnover"], 400000.0)
        self.assertEqual(data["estimated_execution_fees"], 600.0)
        orders = {o["asset_class"]: o["trade_action"] for o in data["rebalance_orders"]}
        self.assertEqual(orders["equity"], "SELL")
        self.assertEqual(orders["debt"], "BUY")
        self.assertEqual(orders["gold"], "BUY")

    def test_cross_tenant_isolation_iteration2(self):
        """Guarantees that Org 1 cannot redeem credits or transition claims on Org 2's records."""
        token_org1 = generate_access_token(1, "Organization", extra_claims={"organization_id": "1", "role": "Organization"})
        headers = {"Authorization": f"Bearer {token_org1}"}

        # Target a record belonging to Org 2
        rec_org2 = IndustryRecord.query.filter_by(organization_id=2).first()
        self.assertIsNotNone(rec_org2)

        res = self.client.post(f"/api/v1/industry-suite/records/{rec_org2.id}/redeem-session-credit", json={"sessions_to_redeem": 1}, headers=headers)
        self.assertEqual(res.status_code, 403)


if __name__ == "__main__":
    unittest.main()
