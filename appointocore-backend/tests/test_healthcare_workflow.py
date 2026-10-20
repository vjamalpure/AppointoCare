import json
import os
import unittest
from datetime import datetime, timedelta

_IS_LOCAL_SQLITE = False
if "DATABASE_URL" not in os.environ:
    os.environ["DATABASE_URL"] = "sqlite:///healthcare-test.db"
    _IS_LOCAL_SQLITE = True
if "SECRET_KEY" not in os.environ:
    os.environ["SECRET_KEY"] = "test-secret-at-least-32-characters-long"
if "JWT_SECRET_KEY" not in os.environ:
    os.environ["JWT_SECRET_KEY"] = "test-jwt-secret-at-least-32-chars-long"

from app import create_app, db
from app.models import Organization, User, Appointment, Customer, Patient, IndustryRecord, AppointmentTransaction, AuditLog
from flask_jwt_extended import create_access_token


class HealthcareWorkflowTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config.update(TESTING=True)

    def setUp(self):
        self.client = self.app.test_client()
        with self.app.app_context():
            if _IS_LOCAL_SQLITE:
                db.create_all()

            # Ensure Org 1 (Healthcare) exists
            self.org1 = Organization.query.get(1)
            if not self.org1:
                self.org1 = Organization(id=1, name="City Care Health & Dental", code="CCHD", sector="Healthcare", username="org1", password="pbkdf2:sha256:dummy")
                db.session.add(self.org1)
                db.session.commit()

            # Ensure Org 2 (Salon) exists for cross-tenant tests
            self.org2 = Organization.query.get(2)
            if not self.org2:
                self.org2 = Organization(id=2, name="Apex Aesthetics", code="AAWS", sector="Salon", username="org2", password="pbkdf2:sha256:dummy")
                db.session.add(self.org2)
                db.session.commit()

            self.org1_token = create_access_token(
                identity="1",
                additional_claims={"organization_id": 1, "role": "Organization", "username": "org1"}
            )
            self.org2_token = create_access_token(
                identity="2",
                additional_claims={"organization_id": 2, "role": "Organization", "username": "org2"}
            )
            self.doc_token = create_access_token(
                identity="101",
                additional_claims={"organization_id": 1, "role": "Doctor", "username": "doc_sarah"}
            )

    def tearDown(self):
        if _IS_LOCAL_SQLITE:
            with self.app.app_context():
                db.drop_all()

    # 1. Patient Registration & Search
    def test_patient_registration_search_and_duplicate_prevention(self):
        import uuid
        headers = {"Authorization": f"Bearer {self.org1_token}", "Content-Type": "application/json"}
        phone = f"99{uuid.uuid4().int % 100000000:08d}"
        unique_name = f"Aarav-{uuid.uuid4().hex[:4]}"

        # Register patient
        reg_payload = {
            "name": unique_name,
            "phone": phone,
            "email": f"{unique_name.lower()}@example.com",
            "gender": "Male",
            "address": "42 MG Road, Bengaluru",
            "check_duplicate": True
        }
        res = self.client.post("/api/v1/customers", json=reg_payload, headers=headers)
        self.assertEqual(res.status_code, 201)
        cust_id = res.json.get("customer_id")
        self.assertTrue(cust_id)

        # Duplicate detection check
        dup_res = self.client.post("/api/v1/customers", json=reg_payload, headers=headers)
        self.assertEqual(dup_res.status_code, 409)
        self.assertIn("already registered", dup_res.json.get("msg", ""))

        # Search by query
        search_res = self.client.get(f"/api/v1/customers?q={unique_name}", headers=headers)
        self.assertEqual(search_res.status_code, 200)
        found = [c for c in search_res.json if c["phone"] == phone]
        self.assertTrue(len(found) > 0)

        # Cleanup
        self.client.delete(f"/api/v1/customers/{cust_id}", headers=headers)

    # 2. Enriched Customer Timeline (includes clinical records & billing)
    def test_patient_timeline_enrichment(self):
        headers = {"Authorization": f"Bearer {self.org1_token}", "Content-Type": "application/json"}
        with self.app.app_context():
            cust = Customer.query.filter_by(organization_id=1).first()
            if not cust:
                cust = Customer(organization_id=1, name="Timeline Patient", phone="9112233445")
                db.session.add(cust)
                db.session.commit()
            cust_id = cust.id

        res = self.client.get(f"/api/v1/customers/{cust_id}/timeline", headers=headers)
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertIn("timeline", data)
        self.assertIn("total_clinical_records", data)
        self.assertIn("total_transactions", data)

    # 3. Doctor Booking Conflict Prevention
    def test_appointment_booking_conflict_prevention(self):
        headers = {"Authorization": f"Bearer {self.org1_token}", "Content-Type": "application/json"}
        target_date = (datetime.utcnow() + timedelta(days=2)).replace(minute=0, second=0, microsecond=0).isoformat()

        # First booking for Dr. Sarah
        payload1 = {
            "customer_name": "Patient Alpha",
            "customer_phone": "9876500001",
            "appointment_date": target_date,
            "staff_name": "doc_sarah",
            "service_name": "Cardiology Consultation",
            "check_conflict": True
        }
        res1 = self.client.post("/appointments", json=payload1, headers=headers)
        self.assertIn(res1.status_code, [200, 201])
        appt1_id = res1.json.get("appointment_id") or res1.json.get("id")

        # Conflicting booking within same slot for Dr. Sarah
        payload2 = {
            "customer_name": "Patient Beta",
            "customer_phone": "9876500002",
            "appointment_date": target_date,
            "staff_name": "doc_sarah",
            "service_name": "Cardiology Followup",
            "check_conflict": True
        }
        res2 = self.client.post("/appointments", json=payload2, headers=headers)
        self.assertEqual(res2.status_code, 409)
        self.assertIn("already has a booking", res2.json.get("msg", ""))

        # Clean up test appointment
        if appt1_id:
            self.client.delete(f"/appointments/{appt1_id}", headers=headers)

    # 4. Appointment Lifecycle (Check-in, Reschedule, Cancel, Status Validation)
    def test_appointment_lifecycle_transitions(self):
        headers = {"Authorization": f"Bearer {self.org1_token}", "Content-Type": "application/json"}
        tomorrow = (datetime.utcnow() + timedelta(days=1)).isoformat()
        res = self.client.post("/appointments", json={
            "customer_name": "Lifecycle Patient",
            "customer_phone": "9876500003",
            "appointment_date": tomorrow,
            "status": "Booked"
        }, headers=headers)
        self.assertIn(res.status_code, [200, 201])
        appt_id = res.json.get("appointment_id") or res.json.get("id")

        # 1. Check-in
        checkin_res = self.client.post(f"/appointments/{appt_id}/check-in", headers=headers)
        self.assertEqual(checkin_res.status_code, 200)
        self.assertEqual(checkin_res.json.get("status"), "Checked-In")

        # 2. Reschedule
        new_date = (datetime.utcnow() + timedelta(days=3)).isoformat()
        resched_res = self.client.post(f"/appointments/{appt_id}/reschedule", json={"appointment_date": new_date}, headers=headers)
        self.assertEqual(resched_res.status_code, 200)
        self.assertEqual(resched_res.json.get("status"), "Booked")

        # 3. Invalid status validation
        invalid_res = self.client.patch(f"/appointments/{appt_id}", json={"status": "NonExistentStatus"}, headers=headers)
        self.assertEqual(invalid_res.status_code, 400)

        # 4. Cancel
        cancel_res = self.client.post(f"/appointments/{appt_id}/cancel", json={"reason": "Patient requested reschedule"}, headers=headers)
        self.assertEqual(cancel_res.status_code, 200)
        self.assertEqual(cancel_res.json.get("status"), "Cancelled")

        # Cleanup
        self.client.delete(f"/appointments/{appt_id}", headers=headers)

    # 5. OPD Queue: Token Generation, Idempotency & State Machine
    def test_opd_queue_lifecycle_and_transition_guards(self):
        headers = {"Authorization": f"Bearer {self.org1_token}", "Content-Type": "application/json"}

        # Create OPD token for Healthcare
        res = self.client.post("/api/v1/industry-suite/queue/create", json={
            "client_name": "Rohan Verma",
            "service": "General OPD",
            "priority": "High"
        }, headers=headers)
        self.assertEqual(res.status_code, 201)
        token_id = res.json.get("id")
        token_no = res.json.get("token_number")
        self.assertTrue(token_no.startswith("OPD-"))
        self.assertEqual(res.json.get("status"), "Waiting")

        # Valid transition: Waiting -> Called
        call_res = self.client.post("/api/v1/industry-suite/queue/advance", json={"record_id": token_id, "status": "Called"}, headers=headers)
        self.assertEqual(call_res.status_code, 200)
        self.assertEqual(call_res.json.get("status"), "Called")

        # Valid transition: Called -> In Consultation
        consult_res = self.client.post("/api/v1/industry-suite/queue/advance", json={"record_id": token_id, "status": "In Consultation"}, headers=headers)
        self.assertEqual(consult_res.status_code, 200)
        self.assertEqual(consult_res.json.get("status"), "In Consultation")

        # Invalid transition: In Consultation -> Waiting (rejected by state machine)
        invalid_res = self.client.post("/api/v1/industry-suite/queue/advance", json={"record_id": token_id, "status": "Skipped"}, headers=headers)
        self.assertEqual(invalid_res.status_code, 400)

        # Valid transition: In Consultation -> Completed
        done_res = self.client.post("/api/v1/industry-suite/queue/advance", json={"record_id": token_id, "status": "Completed"}, headers=headers)
        self.assertEqual(done_res.status_code, 200)
        self.assertEqual(done_res.json.get("status"), "Completed")

        # Cleanup
        self.client.delete(f"/api/v1/industry-suite/queue/{token_id}", headers=headers)

    # 6. Privacy-Safe Public Waiting Queue Display
    def test_privacy_safe_public_queue_display(self):
        # Create an active token first
        headers = {"Authorization": f"Bearer {self.org1_token}", "Content-Type": "application/json"}
        create_res = self.client.post("/api/v1/industry-suite/queue/create", json={
            "client_name": "Devendra Mukherjee",
            "phone": "9876543210",
            "notes": "Severe hypertension and chest tightness"
        }, headers=headers)
        self.assertEqual(create_res.status_code, 201)
        token_id = create_res.json.get("id")

        # Public display requires NO auth token
        pub_res = self.client.get("/api/v1/industry-suite/queue/public-display?organization_id=1")
        self.assertEqual(pub_res.status_code, 200)
        data = pub_res.json
        self.assertIn("tokens", data)
        self.assertIn("refresh_seconds", data)

        # Ensure NO sensitive PHI or phone numbers are exposed
        pub_str = json.dumps(data)
        self.assertNotIn("9876543210", pub_str)
        self.assertNotIn("hypertension", pub_str.lower())
        self.assertNotIn("chest tightness", pub_str.lower())

        # Check name masking (initials only)
        tokens = data.get("tokens", [])
        dev_tokens = [t for t in tokens if t.get("patient_initials") == "D. M."]
        self.assertTrue(len(dev_tokens) > 0)

        # Cleanup
        self.client.delete(f"/api/v1/industry-suite/queue/{token_id}", headers=headers)

    # 7. Clinical Vitals Evaluation (Non-diagnostic advisory threshold check)
    def test_clinical_vitals_evaluation(self):
        from app.routes.industry_suite import evaluate_abnormal_vitals
        vitals = {
            "bp_systolic": 155,
            "bp_diastolic": 98,
            "pulse": 112,
            "spo2": 92,
            "temperature": 101.8
        }
        advisories = evaluate_abnormal_vitals(vitals)
        self.assertEqual(len(advisories), 5)
        # Verify non-diagnostic advisory wording
        for adv in advisories:
            self.assertIn("notice", adv)
            self.assertIn("threshold", adv)
            self.assertTrue("practitioner" in adv["notice"].lower() or "clinical" in adv["notice"].lower() or "baseline" in adv["notice"].lower())

    # 8. Prescription Creation & Amendment History
    def test_prescription_amendment_history_and_audit(self):
        headers = {"Authorization": f"Bearer {self.doc_token}", "Content-Type": "application/json"}
        create_res = self.client.post("/api/v1/industry-suite/records", json={
            "title": "Dr. Sarah Rx - Test Regimen",
            "record_type": "prescription",
            "data": {
                "diagnosis": "Bacterial Tonsillitis",
                "medications": [
                    {"medicine_name": "Azithromycin 500mg", "dosage": "OD", "duration": "3 days"}
                ]
            }
        }, headers=headers)
        self.assertEqual(create_res.status_code, 201)
        rec_id = create_res.json.get("id")

        # Amend prescription
        amend_res = self.client.put(f"/api/v1/industry-suite/records/{rec_id}", json={
            "amendment_reason": "Patient allergic reaction, switched to Cefixime",
            "data": {
                "diagnosis": "Bacterial Tonsillitis",
                "medications": [
                    {"medicine_name": "Cefixime 200mg", "dosage": "BD", "duration": "5 days"}
                ]
            }
        }, headers=headers)
        self.assertEqual(amend_res.status_code, 200)

        # Verify revision history stored in record data
        with self.app.app_context():
            rec = IndustryRecord.query.get(rec_id)
            revisions = (rec.data or {}).get("revisions", [])
            self.assertEqual(len(revisions), 1)
            self.assertIn("switched to Cefixime", revisions[0]["reason"])
            self.assertEqual(revisions[0]["previous_medications"][0]["medicine_name"], "Azithromycin 500mg")

        # Cleanup
        self.client.delete(f"/api/v1/industry-suite/records/{rec_id}", headers=headers)

    # 9. Consultation Billing & Refund Reconciliation
    def test_consultation_billing_and_refund(self):
        headers = {"Authorization": f"Bearer {self.org1_token}", "Content-Type": "application/json"}
        # Create appointment
        appt_res = self.client.post("/appointments", json={
            "customer_name": "Billing Patient",
            "customer_phone": "9876500004",
            "appointment_date": datetime.utcnow().isoformat()
        }, headers=headers)
        appt_id = appt_res.json.get("appointment_id") or appt_res.json.get("id")

        # Create payment transaction
        txn_res = self.client.post("/transactions/create", json={
            "transaction_type": "appointment",
            "appointment_id": appt_id,
            "amount": 750.0,
            "payment_method": "UPI",
            "status": "Success"
        }, headers=headers)
        self.assertEqual(txn_res.status_code, 201)
        txn_id = txn_res.json.get("id")

        with self.app.app_context():
            appt = Appointment.query.get(appt_id)
            self.assertEqual(appt.payment_status, "Paid")

        # Process refund
        refund_res = self.client.post(f"/transactions/{txn_id}/refund", json={
            "amount": 750.0,
            "reason": "Doctor emergency cancellation"
        }, headers=headers)
        self.assertEqual(refund_res.status_code, 201)
        self.assertEqual(refund_res.json.get("status"), "Success")

        with self.app.app_context():
            appt = Appointment.query.get(appt_id)
            self.assertEqual(appt.payment_status, "Refunded")

        # Cleanup
        self.client.delete(f"/appointments/{appt_id}", headers=headers)

    # 10. Cross-Tenant Document & Clinical Access Denial
    def test_cross_tenant_clinical_record_and_pdf_denial(self):
        # Create record in Org 1
        org1_headers = {"Authorization": f"Bearer {self.org1_token}", "Content-Type": "application/json"}
        create_res = self.client.post("/api/v1/industry-suite/records", json={
            "title": "Private Clinical Assessment",
            "record_type": "soap_note",
            "data": {"subjective": "Private symptoms"}
        }, headers=org1_headers)
        self.assertEqual(create_res.status_code, 201)
        rec_id = create_res.json.get("id")

        # Org 2 attempts to download Org 1 record PDF
        org2_headers = {"Authorization": f"Bearer {self.org2_token}"}
        pdf_res = self.client.get(f"/api/v1/industry-suite/records/{rec_id}/download-pdf", headers=org2_headers)
        self.assertEqual(pdf_res.status_code, 403)
        self.assertIn("Cross-tenant access denied", pdf_res.json.get("msg", ""))

        # Org 2 attempts to delete Org 1 record
        del_res = self.client.delete(f"/api/v1/industry-suite/records/{rec_id}", headers=org2_headers)
        self.assertEqual(del_res.status_code, 403)

        # Cleanup from Org 1
        self.client.delete(f"/api/v1/industry-suite/records/{rec_id}", headers=org1_headers)


if __name__ == "__main__":
    unittest.main()
