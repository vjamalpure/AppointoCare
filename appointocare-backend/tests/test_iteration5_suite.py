import unittest
from datetime import datetime, timedelta
from app import create_app, db
from app.models import (
    Organization, User, Customer, Appointment, TaskItem, BusinessPipeline,
    CustomerDocument, DocumentVersion, ApprovalRecord, ClinicalEncounter,
    AppointmentWaitlist, ResourceRoomSchedule, DiagnosticLabOrder, ABDMConsentArtifact
)
from flask_jwt_extended import create_access_token


class TestIteration5Suite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config["TESTING"] = True
        cls.client = cls.app.test_client()

    def setUp(self):
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Retrieve test organization
        self.org = Organization.query.first()
        if not self.org:
            self.org = Organization(
                name="Test Iteration5 Health & Enterprise",
                code="TITER5",
                sector="Healthcare",
                username="test_iter5_admin",
                password="password123"
            )
            db.session.add(self.org)
            db.session.commit()

        # Admin token
        self.admin_token = create_access_token(
            identity="1",
            additional_claims={"role": "Admin", "organization_id": self.org.id}
        )
        self.admin_headers = {
            "Authorization": f"Bearer {self.admin_token}",
            "Content-Type": "application/json"
        }

        # Doctor token
        self.doctor_token = create_access_token(
            identity="2",
            additional_claims={"role": "Doctor", "organization_id": self.org.id, "sub": "Dr. Sarah Jenkins"}
        )
        self.doctor_headers = {
            "Authorization": f"Bearer {self.doctor_token}",
            "Content-Type": "application/json"
        }

        # Staff token
        self.staff_token = create_access_token(
            identity="3",
            additional_claims={"role": "Staff", "organization_id": self.org.id, "sub": "Staff Member"}
        )
        self.staff_headers = {
            "Authorization": f"Bearer {self.staff_token}",
            "Content-Type": "application/json"
        }

        # Test customer
        self.customer = Customer.query.filter_by(organization_id=self.org.id).first()
        if not self.customer:
            self.customer = Customer(
                organization_id=self.org.id,
                name="Priya Patel",
                phone="9876543210",
                email="priya.patel@example.com",
                gender="Female"
            )
            db.session.add(self.customer)
            db.session.commit()

    def tearDown(self):
        self.app_context.pop()

    def test_01_task_management_lifecycle_and_escalation(self):
        """Test task creation, summary, overdue detection, and escalation."""
        # Create task
        res = self.client.post("/api/v1/tasks", json={
            "title": "Review High Risk Diabetic Patient Chart",
            "priority": "High",
            "assigned_to_name": "Dr. Sarah Jenkins",
            "customer_id": self.customer.id,
            "due_date": (datetime.utcnow() + timedelta(days=1)).isoformat()
        }, headers=self.staff_headers)
        self.assertEqual(res.status_code, 201)
        task_id = res.json["task"]["id"]

        # Escalate task
        esc_res = self.client.post(f"/api/v1/tasks/{task_id}/escalate", headers=self.staff_headers)
        self.assertEqual(esc_res.status_code, 200)
        self.assertEqual(esc_res.json["priority"], "Urgent")
        self.assertEqual(esc_res.json["escalation_level"], 1)

        # Get summary
        sum_res = self.client.get("/api/v1/tasks/summary", headers=self.staff_headers)
        self.assertEqual(sum_res.status_code, 200)
        self.assertGreaterEqual(sum_res.json["total"], 1)

    def test_02_business_pipelines_and_deal_transitions(self):
        """Test multi-stage business pipelines, deal creation, and stage progression."""
        # Get sector pipeline (with auto-seeding)
        res = self.client.get("/api/v1/pipelines?sector=Healthcare", headers=self.staff_headers)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(len(res.json) > 0)
        pipe_id = res.json[0]["id"]
        stage_ids = [s["id"] for s in res.json[0]["stages"]]

        # Add deal
        deal_res = self.client.post(f"/api/v1/pipelines/{pipe_id}/deals", json={
            "title": "Annual Executive Health Package for Corporate Group",
            "value": 125000,
            "customer_id": self.customer.id,
            "stage_id": stage_ids[0]
        }, headers=self.staff_headers)
        self.assertEqual(deal_res.status_code, 201)
        deal_id = deal_res.json["deal"]["id"]

        # Move deal to next stage
        move_res = self.client.put(f"/api/v1/pipelines/{pipe_id}/deals/{deal_id}/move", json={
            "stage_id": stage_ids[1]
        }, headers=self.staff_headers)
        self.assertEqual(move_res.status_code, 200)
        self.assertEqual(move_res.json["deal"]["stage_id"], stage_ids[1])

    def test_03_document_versioning_and_electronic_signoffs(self):
        """Test document versioning, download auditing, and electronic signature acknowledgement."""
        # Create base doc
        doc = CustomerDocument(
            organization_id=self.org.id,
            customer_id=self.customer.id,
            title="Cardiac Surgery Consent & Estimate",
            file_name="consent_v1.pdf",
            uploaded_by="Staff"
        )
        db.session.add(doc)
        db.session.commit()

        # Add version 2
        ver_res = self.client.post(f"/api/v1/documents/{doc.id}/versions", json={
            "file_name": "consent_v2_amended.pdf",
            "file_size": 24500,
            "change_notes": "Updated anaesthesia risk disclosures",
            "access_level": "Customer_Facing"
        }, headers=self.staff_headers)
        self.assertEqual(ver_res.status_code, 201)
        self.assertEqual(ver_res.json["version"]["version_number"], 1)

        # Audit download
        dl_res = self.client.post(f"/api/v1/documents/{doc.id}/audit-download", json={}, headers=self.staff_headers)
        self.assertEqual(dl_res.status_code, 200)

        # Electronic signoff
        sig_res = self.client.post("/api/v1/documents/approvals", json={
            "entity_type": "treatment_plan",
            "entity_id": doc.id,
            "signee_name": "Priya Patel",
            "notes": "Patient acknowledged informed consent in clinic"
        }, headers=self.staff_headers)
        self.assertEqual(sig_res.status_code, 201)
        self.assertTrue(sig_res.json["approval"]["signature_hash"].startswith("SIG-"))

    def test_04_healthcare_clinical_encounter_full_journey(self):
        """Test clinical documentation, vitals, structured SOAP notes, and doctor sign-off."""
        # Create clinical encounter
        enc_res = self.client.post("/api/v1/healthcare/encounters", json={
            "patient_id": self.customer.id,
            "encounter_type": "Outpatient Consultation",
            "practitioner_name": "Dr. Sarah Jenkins",
            "practitioner_reg_no": "MCI-2018-9410",
            "chief_complaints": "Exertional dyspnea and episodic palpitation for 2 weeks",
            "vitals": {
                "bp_systolic": 138,
                "bp_diastolic": 88,
                "pulse": 84,
                "temp_f": 98.4,
                "spo2": 98,
                "weight_kg": 64,
                "bmi": 24.2
            },
            "allergies": [{"allergen": "Sulfa drugs", "severity": "Moderate"}],
            "medication_history": [{"name": "Amlodipine 5mg", "duration": "6 months"}],
            "clinical_notes": "S: Patient reports intermittent chest tightness on brisk walking.\nO: S1 S2 heard, no murmurs. Chest clear.\nA: Grade 1 Essential Hypertension with mild exertional angina.\nP: Start Telmisartan 40mg once daily. Order 2D-Echocardiogram and Lipid Profile.",
            "diagnosis": [{"code": "ICD-10 I10", "description": "Essential (primary) hypertension"}],
            "treatment_plan": "Daily blood pressure log, low sodium diet, repeat review in 7 days."
        }, headers=self.doctor_headers)
        self.assertEqual(enc_res.status_code, 201)
        encounter_id = enc_res.json["encounter"]["id"]

        # Doctor signs off and freezes record
        sign_res = self.client.post(f"/api/v1/healthcare/encounters/{encounter_id}/sign-off", json={
            "practitioner_reg_no": "MCI-2018-9410"
        }, headers=self.doctor_headers)
        self.assertEqual(sign_res.status_code, 200)
        self.assertEqual(sign_res.json["status"], "Signed_Off")

        # Longitudinal patient history
        long_res = self.client.get(f"/api/v1/healthcare/encounters/patient/{self.customer.id}", headers=self.doctor_headers)
        self.assertEqual(long_res.status_code, 200)
        self.assertGreaterEqual(len(long_res.json), 1)

    def test_05_healthcare_waitlist_and_room_collision_prevention(self):
        """Test patient waitlist management, appointment promotion, and room resource conflict checking."""
        # Add to waitlist with Urgent priority
        wait_res = self.client.post("/api/v1/healthcare/waitlist", json={
            "customer_name": "Rohan Gupta",
            "customer_phone": "9811122233",
            "urgency": "Urgent",
            "preferred_practitioner": "Dr. Sarah Jenkins",
            "notes": "Post-operative suture removal requested on earlier cancellation"
        }, headers=self.staff_headers)
        self.assertEqual(wait_res.status_code, 201)
        wait_id = wait_res.json["waitlist"]["id"]

        # Promote waitlist entry to appointment
        prom_res = self.client.post(f"/api/v1/healthcare/waitlist/{wait_id}/promote", json={}, headers=self.staff_headers)
        self.assertEqual(prom_res.status_code, 201)
        self.assertEqual(prom_res.json["appointment"]["status"], "Booked")

        # Room reservation with unique test resource name
        room_name = f"Suite-T5-{int(datetime.utcnow().timestamp())}"
        t_start = datetime.utcnow() + timedelta(days=2, hours=10)
        t_end = t_start + timedelta(minutes=45)
        res_res = self.client.post("/api/v1/healthcare/resources/schedule", json={
            "resource_name": room_name,
            "start_time": t_start.isoformat(),
            "end_time": t_end.isoformat(),
            "assigned_practitioner": "Dr. Sarah Jenkins"
        }, headers=self.staff_headers)
        self.assertEqual(res_res.status_code, 201)

        # Attempt collision booking in same room and slot
        collision_res = self.client.post("/api/v1/healthcare/resources/schedule", json={
            "resource_name": room_name,
            "start_time": (t_start + timedelta(minutes=15)).isoformat(),
            "end_time": (t_end + timedelta(minutes=15)).isoformat(),
            "assigned_practitioner": "Dr. Another Doctor"
        }, headers=self.staff_headers)
        self.assertEqual(collision_res.status_code, 409)

    def test_06_healthcare_lab_orders_and_clinic_operational_dashboard(self):
        """Test diagnostic lab order creation, physician review, and clinic dashboard KPIs."""
        # Create lab order
        lab_res = self.client.post("/api/v1/healthcare/lab-orders", json={
            "customer_id": self.customer.id,
            "test_name": "Comprehensive Lipid & Renal Panel",
            "category": "Biochemistry",
            "ordering_doctor": "Dr. Sarah Jenkins"
        }, headers=self.doctor_headers)
        self.assertEqual(lab_res.status_code, 201)
        order_id = lab_res.json["order"]["id"]

        # Review lab results
        rev_res = self.client.put(f"/api/v1/healthcare/lab-orders/{order_id}/review", json={
            "doctor_review_notes": "Serum Creatinine 0.9 mg/dL (Normal). Lipid profile: Total Cholesterol 185 mg/dL."
        }, headers=self.doctor_headers)
        self.assertEqual(rev_res.status_code, 200)
        self.assertEqual(rev_res.json["order"]["status"], "Reviewed_By_Doctor")

        # Clinic operational dashboard
        dash_res = self.client.get("/api/v1/healthcare/operational-dashboard", headers=self.doctor_headers)
        self.assertEqual(dash_res.status_code, 200)
        self.assertIn("clinic_metrics", dash_res.json)
        self.assertIn("average_patient_wait_time_minutes", dash_res.json["clinic_metrics"])

    def test_07_customer_unified_timeline_and_safe_import_validation(self):
        """Test Customer 360 timeline aggregation and CSV import validation with duplicate detection."""
        # 360 Timeline
        time_res = self.client.get(f"/api/v1/customers/{self.customer.id}/unified-timeline", headers=self.staff_headers)
        self.assertEqual(time_res.status_code, 200)
        self.assertIn("events", time_res.json)
        self.assertGreaterEqual(time_res.json["total_events"], 1)

        # Batch import validation with dynamic unique phones
        p1 = f"71{int(datetime.utcnow().timestamp()) % 100000000:08d}"
        p2 = f"72{int(datetime.utcnow().timestamp()) % 100000000:08d}"
        val_res = self.client.post("/api/v1/customers/import-validate", json={
            "rows": [
                {"name": "Valid Client 1", "phone": p1, "email": f"{p1}@example.com"},
                {"name": "Valid Client 2", "phone": p2, "email": f"{p2}@example.com"},
                {"name": "Duplicate Client", "phone": self.customer.phone, "email": self.customer.email},  # Duplicate
                {"name": "", "phone": "123"}  # Error
            ]
        }, headers=self.staff_headers)
        self.assertEqual(val_res.status_code, 200)
        summary = val_res.json["summary"]
        self.assertEqual(summary["valid_count"], 2)
        self.assertEqual(summary["duplicate_count"], 1)
        self.assertEqual(summary["error_count"], 1)

    def test_08_eight_industry_domain_deepening(self):
        """Test vertical deepening across Salon, Finance, Insurance, Retail, and Professional Services."""
        # Salon membership renewal
        s_res = self.client.post("/api/v1/industry-suite/salon/memberships/MEM-VIP-99/renew", json={
            "renewal_months": 12, "fee_amount": 14999.0
        }, headers=self.staff_headers)
        self.assertEqual(s_res.status_code, 200)
        self.assertEqual(s_res.json["renewal_status"], "ACTIVE_RENEWED")

        # Finance suitability review
        f_res = self.client.post("/api/v1/industry-suite/finance/suitability-review", json={
            "customer_id": self.customer.id, "risk_score": 78
        }, headers=self.staff_headers)
        self.assertEqual(f_res.status_code, 200)
        self.assertIn("approved_asset_mix", f_res.json)

        # Insurance quote-to-policy conversion
        i_res = self.client.post("/api/v1/industry-suite/insurance/quote-to-policy", json={
            "quote_id": "Q-CARE-99", "carrier": "Care Health Insurance", "annual_premium": 28000.0
        }, headers=self.staff_headers)
        self.assertEqual(i_res.status_code, 201)
        self.assertEqual(i_res.json["status"], "BOUND_AND_ISSUED")

        # Retail sales order
        r_res = self.client.post("/api/v1/industry-suite/retail/orders", json={
            "customer_name": "VIP Client",
            "items": [{"sku": "AURA-BLAZER-40", "name": "Bespoke Cashmere Blazer", "qty": 1, "unit_price": 45000.0}]
        }, headers=self.staff_headers)
        self.assertEqual(r_res.status_code, 201)
        self.assertIn("order_number", r_res.json)

        # Professional services timesheet
        p_res = self.client.post("/api/v1/industry-suite/prof-services/timesheets/submit", json={
            "project_code": "PRJ-CLOUD-ENTERPRISE", "total_hours": 42.0, "billable_hours": 40.0
        }, headers=self.staff_headers)
        self.assertEqual(p_res.status_code, 201)
        self.assertEqual(p_res.json["status"], "SUBMITTED_FOR_APPROVAL")


if __name__ == "__main__":
    unittest.main()
