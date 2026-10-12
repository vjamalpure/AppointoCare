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


if __name__ == "__main__":
    unittest.main()
