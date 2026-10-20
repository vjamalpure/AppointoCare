"""
AppointoCare Industry Leaders Competitor Matrix Verification Suite
Comprehensive automated tests verifying market benchmark parity and gap-closure:
1. Shared Platform:
   - Automation event dispatcher (`POST /api/v1/automation/dispatch-event`) & execution audit logging (`GET /api/v1/automation/logs`)
   - Customer 360 / Unified timeline (`GET /api/v1/customers/<id>/360`)
   - Operational KPIs across 9 verticals (`GET /api/v1/analytics/operational-kpis`)
2. Healthcare (Clinicea Parity):
   - Closed-loop care workflow (`GET /api/v1/healthcare/closed-loop-care/<patient_id>`)
   - Medication refill request & dispensing approval (`POST /api/v1/healthcare/medications/refills`, `POST /approve`)
3. Salon & Wellness (Zenoti Parity):
   - Cancellation recovery engine (`POST /api/v1/industry-suite/salon/recover-cancellation`)
   - Retail & consumable inventory POS (`GET /api/v1/industry-suite/inventory`, `POST /inventory`)
4. Finance & Wealth (Salesforce FSC & Investwell Parity):
   - Portfolio health & allocation drift (`GET /api/v1/industry-suite/finance/portfolio-health`)
   - Household relationship mapping (`GET /api/v1/industry-suite/finance/households`)
   - Risk suitability assessment profile (`POST /api/v1/industry-suite/finance/suitability-profile`)
5. Insurance Brokerage (EZLynx Parity):
   - Renewal command center (`GET /api/v1/industry-suite/insurance/renewal-command-center`)
   - Policy records administration (`POST /api/v1/industry-suite/insurance/policies`)
6. Retail & Bespoke (Clientbook & Shopify POS Parity):
   - Bespoke order lifecycle workspace (`POST /api/v1/industry-suite/retail/bespoke-orders`, `PUT /stage`)
7. Education & Study Abroad (ApplyBoard Parity):
   - Global university program catalog (`GET /api/v1/industry-suite/education/programs`)
   - Student admissions readiness scorecard (`POST /api/v1/industry-suite/education/readiness-score`)
8. Legal & Advisory (Clio & MyCase Parity):
   - Legal matters hub with adverse-party conflict clearance (`POST /api/v1/industry-suite/legal/matters`, `GET /matters`)
9. Real Estate & Architecture (Follow Up Boss & Buildertrend Parity):
   - Unit reservations with escrow deposit (`GET /api/v1/industry-suite/real-estate/reservations`)
   - Architecture project drawings & revisions (`GET /api/v1/industry-suite/real-estate/architecture-projects`)
10. Professional & IT Services (Accelo Parity):
   - Project margin early-warning engine (`GET /api/v1/industry-suite/professional/project-margins`)
   - P1–P4 SLA incident escalation tracking (`GET /api/v1/industry-suite/professional/incidents`)
"""

import unittest
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token
from app import create_app
from app.models import (
    db, Organization, User, Customer, AutomationRule, DiagnosticLabOrder
)
from app.utils.hash_helper import hash_password


class TestIndustryLeadersMatrix(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

        # 1. Organization for testing
        self.org = db.session.get(Organization, 1)
        if not self.org:
            self.org = Organization(
                name="Metro Multi-Specialty & Commercial Care",
                code="ORG-METRO-01",
                sector="Healthcare",
                username="metro_admin",
                password=hash_password("Pass@1234"),
                subscription_plan="Enterprise",
                subscription_status="Active"
            )
            db.session.add(self.org)
            db.session.commit()

        # 2. Doctor user
        self.doctor = User.query.filter_by(username="dr_matrix_lead").first()
        if not self.doctor:
            self.doctor = User(
                organization_id=self.org.id,
                username="dr_matrix_lead",
                password=hash_password("Pass@1234"),
                role="Doctor",
                is_active=True
            )
            db.session.add(self.doctor)
            db.session.commit()

        # 3. Patient/Customer
        self.customer = Customer.query.filter_by(organization_id=self.org.id, phone="9988776655").first()
        if not self.customer:
            self.customer = Customer(
                organization_id=self.org.id,
                name="Ananya Sen",
                phone="9988776655",
                email="ananya.sen@example.com"
            )
            db.session.add(self.customer)
            db.session.commit()

        # 4. Generate Tokens
        self.org_token = create_access_token(
            identity=str(self.org.id),
            additional_claims={"role": "Organization", "organization_id": self.org.id, "sub": str(self.org.id)}
        )
        self.doctor_token = create_access_token(
            identity=str(self.doctor.id),
            additional_claims={"role": "Doctor", "organization_id": self.org.id, "sub": "dr_matrix_lead"}
        )

        self.org_headers = {
            "Authorization": f"Bearer {self.org_token}",
            "Content-Type": "application/json"
        }
        self.doctor_headers = {
            "Authorization": f"Bearer {self.doctor_token}",
            "Content-Type": "application/json"
        }

    def tearDown(self):
        self.app_context.pop()

    # ==========================================
    # 1. SHARED PLATFORM TESTS
    # ==========================================
    def test_automation_event_dispatcher_and_execution_logs(self):
        """Test event-driven automation dispatcher and execution audit log logging."""
        # Ensure at least one active rule exists
        rule = AutomationRule.query.filter_by(organization_id=self.org.id, event_trigger="appointment.cancelled").first()
        if not rule:
            rule = AutomationRule(
                organization_id=self.org.id,
                name="Auto-trigger Waitlist Recall on Cancel",
                event_trigger="appointment.cancelled",
                action_type="NOTIFY_WAITLIST",
                is_active=True
            )
            db.session.add(rule)
            db.session.commit()

        # Dispatch event
        res = self.client.post(
            "/api/v1/automation/dispatch-event",
            headers=self.org_headers,
            json={"event_trigger": "appointment.cancelled", "payload": {"appointment_id": 101, "customer_id": self.customer.id}}
        )
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertGreaterEqual(data.get("executed_count", 0), 1)

        # Verify logs endpoint
        log_res = self.client.get("/api/v1/automation/logs", headers=self.org_headers)
        self.assertEqual(log_res.status_code, 200)
        logs = log_res.get_json()
        self.assertIsInstance(logs, list)
        self.assertGreater(len(logs), 0)
        self.assertEqual(logs[0]["event_trigger"], "appointment.cancelled")

    def test_customer_360_unified_timeline(self):
        """Test customer 360 endpoint returns unified timeline across services."""
        res = self.client.get(f"/api/v1/customers/{self.customer.id}/360", headers=self.doctor_headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("timeline_events", data)
        self.assertIn("customer", data)
        self.assertEqual(data["customer"]["id"], self.customer.id)

    def test_operational_kpis_across_all_9_verticals(self):
        """Test operational-kpis endpoint returns real metrics for the active organization's sector."""
        res = self.client.get("/api/v1/analytics/operational-kpis", headers=self.org_headers)
        self.assertEqual(res.status_code, 200)
        kpis = res.get_json()
        self.assertIn("sector", kpis)
        self.assertIn("sector_kpis", kpis)
        self.assertIn("funnel", kpis)
        self.assertIn("summary", kpis)

    # ==========================================
    # 2. HEALTHCARE & CLINICS (Clinicea Parity)
    # ==========================================
    def test_healthcare_closed_loop_care_and_refills(self):
        """Test Clinicea-parity closed-loop care and medication refill approvals."""
        # 1. Closed-loop care summary
        res = self.client.get(f"/api/v1/healthcare/closed-loop-care/{self.customer.id}", headers=self.doctor_headers)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("workflow_stage", data)
        self.assertIn("lab_orders", data)

        # 2. Medication Refill Creation
        refill_res = self.client.post(
            "/api/v1/healthcare/medications/refills",
            headers=self.doctor_headers,
            json={
                "customer_id": self.customer.id,
                "prescription_id": 999,
                "medication_name": "Atorvastatin 10mg",
                "quantity_requested": 30
            }
        )
        self.assertEqual(refill_res.status_code, 201)
        refill = refill_res.get_json()
        refill_id = refill["refill"]["id"]

        # 3. Approve Refill
        approve_res = self.client.post(
            f"/api/v1/healthcare/medications/refills/{refill_id}/approve",
            headers=self.doctor_headers,
            json={"instructions": "Dispensed 30 tablets. Take after dinner."}
        )
        self.assertEqual(approve_res.status_code, 200)
        self.assertEqual(approve_res.get_json()["status"], "Approved")

    # ==========================================
    # 3. SALON & WELLNESS (Zenoti Parity)
    # ==========================================
    def test_salon_cancellation_recovery_and_inventory(self):
        """Test Zenoti-parity cancellation recovery engine and inventory management."""
        # Cancellation Recovery
        rec_res = self.client.post(
            "/api/v1/industry-suite/salon/recover-cancellation",
            headers=self.org_headers,
            json={
                "cancelled_appointment_id": 401,
                "service_name": "Signature Balayage & Olaplex Treatment",
                "service_start": (datetime.utcnow() + timedelta(days=1)).isoformat()
            }
        )
        self.assertIn(rec_res.status_code, [200, 201])
        rec_data = rec_res.get_json()
        self.assertTrue(rec_data["success"])
        self.assertIn("offer", rec_data)

        # Inventory Item Creation & Listing
        inv_post = self.client.post(
            "/api/v1/industry-suite/inventory",
            headers=self.org_headers,
            json={
                "sku": f"SKU-SPA-{int(datetime.utcnow().timestamp())}",
                "name": "Moroccan Argan Repair Elixir 100ml",
                "category": "Hair Care",
                "stock_quantity": 25,
                "reorder_level": 5,
                "cost_price": 650.0,
                "retail_price": 1400.0
            }
        )
        self.assertEqual(inv_post.status_code, 201)

        inv_get = self.client.get("/api/v1/industry-suite/inventory", headers=self.org_headers)
        self.assertEqual(inv_get.status_code, 200)
        self.assertIsInstance(inv_get.get_json(), list)

    # ==========================================
    # 4. FINANCE & WEALTH (Salesforce FSC Parity)
    # ==========================================
    def test_finance_portfolio_health_and_suitability(self):
        """Test Salesforce FSC-parity portfolio health drift, household view, and suitability."""
        # Portfolio Health
        health_res = self.client.get(f"/api/v1/industry-suite/finance/portfolio-health?customer_id={self.customer.id}", headers=self.org_headers)
        self.assertEqual(health_res.status_code, 200)
        data = health_res.get_json()
        self.assertIn("status", data)
        self.assertIn("average_drift_percentage", data)

        # Household View
        house_res = self.client.get("/api/v1/industry-suite/finance/households", headers=self.org_headers)
        self.assertEqual(house_res.status_code, 200)
        self.assertIsInstance(house_res.get_json(), list)

        # Suitability Profile
        prof_res = self.client.post(
            "/api/v1/industry-suite/finance/suitability-profile",
            headers=self.org_headers,
            json={
                "customer_id": self.customer.id,
                "risk_category": "Growth Equity",
                "risk_score": 82,
                "investment_horizon_years": 10,
                "suitability_verified": True
            }
        )
        self.assertEqual(prof_res.status_code, 201)

    # ==========================================
    # 5. INSURANCE BROKERAGE (EZLynx Parity)
    # ==========================================
    def test_insurance_renewal_command_center_and_policies(self):
        """Test EZLynx-parity renewal command center and policy administration."""
        # Create Policy
        pol_res = self.client.post(
            "/api/v1/industry-suite/insurance/policies",
            headers=self.org_headers,
            json={
                "customer_id": self.customer.id,
                "policy_number": f"POL-HLTH-{int(datetime.utcnow().timestamp())}",
                "carrier": "HDFC ERGO",
                "policy_type": "Comprehensive Health",
                "premium_amount": 28500.0,
                "sum_assured": 1500000.0,
                "expiry_date": (datetime.utcnow() + timedelta(days=20)).isoformat()
            }
        )
        self.assertEqual(pol_res.status_code, 201)

        # Renewal Command Center
        ren_res = self.client.get("/api/v1/industry-suite/insurance/renewal-command-center", headers=self.org_headers)
        self.assertEqual(ren_res.status_code, 200)
        ren_data = ren_res.get_json()
        self.assertIn("renewals_pipeline", ren_data)

    # ==========================================
    # 6. RETAIL & LUXURY BESPOKE (Clientbook Parity)
    # ==========================================
    def test_retail_bespoke_order_lifecycle(self):
        """Test bespoke order creation and stage progression."""
        # Create bespoke order
        create_res = self.client.post(
            "/api/v1/industry-suite/retail/bespoke-orders",
            headers=self.org_headers,
            json={
                "customer_id": self.customer.id,
                "garment_type": "Three-Piece Tuxedo",
                "fabric_reference": "Vitale Barberis Canonico Super 150s",
                "measurements": {"chest": 42, "waist": 34, "inseam": 32},
                "total_price_inr": 85000.0,
                "deposit_paid_inr": 40000.0
            }
        )
        self.assertEqual(create_res.status_code, 201)
        order = create_res.get_json()["order"]
        order_id = order["id"]

        # Advance stage
        stage_res = self.client.put(
            f"/api/v1/industry-suite/retail/bespoke-orders/{order_id}/stage",
            headers=self.org_headers,
            json={"stage": "Fittings", "notes": "First fitting scheduled in VIP lounge"}
        )
        self.assertEqual(stage_res.status_code, 200)
        self.assertEqual(stage_res.get_json()["stage"], "Fittings")

    # ==========================================
    # 7. EDUCATION & STUDY ABROAD (ApplyBoard Parity)
    # ==========================================
    def test_education_programs_and_student_readiness(self):
        """Test ApplyBoard-parity university programs catalog and student readiness scorecard."""
        # Program Catalog
        prog_res = self.client.get("/api/v1/industry-suite/education/programs", headers=self.org_headers)
        self.assertEqual(prog_res.status_code, 200)
        progs = prog_res.get_json()
        self.assertIsInstance(progs, list)
        self.assertGreater(len(progs), 0)

        # Student Readiness Scorecard
        score_res = self.client.post(
            "/api/v1/industry-suite/education/readiness-score",
            headers=self.org_headers,
            json={
                "student_id": self.customer.id,
                "target_program_id": progs[0]["id"],
                "gpa": 3.90,
                "test_score": "GRE 328 / TOEFL 115",
                "documents_provided": ["Official Transcripts", "Statement of Purpose", "Recommendation Letters", "Financial Proof"]
            }
        )
        score_data = score_res.get_json() or {}
        score_card = score_data.get("scorecard", {})
        self.assertIn("readiness_score", score_card)
        self.assertIn("readiness_tier", score_card)

    # ==========================================
    # 8. LEGAL & CONSULTANCY (Clio Parity)
    # ==========================================
    def test_legal_matters_and_conflict_checks(self):
        """Test Clio-parity legal matter management with conflict checks."""
        matter_res = self.client.post(
            "/api/v1/industry-suite/legal/matters",
            headers=self.org_headers,
            json={
                "customer_id": self.customer.id,
                "title": "Cross-Border Series A Term Sheet Advisory",
                "practice_area": "Corporate / Venture Capital",
                "lead_attorney": "Adv. Rajesh Varma",
                "retainer_balance_inr": 150000.0,
                "adverse_party_names": ["Alpha Syndicate Ltd"]
            }
        )
        self.assertEqual(matter_res.status_code, 201)
        matter_data = matter_res.get_json()["matter"]
        self.assertTrue(matter_data["conflict_cleared"])

        list_res = self.client.get("/api/v1/industry-suite/legal/matters", headers=self.org_headers)
        self.assertEqual(list_res.status_code, 200)
        self.assertIsInstance(list_res.get_json(), list)

    # ==========================================
    # 9. REAL ESTATE & ARCHITECTURE (Follow Up Boss & Buildertrend Parity)
    # ==========================================
    def test_real_estate_reservations_and_architecture(self):
        """Test unit reservations with escrow and architecture project workflows."""
        res_list = self.client.get("/api/v1/industry-suite/real-estate/reservations", headers=self.org_headers)
        self.assertEqual(res_list.status_code, 200)
        self.assertIsInstance(res_list.get_json(), list)

        arch_list = self.client.get("/api/v1/industry-suite/real-estate/architecture-projects", headers=self.org_headers)
        self.assertEqual(arch_list.status_code, 200)
        self.assertIsInstance(arch_list.get_json(), list)

    # ==========================================
    # 10. PROFESSIONAL & IT SERVICES (Accelo Parity)
    # ==========================================
    def test_professional_project_margins_and_incidents(self):
        """Test Accelo-parity project margin early-warning and SLA incident tracking."""
        margin_res = self.client.get("/api/v1/industry-suite/professional/project-margins", headers=self.org_headers)
        self.assertEqual(margin_res.status_code, 200)
        margins = margin_res.get_json()
        self.assertIsInstance(margins, list)
        self.assertGreater(len(margins), 0)
        self.assertIn("current_margin_pct", margins[0])

        inc_res = self.client.get("/api/v1/industry-suite/professional/incidents", headers=self.org_headers)
        self.assertEqual(inc_res.status_code, 200)
        incidents = inc_res.get_json()
        self.assertIsInstance(incidents, list)
        self.assertGreater(len(incidents), 0)
        self.assertIn("severity", incidents[0])


if __name__ == "__main__":
    unittest.main()
