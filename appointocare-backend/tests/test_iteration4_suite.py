import unittest
import io
import json
from app import create_app, db
from app.models import (
    Organization, Customer, IndustryRecord, Appointment,
    CustomFieldDefinition, WorkflowDefinition, WorkflowTransitionHistory,
    AutomationRule, CustomerPortalSession, CustomerDocument
)
from app.utils.jwt_helper import generate_access_token


class Iteration4SuiteTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def setUp(self):
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        db.session.remove()
        self.ctx.pop()

    def test_custom_field_definitions_and_creation(self):
        """Validates auto-seeding of sector custom fields and tenant custom field creation."""
        token = generate_access_token(1, "Organization", extra_claims={"organization_id": "1", "role": "Organization"})
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Fetch custom fields (auto-seeds defaults if empty)
        res = self.client.get("/api/v1/custom-fields/definitions", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["organization_id"], 1)
        self.assertGreater(len(data["definitions"]), 0)

        # 2. Add tenant-specific custom field
        new_field_payload = {
            "field_key": "patient_diet_preference",
            "field_label": "Dietary Preference & Restrictions",
            "field_type": "select",
            "options": ["Vegetarian", "Vegan", "Keto", "Diabetic Spec"],
            "is_required": False
        }
        res_create = self.client.post("/api/v1/custom-fields/definitions", json=new_field_payload, headers=headers)
        self.assertEqual(res_create.status_code, 201)
        created_json = res_create.get_json()
        self.assertEqual(created_json["custom_field"]["field_key"], "patient_diet_preference")

    def test_workflow_definition_and_transition_enforcement(self):
        """Validates workflow state machine and transition rule enforcement."""
        token = generate_access_token(1, "Doctor", extra_claims={"organization_id": "1", "role": "Doctor"})
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Fetch workflow definition
        res_wf = self.client.get("/api/v1/workflows/definitions", headers=headers)
        self.assertEqual(res_wf.status_code, 200)
        wf_data = res_wf.get_json()["workflow"]
        self.assertIn("statuses", wf_data)
        self.assertIn("transitions", wf_data)

        # 2. Setup record
        rec = IndustryRecord.query.filter_by(organization_id=1).first()
        self.assertIsNotNone(rec)
        rec.status = "Triage_Pending"
        rec_data = dict(rec.data or {})
        rec_data["triage_priority"] = "Urgent Level 2"
        rec.data = rec_data
        db.session.commit()

        # 3. Transition to In_Consultation
        trans_payload = {
            "target_status": "In_Consultation",
            "comment": "Doctor accepted patient into consultation room.",
            "additional_data": {"vitals_verified": True}
        }
        res_trans = self.client.post(f"/api/v1/workflows/records/{rec.id}/transition", json=trans_payload, headers=headers)
        self.assertEqual(res_trans.status_code, 200)
        trans_data = res_trans.get_json()
        self.assertEqual(trans_data["new_status"], "In_Consultation")

        # 4. Verify transition history
        res_hist = self.client.get(f"/api/v1/workflows/records/{rec.id}/history", headers=headers)
        self.assertEqual(res_hist.status_code, 200)
        hist_data = res_hist.get_json()
        self.assertGreater(len(hist_data["history"]), 0)
        self.assertEqual(hist_data["history"][0]["to_status"], "In_Consultation")

    def test_customer_self_service_portal_flow(self):
        """Validates customer passcode generation, verification, portal overview, document upload and digital response."""
        # Find or create a test customer
        cust = Customer.query.filter_by(organization_id=1).first()
        self.assertIsNotNone(cust)

        # 1. Request verification passcode
        res_req = self.client.post("/api/v1/portal/auth/request-code", json={
            "phone": cust.phone,
            "organization_id": 1
        })
        self.assertEqual(res_req.status_code, 200)
        req_data = res_req.get_json()
        token = req_data["session_token"]
        code = req_data["verification_code"]

        # 2. Verify code
        res_verify = self.client.post("/api/v1/portal/auth/verify", json={
            "session_token": token,
            "auth_code": code
        })
        self.assertEqual(res_verify.status_code, 200)
        self.assertEqual(res_verify.get_json()["status"], "authenticated")

        portal_headers = {"X-Portal-Token": token}

        # 3. Overview
        res_over = self.client.get("/api/v1/portal/overview", headers=portal_headers)
        self.assertEqual(res_over.status_code, 200)
        over_data = res_over.get_json()
        self.assertEqual(over_data["customer"]["id"], cust.id)
        self.assertIn("appointments", over_data)
        self.assertIn("industry_records", over_data)

        # 4. Document upload
        doc_payload = {
            "title": "Government ID Proof & Insurance Card",
            "file_name": "id_card_scan.pdf",
            "content": "TEST_PDF_MOCK_CONTENT_STREAM"
        }
        res_doc = self.client.post("/api/v1/portal/documents/upload", json=doc_payload, headers=portal_headers)
        self.assertEqual(res_doc.status_code, 201)
        self.assertEqual(res_doc.get_json()["status"], "Pending_Review")

        # 5. Digital approval on record
        rec = IndustryRecord.query.filter_by(organization_id=1).first()
        res_resp = self.client.post(f"/api/v1/portal/records/{rec.id}/respond", json={
            "decision": "APPROVED",
            "notes": "Patient verified and consented to care treatment plan."
        }, headers=portal_headers)
        self.assertEqual(res_resp.status_code, 200)

        # 6. Preferences
        res_pref = self.client.post("/api/v1/portal/preferences", json={"whatsapp": True, "email": True, "sms": False}, headers=portal_headers)
        self.assertEqual(res_pref.status_code, 200)

    def test_operational_analytics_and_xlsx_export(self):
        """Validates real-time operational KPIs and sanitized multi-tab XLSX report generation."""
        token = generate_access_token(1, "Organization", extra_claims={"organization_id": "1", "role": "Organization"})
        headers = {"Authorization": f"Bearer {token}"}

        # 1. JSON operational KPIs
        res_kpi = self.client.get("/api/v1/analytics/operational-kpis", headers=headers)
        self.assertEqual(res_kpi.status_code, 200)
        kpi_data = res_kpi.get_json()
        self.assertIn("sector_kpis", kpi_data)
        self.assertIn("funnel", kpi_data)
        self.assertIn("staff_productivity", kpi_data)

        # 2. XLSX Export
        res_xlsx = self.client.get("/api/v1/analytics/export?format=xlsx", headers=headers)
        self.assertEqual(res_xlsx.status_code, 200)
        self.assertEqual(res_xlsx.content_type, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        self.assertIn("analytics_report_1.xlsx", res_xlsx.headers.get("Content-Disposition", ""))

        import openpyxl
        wb = openpyxl.load_workbook(io.BytesIO(res_xlsx.get_data()))
        self.assertIn("Executive KPIs", wb.sheetnames)
        self.assertIn("Staff Productivity", wb.sheetnames)

    def test_advanced_automation_rules(self):
        """Validates listing automation rules and safe trigger execution."""
        token = generate_access_token(1, "Organization", extra_claims={"organization_id": "1", "role": "Organization"})
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Fetch rules (auto-seeds defaults)
        res_rules = self.client.get("/api/v1/automations/rules", headers=headers)
        self.assertEqual(res_rules.status_code, 200)
        rules = res_rules.get_json()
        self.assertGreater(len(rules), 0)

        # 2. Trigger test execution
        first_rule_id = rules[0]["id"]
        res_trig = self.client.post(f"/api/v1/automations/rules/{first_rule_id}/trigger", headers=headers)
        self.assertEqual(res_trig.status_code, 200)
        self.assertEqual(res_trig.get_json()["rule_id"], first_rule_id)

    def test_client_portal_self_service_booking_and_management(self):
        """Validates customer self-service appointment booking, rescheduling, and cancellation."""
        cust = Customer.query.filter_by(organization_id=1).first()
        self.assertIsNotNone(cust)

        # Login to portal
        res_req = self.client.post("/api/v1/portal/auth/request-code", json={"phone": cust.phone, "organization_id": 1})
        sess_token = res_req.get_json()["session_token"]
        auth_code = res_req.get_json()["verification_code"]
        self.client.post("/api/v1/portal/auth/verify", json={"session_token": sess_token, "auth_code": auth_code})
        portal_headers = {"X-Portal-Token": sess_token}

        # 1. Get Services
        res_svc = self.client.get("/api/v1/portal/services", headers=portal_headers)
        self.assertEqual(res_svc.status_code, 200)
        services = res_svc.get_json()["services"]
        self.assertGreater(len(services), 0)

        # 2. Book appointment
        book_payload = {
            "service_name": services[0]["name"],
            "appointment_date": "2026-12-15T10:30:00",
            "staff_name": "Dr. Sarah",
            "notes": "Routine checkup self-booked via portal"
        }
        res_book = self.client.post("/api/v1/portal/appointments/book", json=book_payload, headers=portal_headers)
        self.assertEqual(res_book.status_code, 201)
        appt_id = res_book.get_json()["appointment_id"]

        # 3. Reschedule appointment
        res_resched = self.client.post(f"/api/v1/portal/appointments/{appt_id}/reschedule", json={
            "appointment_date": "2026-12-16T14:00:00"
        }, headers=portal_headers)
        self.assertEqual(res_resched.status_code, 200)

        # 4. Cancel appointment
        res_cancel = self.client.post(f"/api/v1/portal/appointments/{appt_id}/cancel", json={
            "reason": "Client schedule conflict"
        }, headers=portal_headers)
        self.assertEqual(res_cancel.status_code, 200)
        self.assertEqual(res_cancel.get_json()["status"], "Cancelled")

    def test_nine_industry_competitive_feature_packs(self):
        """Validates specialized endpoints across all nine industry packs."""
        token = generate_access_token(1, "Organization", extra_claims={"organization_id": "1", "role": "Organization"})
        headers = {"Authorization": f"Bearer {token}"}
        cust = Customer.query.filter_by(organization_id=1).first()
        rec = IndustryRecord.query.filter_by(organization_id=1).first()

        # 1. Healthcare: Timeline & FHIR R4 Bundle
        res_tl = self.client.get(f"/api/v1/industry-suite/healthcare/patient/{cust.id}/timeline", headers=headers)
        self.assertEqual(res_tl.status_code, 200)
        self.assertIn("timeline_events", res_tl.get_json())

        res_fhir = self.client.get(f"/api/v1/industry-suite/healthcare/patient/{cust.id}/fhir-bundle", headers=headers)
        self.assertEqual(res_fhir.status_code, 200)
        self.assertEqual(res_fhir.get_json()["resourceType"], "Bundle")

        res_tmpl = self.client.get("/api/v1/industry-suite/healthcare/clinical-templates", headers=headers)
        self.assertEqual(res_tmpl.status_code, 200)
        self.assertGreater(len(res_tmpl.get_json()["templates"]), 0)

        # 2. Salon & Wellness: Membership & Consumables
        res_mem = self.client.post("/api/v1/industry-suite/salon/memberships/enroll", json={
            "customer_id": cust.id, "tier": "Gold", "fee_paid": 3000
        }, headers=headers)
        self.assertEqual(res_mem.status_code, 201)

        res_loy = self.client.get(f"/api/v1/industry-suite/salon/customers/{cust.id}/loyalty", headers=headers)
        self.assertEqual(res_loy.status_code, 200)
        self.assertTrue(res_loy.get_json()["has_membership"])

        res_cons = self.client.post(f"/api/v1/industry-suite/salon/records/{rec.id}/log-consumables", json={
            "items": [{"product": "Argan Serum", "units": 15, "cost": 150}]
        }, headers=headers)
        self.assertEqual(res_cons.status_code, 200)

        # 3. Finance: Risk Profile & Compliance
        res_risk = self.client.post("/api/v1/industry-suite/finance/evaluate-risk-profile", json={
            "time_horizon_years": 8, "loss_reaction": "BUY_MORE", "investment_goal": "GROWTH"
        }, headers=headers)
        self.assertEqual(res_risk.status_code, 200)
        self.assertIn("model_asset_allocation", res_risk.get_json())

        res_comp = self.client.post(f"/api/v1/industry-suite/finance/records/{rec.id}/compliance-checklist", json={
            "kyc_id_verified": True, "aml_pep_screened": True
        }, headers=headers)
        self.assertEqual(res_comp.status_code, 200)

        # 4. Insurance: Quote Comparison & Renewals
        res_quotes = self.client.post("/api/v1/industry-suite/insurance/compare-quotes", json={
            "age": 32, "sum_assured": 1500000
        }, headers=headers)
        self.assertEqual(res_quotes.status_code, 200)
        self.assertEqual(len(res_quotes.get_json()["quotes"]), 3)

        res_ren = self.client.get("/api/v1/industry-suite/insurance/renewals-upcoming?days=60", headers=headers)
        self.assertEqual(res_ren.status_code, 200)

        # 5. Retail: Catalog & Stock Movement
        res_cat = self.client.get("/api/v1/industry-suite/retail/catalog", headers=headers)
        self.assertEqual(res_cat.status_code, 200)
        self.assertGreater(len(res_cat.get_json()["catalog"]), 0)

        res_stock = self.client.post("/api/v1/industry-suite/retail/stock-movement", json={
            "sku": "HC-BLAZER-01", "quantity": 5, "movement_type": "RESTOCK"
        }, headers=headers)
        self.assertEqual(res_stock.status_code, 200)

        # 6. Education: University Comparison & Visa Checklist
        res_uni = self.client.post("/api/v1/industry-suite/education/compare-universities", json={}, headers=headers)
        self.assertEqual(res_uni.status_code, 200)
        self.assertEqual(len(res_uni.get_json()["comparison"]), 3)

        res_visa = self.client.post(f"/api/v1/industry-suite/education/records/{rec.id}/visa-checklist", json={
            "cas_or_i20_received": True, "bank_financial_affidavit": True
        }, headers=headers)
        self.assertEqual(res_visa.status_code, 200)

        # 7. Legal: Conflict Review & Retainer Statement
        res_conf = self.client.post("/api/v1/industry-suite/legal/conflict-review", json={
            "adverse_party": "Omega Industries", "matter_title": "Arbitration"
        }, headers=headers)
        self.assertEqual(res_conf.status_code, 200)
        self.assertIn("clearance_status", res_conf.get_json())

        res_ret = self.client.get(f"/api/v1/industry-suite/legal/records/{rec.id}/retainer-statement", headers=headers)
        self.assertEqual(res_ret.status_code, 200)

        # 8. Real Estate: Properties & Commission Split
        res_prop = self.client.get("/api/v1/industry-suite/real-estate/properties", headers=headers)
        self.assertEqual(res_prop.status_code, 200)

        res_comm = self.client.post(f"/api/v1/industry-suite/real-estate/deals/{rec.id}/calculate-commission", json={
            "sale_price": 20000000, "commission_rate_pct": 2.5
        }, headers=headers)
        self.assertEqual(res_comm.status_code, 200)

        # 9. Professional Services: Resource Utilization & SLA Escalation
        res_res = self.client.get("/api/v1/industry-suite/professional-services/resource-utilization", headers=headers)
        self.assertEqual(res_res.status_code, 200)

        res_sla = self.client.post(f"/api/v1/industry-suite/professional-services/records/{rec.id}/sla-escalation", json={
            "severity": "P1 - Critical", "incident_summary": "System outage"
        }, headers=headers)
        self.assertEqual(res_sla.status_code, 200)

        # 10. Platform Integrations Status
        res_integ = self.client.get("/api/v1/industry-suite/platform/integrations/status", headers=headers)
        self.assertEqual(res_integ.status_code, 200)
        self.assertIn("integrations", res_integ.get_json())


if __name__ == "__main__":
    unittest.main()

