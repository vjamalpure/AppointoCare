"""
Comprehensive Sample Data Migration Script for AppointoCare Multi-Industry Platform
Seeds users of each level (SuperAdmin, Org Admins, Staff/Specialists/Managers),
all 9 industry sectors, branches, services, customers/patients, appointments,
transactions, subscriptions, plans, templates, notifications, audit logs,
and rich specialized IndustryRecord entries for all market-leading sector features.

Can be run standalone:
    python sample_data.py [--reset]
or invoked programmatically via:
    from sample_data import seed_all_sample_data
    seed_all_sample_data()
"""

import os
import sys
from datetime import datetime, timedelta
from app import create_app
from app.models import (
    db,
    Admin,
    Organization,
    User,
    Branch,
    Customer,
    Patient,
    Service,
    Appointment,
    AppointmentTransaction,
    OrganizationTransaction,
    SubscriptionPlan,
    Subscription,
    SectorTemplate,
    MessageLog,
    AuditLog,
    Notification,
    IndustryRecord
)
from app.utils.hash_helper import hash_password

DEFAULT_ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin@12345")
DEFAULT_ORG_PASSWORD = os.getenv("ORG_PASSWORD", "Org@12345")
DEFAULT_STAFF_PASSWORD = os.getenv("STAFF_PASSWORD", "Staff@12345")

# All 9 multi-industry organizations with market-leading platform features & records
SAMPLE_ORGANIZATIONS = [
    {
        "name": "City Care Health & Dental",
        "code": "ORG1",
        "sector": "Healthcare",
        "username": "org1",
        "plan": "Enterprise",
        "status": "Active",
        "branches": [
            {"name": "Downtown Central Hospital", "address": "100 Medical Center Blvd, Metro City", "phone": "+1 555-0101", "tz": "America/New_York"},
            {"name": "Westside Dental Specialty Center", "address": "450 Westside Ave, Suite 300", "phone": "+1 555-0102", "tz": "America/New_York"},
        ],
        "staff": [
            {"username": "staff1", "role": "Staff"},
            {"username": "doc_sarah", "role": "Doctor"},
            {"username": "dr_chen", "role": "Doctor"},
        ],
        "services": [
            {"name": "General Physician Consultation", "category": "Medical", "price": 120.0, "duration": 30},
            {"name": "Comprehensive Dental Cleaning & Exam", "category": "Dental", "price": 180.0, "duration": 45},
            {"name": "Orthopedic Assessment & Digital X-Ray", "category": "Diagnostics", "price": 260.0, "duration": 60},
            {"name": "Pediatric Routine Wellness Exam", "category": "Pediatrics", "price": 140.0, "duration": 30},
        ],
        "customers": [
            {"name": "Michael Harrison", "phone": "+1 555-1101", "email": "michael.h@example.com", "gender": "Male", "mrn": "MRN-2026-901"},
            {"name": "Sarah Connor", "phone": "+1 555-1102", "email": "s.connor@example.com", "gender": "Female", "mrn": "MRN-2026-902"},
            {"name": "David Miller", "phone": "+1 555-1103", "email": "dmiller@example.com", "gender": "Male", "mrn": "MRN-2026-903"},
            {"name": "Emma Watson", "phone": "+1 555-1104", "email": "emma.w@example.com", "gender": "Female", "mrn": "MRN-2026-904"},
        ],
        "appointments": [
            {"customer": "Michael Harrison", "phone": "+1 555-1101", "service": "General Physician Consultation", "days_offset": 0, "status": "Booked", "payment": "Paid", "amount": 120.0},
            {"customer": "Sarah Connor", "phone": "+1 555-1102", "service": "Comprehensive Dental Cleaning & Exam", "days_offset": 1, "status": "Booked", "payment": "Unpaid", "amount": 180.0},
            {"customer": "David Miller", "phone": "+1 555-1103", "service": "Orthopedic Assessment & Digital X-Ray", "days_offset": -1, "status": "Completed", "payment": "Paid", "amount": 260.0},
            {"customer": "Emma Watson", "phone": "+1 555-1104", "service": "Pediatric Routine Wellness Exam", "days_offset": -2, "status": "Completed", "payment": "Paid", "amount": 140.0},
        ],
        "industry_records": [
            {
                "title": "Dr. Sarah Rx - Michael Harrison (Post-Op Antibiotic & Analgesic)",
                "record_type": "prescription",
                "customer_phone": "+1 555-1101",
                "status": "Active",
                "data": {
                    "prescriber": "Dr. Sarah Jenkins, MD (Board Certified)",
                    "rx_number": "RX-2026-HC-00812",
                    "diagnosis": "Acute bacterial maxillary sinusitis with localized dental inflammation.",
                    "vitals": {"bp": "122/78 mmHg", "pulse": "72 bpm", "temp": "98.6 Â°F", "spo2": "99%"},
                    "medications": [
                        {"name": "Amoxicillin / Clavulanate 625mg", "dosage": "1 tablet twice daily", "duration": "7 days", "instructions": "Take with meals. Complete entire course."},
                        {"name": "Ibuprofen 400mg", "dosage": "1 tablet as needed", "duration": "5 days", "instructions": "Take with food for pain."}
                    ],
                    "refills": 0,
                    "signed_electronically": True
                }
            },
            {
                "title": "Comprehensive Triage Intake & Vitals Matrix - Sarah Connor",
                "record_type": "triage",
                "customer_phone": "+1 555-1102",
                "status": "Active",
                "data": {
                    "triage_level": "Tier 3 - Semi-Urgent",
                    "blood_pressure": "135/85 mmHg",
                    "pulse_rate": "84 bpm",
                    "body_temperature": "99.1 Â°F",
                    "spo2_oxygen": "97%",
                    "allergies": ["Penicillin", "Latex"],
                    "presenting_complaint": "Persistent severe right-side dental pain radiating to jaw.",
                    "attending_nurse": "Staff RN Lisa"
                }
            },
            {
                "title": "Executive Health & Lipid Panel Diagnostic Report - David Miller",
                "record_type": "lab_report",
                "customer_phone": "+1 555-1103",
                "status": "Completed",
                "data": {
                    "panel_name": "Executive Lipid & Comprehensive Metabolic Profile",
                    "total_cholesterol": "192 mg/dL",
                    "hdl": "54 mg/dL",
                    "ldl": "116 mg/dL",
                    "triglycerides": "110 mg/dL",
                    "fasting_glucose": "94 mg/dL",
                    "hba1c": "5.4%",
                    "lab_accession_id": "METRO-LAB-2026-9901",
                    "interpretation": "Normal metabolic markers. Optimal glycemic index."
                }
            },
            {
                "title": "OPD Queue Token #OPD-001 - Michael Harrison",
                "record_type": "opd_queue",
                "customer_phone": "+1 555-1101",
                "status": "Waiting",
                "data": {
                    "token_number": "OPD-001",
                    "queue_status": "Waiting",
                    "department": "General Medicine",
                    "priority": "Normal",
                    "assigned_doctor": "Dr. Sarah Jenkins",
                    "estimated_wait": "15 minutes",
                    "check_in_time": "09:30 AM"
                }
            },
            {
                "title": "OPD Queue Token #OPD-002 - Emma Watson",
                "record_type": "opd_queue",
                "customer_phone": "+1 555-1104",
                "status": "In Consultation",
                "data": {
                    "token_number": "OPD-002",
                    "queue_status": "In Consultation",
                    "department": "Pediatrics",
                    "priority": "Normal",
                    "assigned_doctor": "Dr. Chen Wei",
                    "estimated_wait": "0 minutes",
                    "check_in_time": "09:15 AM"
                }
            },
            {
                "title": "SOAP Clinical Notes - David Miller (Post-Orthopedic Assessment)",
                "record_type": "soap_note",
                "customer_phone": "+1 555-1103",
                "status": "Completed",
                "data": {
                    "subjective": "Patient reports persistent right knee pain post-marathon. Pain score 5/10, aggravated by stair climbing.",
                    "objective": "Range of motion 120Â° flexion. X-ray shows mild patellofemoral joint space narrowing. No effusion.",
                    "assessment": "Early-stage patellofemoral syndrome. BMI 24.2, cardiovascular fitness excellent.",
                    "plan": "Physical therapy referral 3x/week for 6 weeks. Naproxen 500mg PRN. Follow-up in 30 days with MRI if unresolved.",
                    "icd10_codes": ["M22.0", "M25.561"],
                    "attending_physician": "Dr. Chen Wei, MD (Orthopedics)"
                }
            },
            {
                "title": "Medical Invoice & Pre-Auth #INV-HC-2026-001 - Sarah Connor",
                "record_type": "medical_bill",
                "customer_phone": "+1 555-1102",
                "status": "Active",
                "data": {
                    "invoice_number": "INV-HC-2026-001",
                    "procedure_codes": ["D0120", "D1110"],
                    "consultation_fee": 180.0,
                    "lab_charges": 0.0,
                    "pharmacy_charges": 45.0,
                    "total_billed": 225.0,
                    "insurance_coverage": 180.0,
                    "patient_copay": 45.0,
                    "tpa_provider": "Aetna PPO Network",
                    "pre_auth_status": "Approved"
                }
            }
        ]
    },
    {
        "name": "Apex Aesthetics & Wellness Spa",
        "code": "ORG2",
        "sector": "Salon & Wellness",
        "username": "org2",
        "plan": "Professional",
        "status": "Active",
        "branches": [
            {"name": "Midtown Luxe Spa & Lounge", "address": "780 Fifth Avenue, Floor 4", "phone": "+1 555-0201", "tz": "America/New_York"}
        ],
        "staff": [
            {"username": "olivia_spa", "role": "Therapist"},
            {"username": "chloe_hair", "role": "Stylist"}
        ],
        "services": [
            {"name": "Hydra-Facial & Dermaplaning Session", "category": "Aesthetics", "price": 220.0, "duration": 60},
            {"name": "Balayage Color & Master Precision Cut", "category": "Hair", "price": 310.0, "duration": 90},
            {"name": "Hot Stone Aromatherapy Deep Massage", "category": "Body", "price": 160.0, "duration": 75}
        ],
        "customers": [
            {"name": "Jessica Alba", "phone": "+1 555-2101", "email": "jessica.a@example.com", "gender": "Female"},
            {"name": "Victoria Beckham", "phone": "+1 555-2102", "email": "v.beckham@example.com", "gender": "Female"},
            {"name": "Sophia Loren", "phone": "+1 555-2103", "email": "sophia.l@example.com", "gender": "Female"}
        ],
        "appointments": [
            {"customer": "Jessica Alba", "phone": "+1 555-2101", "service": "Hydra-Facial & Dermaplaning Session", "days_offset": 0, "status": "Booked", "payment": "Paid", "amount": 220.0},
            {"customer": "Victoria Beckham", "phone": "+1 555-2102", "service": "Balayage Color & Master Precision Cut", "days_offset": 2, "status": "Booked", "payment": "Unpaid", "amount": 310.0},
            {"customer": "Sophia Loren", "phone": "+1 555-2103", "service": "Hot Stone Aromatherapy Deep Massage", "days_offset": -1, "status": "Completed", "payment": "Paid", "amount": 160.0}
        ],
        "industry_records": [
            {
                "title": "Suite Allocation - Hydrotherapy Sanctuary Suite 2 (Jessica Alba)",
                "record_type": "room_allocation",
                "customer_phone": "+1 555-2101",
                "status": "Active",
                "data": {
                    "suite_name": "Suite 2 - Hydrotherapy & Aromatherapy Sanctuary",
                    "lead_aesthetician": "Olivia Vance (Senior Aesthetician)",
                    "ambient_temperature": "24Â°C",
                    "scent_profile": "Organic Eucalyptus & Lavender Infusion",
                    "suite_amenities": ["Heated ergonomic contour table", "Chromotherapy soft illumination", "Soundproof acoustical enclosure"]
                }
            },
            {
                "title": "Bespoke Balayage Color Formula Card - Victoria Beckham",
                "record_type": "formula_card",
                "customer_phone": "+1 555-2102",
                "status": "Active",
                "data": {
                    "color_system": "Wella Illumina High-Lift Blend",
                    "formula_ratio": "9/60 (45g) + 10/1 (15g) with 20 Vol Color Touch Developer",
                    "processing_duration": "35 minutes at room temp",
                    "patch_test_date": "2026-09-12",
                    "patch_test_result": "Negative / Clear",
                    "hair_porosity": "Medium",
                    "scalp_sensitivity": "None observed"
                }
            },
            {
                "title": "VIP Spa Add-on Ritual & Upsell Package - Sophia Loren",
                "record_type": "upsell_package",
                "customer_phone": "+1 555-2103",
                "status": "Completed",
                "data": {
                    "base_treatment": "Hot Stone Aromatherapy Deep Massage",
                    "selected_upsells": [
                        {"name": "24K Gold Collagen Eye Treatment", "price": 45.0},
                        {"name": "Organic Moroccan Rosehip Scalp Ritual", "price": 35.0},
                        {"name": "Volcanic Basalt Heated Foot Compress", "price": 30.0}
                    ],
                    "additional_total": 110.0,
                    "guest_experience_rating": "5 / 5 Stars"
                }
            },
            {
                "title": "10-Session Ritual Pass (Gold Tier) - Jessica Alba",
                "record_type": "ritual_pass",
                "customer_phone": "+1 555-2101",
                "status": "Active",
                "data": {
                    "pass_type": "Gold Spa Ritual Pass",
                    "total_sessions": 10,
                    "sessions_used": 3,
                    "sessions_remaining": 7,
                    "pass_value": 1800.0,
                    "per_session_value": 180.0,
                    "valid_services": ["Hydra-Facial", "Dermaplaning", "Deep Tissue Massage", "Aromatherapy"],
                    "expiry_date": "2027-03-15",
                    "auto_renew": True
                }
            },
            {
                "title": "Backbar Consumable Log - Suite 2 (September 2026)",
                "record_type": "backbar_log",
                "customer_phone": "+1 555-2101",
                "status": "Active",
                "data": {
                    "suite_name": "Suite 2 - Hydrotherapy Sanctuary",
                    "period": "September 2026",
                    "consumables": [
                        {"item": "Dermalogica Daily Microfoliant (75g)", "qty_used": 4, "unit_cost": 18.50, "total": 74.0},
                        {"item": "Elemis Pro-Collagen Marine Cream (50ml)", "qty_used": 2, "unit_cost": 42.0, "total": 84.0},
                        {"item": "Organic Essential Oil Blend (Lavender/Eucalyptus)", "qty_used": 6, "unit_cost": 12.0, "total": 72.0}
                    ],
                    "total_consumable_cost": 230.0,
                    "variance_from_budget": "-$20 (Under budget)"
                }
            }
        ]
    },
    {
        "name": "Vanguard Wealth & Asset Advisory",
        "code": "ORG3",
        "sector": "Finance",
        "username": "org3",
        "plan": "Enterprise",
        "status": "Active",
        "branches": [
            {"name": "Wall Street Private Client Group", "address": "14 Wall Street, 22nd Floor", "phone": "+1 555-0301", "tz": "America/New_York"}
        ],
        "staff": [
            {"username": "alex_wealth", "role": "Advisor"},
            {"username": "sarah_tax", "role": "Analyst"}
        ],
        "services": [
            {"name": "High-Net-Worth Portfolio Restructuring", "category": "Advisory", "price": 500.0, "duration": 60},
            {"name": "Cross-Border Tax & Trust Structuring", "category": "Tax", "price": 650.0, "duration": 90},
            {"name": "Retirement & Estate Liquidity Planning", "category": "Estate", "price": 350.0, "duration": 45}
        ],
        "customers": [
            {"name": "Marcus Vance", "phone": "+1 555-3101", "email": "marcus.v@example.com", "gender": "Male"},
            {"name": "Helena Montgomery", "phone": "+1 555-3102", "email": "h.montgomery@example.com", "gender": "Female"}
        ],
        "appointments": [
            {"customer": "Marcus Vance", "phone": "+1 555-3101", "service": "High-Net-Worth Portfolio Restructuring", "days_offset": 0, "status": "Booked", "payment": "Paid", "amount": 500.0},
            {"customer": "Helena Montgomery", "phone": "+1 555-3102", "service": "Cross-Border Tax & Trust Structuring", "days_offset": 1, "status": "Booked", "payment": "Paid", "amount": 650.0}
        ],
        "industry_records": [
            {
                "title": "FINRA Rule 2111 KYC & Suitability Dossier - Marcus Vance",
                "record_type": "kyc_dossier",
                "customer_phone": "+1 555-3101",
                "status": "Active",
                "data": {
                    "investor_accreditation": "Qualified Purchaser (Securities Act 3c7)",
                    "verified_liquid_net_worth": "$4,200,000 USD",
                    "annual_earned_income": "$750,000 USD",
                    "risk_tolerance_class": "Moderate-Aggressive Capital Appreciation",
                    "investment_horizon": "10 - 15 Years",
                    "aml_ofac_screening": "Clear / No PEP or Sanction Hits",
                    "certifying_officer": "Alex Vance, CFP, CFA"
                }
            },
            {
                "title": "Q4 Strategic Asset Allocation Matrix - Marcus Vance",
                "record_type": "portfolio_allocation",
                "customer_phone": "+1 555-3101",
                "status": "Active",
                "data": {
                    "benchmark_target": "Global Balanced 70/30 Index",
                    "target_allocations": {
                        "public_equities_pct": 60,
                        "private_credit_pct": 15,
                        "fixed_income_pct": 15,
                        "cash_and_alternatives_pct": 10
                    },
                    "rebalancing_drift": "+4.2% Overweight in US Tech Equity",
                    "recommended_trade": "Trim US Large Cap equity; reallocate $250k into Tax-Exempt Municipal Bonds."
                }
            },
            {
                "title": "Form ADV Part 2A & Fiduciary Engagement Disclosure - Helena Montgomery",
                "record_type": "fiduciary_letter",
                "customer_phone": "+1 555-3102",
                "status": "Active",
                "data": {
                    "engagement_type": "Discretionary Multi-Family Office Mandate",
                    "advisory_fee_schedule": "0.65% AUM per annum billed quarterly in arrears",
                    "custodian_bank": "BNY Mellon Pershing",
                    "fiduciary_standard": "SEC Section 206 Standard of Utmost Good Faith",
                    "effective_date": "2026-09-10"
                }
            },
            {
                "title": "Q3 Fiduciary Quarterly Review Scheduler - Marcus Vance",
                "record_type": "quarterly_review",
                "customer_phone": "+1 555-3101",
                "status": "Active",
                "data": {
                    "review_quarter": "Q3 2026",
                    "scheduled_review_date": "2026-10-05",
                    "agenda_items": [
                        "Portfolio performance vs S&P 500 benchmark",
                        "Tax-loss harvesting opportunities before year-end",
                        "Alternative investment allocation review (Private Credit)",
                        "Insurance coverage adequacy audit"
                    ],
                    "risk_score_current": 6.8,
                    "risk_score_target": 7.0,
                    "compliance_status": "All Form ADV disclosures current"
                }
            }
        ]
    },
    {
        "name": "Sovereign Life & Risk Insurance",
        "code": "ORG4",
        "sector": "Insurance",
        "username": "org4",
        "plan": "Professional",
        "status": "Active",
        "branches": [
            {"name": "Financial District Branch", "address": "200 Liberty Street, Suite 12", "phone": "+1 555-0401", "tz": "America/New_York"}
        ],
        "staff": [
            {"username": "victoria_insur", "role": "Underwriter"}
        ],
        "services": [
            {"name": "Whole-Life & Term Policy Underwriting", "category": "Life", "price": 0.0, "duration": 45},
            {"name": "Commercial Liability & Cyber Shield Review", "category": "Corporate", "price": 250.0, "duration": 60}
        ],
        "customers": [
            {"name": "Ethan Hunt", "phone": "+1 555-4101", "email": "ethan.h@example.com", "gender": "Male"},
            {"name": "Robert Langdon", "phone": "+1 555-4102", "email": "r.langdon@example.com", "gender": "Male"}
        ],
        "appointments": [
            {"customer": "Ethan Hunt", "phone": "+1 555-4101", "service": "Commercial Liability & Cyber Shield Review", "days_offset": 1, "status": "Booked", "payment": "Paid", "amount": 250.0},
            {"customer": "Robert Langdon", "phone": "+1 555-4102", "service": "Whole-Life & Term Policy Underwriting", "days_offset": -1, "status": "Completed", "payment": "Paid", "amount": 0.0}
        ],
        "industry_records": [
            {
                "title": "Key-Person Term Life Quote & Actuarial Breakdown - Ethan Hunt",
                "record_type": "premium_quote",
                "customer_phone": "+1 555-4101",
                "status": "Active",
                "data": {
                    "policy_tier": "20-Year Level Term Key-Person Life",
                    "total_sum_assured": "$2,500,000 USD",
                    "underwriting_class": "Preferred Plus Non-Smoker",
                    "annual_premium": 1450.0,
                    "monthly_premium": 125.0,
                    "included_riders": ["Accelerated Death Benefit for Terminal Illness", "Accidental Death & Dismemberment Rider"]
                }
            },
            {
                "title": "Medical & Hazard Underwriting Questionnaire - Robert Langdon",
                "record_type": "underwriting_dossier",
                "customer_phone": "+1 555-4102",
                "status": "Completed",
                "data": {
                    "applicant_age": 48,
                    "body_mass_index": 23.8,
                    "tobacco_use": "Non-Smoker (Verified Cotinine Screen Negative)",
                    "hazardous_activities": "Occasional international field research (Low Risk)",
                    "cardiovascular_history": "Clear / Normal EKG on file",
                    "underwriting_verdict": "Standard Table A / Approved with No Exclusions"
                }
            },
            {
                "title": "FNOL Claim Adjudication Docket #CLM-2026-0819 - Ethan Hunt",
                "record_type": "claim_file",
                "customer_phone": "+1 555-4101",
                "status": "Settled",
                "data": {
                    "claim_id": "CLM-2026-0819",
                    "policy_number": "POL-NY-77291-L",
                    "incident_type": "Inpatient Emergency Surgery Reimbursement",
                    "claimed_amount": 14200.0,
                    "adjudicated_amount": 13800.0,
                    "deductible_applied": 400.0,
                    "status": "Approved & Disbursed to Healthcare Provider"
                }
            },
            {
                "title": "Policy Schedule & Nominee Document Vault - Robert Langdon",
                "record_type": "policy_vault",
                "customer_phone": "+1 555-4102",
                "status": "Active",
                "data": {
                    "policy_number": "POL-NY-77291-L",
                    "policy_type": "20-Year Level Premium Term Life",
                    "sum_assured": "$2,500,000 USD",
                    "nominees": [
                        {"name": "Margaret Langdon", "relationship": "Spouse", "share_pct": 60},
                        {"name": "Philip Langdon", "relationship": "Son", "share_pct": 40}
                    ],
                    "endorsement_riders": ["Accidental Death Benefit", "Critical Illness Accelerator"],
                    "last_premium_paid": "2026-09-01",
                    "next_premium_due": "2026-10-01"
                }
            }
        ]
    },
    {
        "name": "Aura Haute Couture & Styling Lounge",
        "code": "ORG5",
        "sector": "Retail",
        "username": "org5",
        "plan": "Professional",
        "status": "Active",
        "branches": [
            {"name": "Madison Avenue Showroom", "address": "650 Madison Avenue", "phone": "+1 555-0501", "tz": "America/New_York"}
        ],
        "staff": [
            {"username": "jeanluc_style", "role": "Stylist"}
        ],
        "services": [
            {"name": "VIP Runway Wardrobe Consultation", "category": "Styling", "price": 300.0, "duration": 90},
            {"name": "Bespoke Suiting & Tailoring Fitting", "category": "Tailoring", "price": 150.0, "duration": 45}
        ],
        "customers": [
            {"name": "Claire Dupont", "phone": "+1 555-5101", "email": "c.dupont@example.com", "gender": "Female"},
            {"name": "Vivienne Westwood VIP", "phone": "+1 555-5102", "email": "vip.client@example.com", "gender": "Female"}
        ],
        "appointments": [
            {"customer": "Claire Dupont", "phone": "+1 555-5101", "service": "VIP Runway Wardrobe Consultation", "days_offset": 0, "status": "Booked", "payment": "Paid", "amount": 300.0},
            {"customer": "Vivienne Westwood VIP", "phone": "+1 555-5102", "service": "Bespoke Suiting & Tailoring Fitting", "days_offset": 3, "status": "Booked", "payment": "Paid", "amount": 150.0}
        ],
        "industry_records": [
            {
                "title": "Haute Couture Anatomical Sizing Matrix - Claire Dupont",
                "record_type": "sizing_matrix",
                "customer_phone": "+1 555-5101",
                "status": "Active",
                "data": {
                    "measurements": {
                        "bust": "34B",
                        "waist": "26.0 in",
                        "high_hip": "33.5 in",
                        "low_hip": "36.0 in",
                        "shoulder_breadth": "15.0 in",
                        "inseam": "31.5 in",
                        "sleeve_length": "23.0 in"
                    },
                    "posture_notes": "Slight erect posture, right shoulder +0.5cm height variation.",
                    "fabric_preferences": ["Pure Mulberry Silk", "Loro Piana Double-Faced Cashmere", "French Chantilly Lace"]
                }
            },
            {
                "title": "Chambre PrivÃ©e Lounge Reservation - Claire Dupont",
                "record_type": "vip_lounge",
                "customer_phone": "+1 555-5101",
                "status": "Active",
                "data": {
                    "reserved_suite": "The Platinum Mirror Salon (Chambre PrivÃ©e 1)",
                    "beverage_service": "Dom PÃ©rignon 2013 Brut & Sparkling San Pellegrino",
                    "curated_soundtrack": "Acoustic Paris Classical Lounge",
                    "accompanying_guests": 1,
                    "personal_concierge": "Jean-Luc (Senior Wardrobe Director)"
                }
            },
            {
                "title": "Autumn/Winter Paris Runway Curation Lookbook",
                "record_type": "lookbook",
                "customer_phone": "+1 555-5101",
                "status": "Active",
                "data": {
                    "capsule_collection": "AURA Fall Couture 2026",
                    "curated_garments": [
                        {"sku": "AURA-C-011", "name": "Double-Breasted Cashmere Trench", "color": "Camel", "price": 3800.0},
                        {"sku": "AURA-C-042", "name": "Silk Crepe-de-Chine Evening Slip Gown", "color": "Midnight Navy", "price": 4200.0},
                        {"sku": "AURA-A-108", "name": "Hand-Stitched Italian Nappa Gloves", "color": "Bordeaux", "price": 650.0}
                    ],
                    "total_lookbook_value": 8650.0
                }
            },
            {
                "title": "Bespoke Alteration Pipeline #ALT-2026-019 - Vivienne Westwood VIP",
                "record_type": "alteration_ticket",
                "customer_phone": "+1 555-5102",
                "status": "Active",
                "data": {
                    "ticket_id": "ALT-2026-019",
                    "garment": "Hand-Tailored Silk Lapel Tuxedo Jacket",
                    "alteration_type": "Sleeve Shortening + Waist Suppression",
                    "stages": [
                        {"stage": "Pinned & Marked", "status": "Completed", "date": "2026-09-14"},
                        {"stage": "In Atelier (Master Tailor)", "status": "In Progress", "date": "2026-09-16"},
                        {"stage": "Pressed & Quality Check", "status": "Pending", "date": None},
                        {"stage": "Ready for Client Fitting", "status": "Pending", "date": None}
                    ],
                    "estimated_completion": "2026-09-20",
                    "alteration_fee": 185.0
                }
            }
        ]
    },
    {
        "name": "Beacon Global University Counseling",
        "code": "ORG6",
        "sector": "Education",
        "username": "org6",
        "plan": "Professional",
        "status": "Active",
        "branches": [
            {"name": "Academic Heights Center", "address": "120 College Walk, Suite 500", "phone": "+1 555-0601", "tz": "America/New_York"}
        ],
        "staff": [
            {"username": "elena_counsel", "role": "Counselor"}
        ],
        "services": [
            {"name": "Ivy League Admissions Strategy Call", "category": "Admissions", "price": 400.0, "duration": 60},
            {"name": "SOP & Research Statement Review", "category": "Editorial", "price": 250.0, "duration": 45}
        ],
        "customers": [
            {"name": "Alexander Young", "phone": "+1 555-6101", "email": "ayoung@example.com", "gender": "Male"},
            {"name": "Sophia Chen", "phone": "+1 555-6102", "email": "schen@example.com", "gender": "Female"}
        ],
        "appointments": [
            {"customer": "Alexander Young", "phone": "+1 555-6101", "service": "Ivy League Admissions Strategy Call", "days_offset": 1, "status": "Booked", "payment": "Paid", "amount": 400.0},
            {"customer": "Sophia Chen", "phone": "+1 555-6102", "service": "SOP & Research Statement Review", "days_offset": -1, "status": "Completed", "payment": "Paid", "amount": 250.0}
        ],
        "industry_records": [
            {
                "title": "Class of 2027 College Shortlist - Alexander Young",
                "record_type": "university_shortlist",
                "customer_phone": "+1 555-6101",
                "status": "Active",
                "data": {
                    "intended_major": "Computer Science & Artificial Intelligence",
                    "unweighted_gpa": "3.96 / 4.0",
                    "standardized_tests": "SAT 1550 (Math 800, EBRW 750)",
                    "reach_universities": ["Stanford University", "MIT", "Carnegie Mellon SCS"],
                    "match_universities": ["Georgia Institute of Technology", "Univ of Michigan Ann Arbor", "UT Austin"],
                    "safety_universities": ["Purdue University", "Univ of Maryland College Park"]
                }
            },
            {
                "title": "Admissions Milestones & Common App Timetable - Alexander Young",
                "record_type": "application_milestones",
                "customer_phone": "+1 555-6101",
                "status": "Active",
                "data": {
                    "early_action_deadline": "Nov 01, 2026 (Stanford REA)",
                    "common_app_essay_status": "Draft 3 - Counselor Revision in Progress",
                    "letters_of_recommendation": {
                        "ap_calculus_bc_teacher": "Submitted",
                        "ap_physics_c_teacher": "Submitted",
                        "guidance_counselor": "Drafted"
                    },
                    "financial_aid_profile": "CSS Profile & FAFSA verified"
                }
            },
            {
                "title": "Personal Statement Hook & Narrative Rubric - Sophia Chen",
                "record_type": "sop_review",
                "customer_phone": "+1 555-6102",
                "status": "Completed",
                "data": {
                    "essay_prompt": "Common App: Lessons from a Obstacle or Failure",
                    "evaluation_scores": {
                        "narrative_hook": "9 / 10",
                        "originality_and_voice": "8.5 / 10",
                        "intellectual_curiosity": "9 / 10",
                        "grammar_and_mechanics": "9.5 / 10"
                    },
                    "counselor_editorial_remarks": "Compelling narrative opening on computational biology laboratory trial. Sharpen concluding paragraph to clearly synthesize prospective undergraduate research goals."
                }
            },
            {
                "title": "Dean's Merit Scholarship Match Analysis - Alexander Young",
                "record_type": "scholarship_match",
                "customer_phone": "+1 555-6101",
                "status": "Active",
                "data": {
                    "matched_scholarships": [
                        {"name": "Stanford Knight-Hennessy Scholars", "amount": "Full Tuition + Stipend", "deadline": "Oct 11, 2026", "fit_score": "92%"},
                        {"name": "MIT Presidential Fellowship", "amount": "$75,000/year", "deadline": "Dec 01, 2026", "fit_score": "88%"},
                        {"name": "Georgia Tech Presidential Scholarship", "amount": "$25,000/year", "deadline": "Jan 05, 2027", "fit_score": "95%"}
                    ],
                    "total_potential_value": "$350,000+",
                    "css_profile_status": "Submitted & Verified",
                    "fafsa_efc": "$18,500"
                }
            }
        ]
    },
    {
        "name": "Sterling & Blackwood Legal Partners",
        "code": "ORG7",
        "sector": "Consultancy",
        "username": "org7",
        "plan": "Enterprise",
        "status": "Active",
        "branches": [
            {"name": "Park Avenue Chambers", "address": "345 Park Avenue, 30th Floor", "phone": "+1 555-0701", "tz": "America/New_York"}
        ],
        "staff": [
            {"username": "eleanor_legal", "role": "Partner"}
        ],
        "services": [
            {"name": "M&A Due Diligence & Corporate Counsel", "category": "Corporate", "price": 850.0, "duration": 60},
            {"name": "Intellectual Property & Patent Defense", "category": "IP", "price": 700.0, "duration": 60}
        ],
        "customers": [
            {"name": "Jonathan Vance", "phone": "+1 555-7101", "email": "jvance@example.com", "gender": "Male"},
            {"name": "Nexus Ventures Group", "phone": "+1 555-7102", "email": "contact@nexusvc.com", "gender": "Corporate"}
        ],
        "appointments": [
            {"customer": "Jonathan Vance", "phone": "+1 555-7101", "service": "M&A Due Diligence & Corporate Counsel", "days_offset": 0, "status": "Booked", "payment": "Paid", "amount": 850.0},
            {"customer": "Nexus Ventures Group", "phone": "+1 555-7102", "service": "Intellectual Property & Patent Defense", "days_offset": 2, "status": "Booked", "payment": "Paid", "amount": 700.0}
        ],
        "industry_records": [
            {
                "title": "Project Apex M&A Ethical Conflict Check Clearance",
                "record_type": "conflict_clearance",
                "customer_phone": "+1 555-7101",
                "status": "Active",
                "data": {
                    "matter_code": "MAT-2026-MA-041",
                    "matter_title": "Acquisition of CloudScale Technologies Ltd",
                    "adverse_parties_queried": ["CloudScale Ltd", "Venture Partners LLC", "Apex Holdings Group"],
                    "database_search_result": "Zero adverse engagements found across 10-year historical firm registry.",
                    "ethical_wall_required": False,
                    "clearance_status": "CLEARED BY SENIOR ETHICS COMMITTEE",
                    "managing_partner": "Eleanor Sterling, Esq."
                }
            },
            {
                "title": "Corporate Retainer Depletion & Billable Ledger - Jonathan Vance",
                "record_type": "retainer_ledger",
                "customer_phone": "+1 555-7101",
                "status": "Active",
                "data": {
                    "initial_retainer_deposit": 35000.0,
                    "partner_hourly_rate": 850.0,
                    "associate_hourly_rate": 450.0,
                    "hours_billed_to_date": 18.5,
                    "current_retainer_balance": 19275.0,
                    "weekly_burn_rate": "4.2 hours / week",
                    "replenishment_threshold": 5000.0
                }
            },
            {
                "title": "Series B Stock Purchase Agreement - Redline v4.2 Privileged Docket",
                "record_type": "privileged_dossier",
                "customer_phone": "+1 555-7102",
                "status": "Active",
                "data": {
                    "document_title": "Definitive Series B Preferred Stock Purchase Agreement",
                    "privilege_designation": "ATTORNEY-CLIENT PRIVILEGED & STRICTLY CONFIDENTIAL",
                    "indemnification_cap": "Capped at 10% total transaction purchase price",
                    "escrow_holdback": "$2,400,000 USD held for 18 calendar months",
                    "rep_and_warranty_insurance": "Bound with Lloyd's Syndicate"
                }
            },
            {
                "title": "Court Filing & Discovery Milestones - Project Apex M&A",
                "record_type": "matter_milestone",
                "customer_phone": "+1 555-7101",
                "status": "Active",
                "data": {
                    "matter_code": "MAT-2026-MA-041",
                    "milestones": [
                        {"milestone": "Initial Due Diligence Request List", "deadline": "2026-09-20", "status": "Completed"},
                        {"milestone": "Virtual Data Room Population", "deadline": "2026-09-28", "status": "In Progress"},
                        {"milestone": "Definitive Agreement Signature", "deadline": "2026-10-15", "status": "Pending"},
                        {"milestone": "Regulatory Antitrust Filing (HSR)", "deadline": "2026-10-30", "status": "Pending"},
                        {"milestone": "Closing & Fund Transfer", "deadline": "2026-11-15", "status": "Pending"}
                    ],
                    "statute_of_limitations": "N/A (Transactional)",
                    "managing_attorney": "Eleanor Sterling, Esq."
                }
            }
        ]
    },
    {
        "name": "Sovereign Realty & Architectural Partners",
        "code": "ORG8",
        "sector": "Real Estate",
        "username": "org8",
        "plan": "Professional",
        "status": "Active",
        "branches": [
            {"name": "TriBeCa Penthouse Gallery", "address": "88 Franklin Street", "phone": "+1 555-0801", "tz": "America/New_York"}
        ],
        "staff": [
            {"username": "marcus_realty", "role": "Broker"}
        ],
        "services": [
            {"name": "Luxury Penthouse Private Showing", "category": "Listing", "price": 0.0, "duration": 60},
            {"name": "Architectural Design Feasibility Review", "category": "Architecture", "price": 450.0, "duration": 60}
        ],
        "customers": [
            {"name": "Lady Catherine", "phone": "+1 555-8101", "email": "catherine@example.com", "gender": "Female"},
            {"name": "Lord Sterling", "phone": "+1 555-8102", "email": "sterling.re@example.com", "gender": "Male"}
        ],
        "appointments": [
            {"customer": "Lady Catherine", "phone": "+1 555-8101", "service": "Luxury Penthouse Private Showing", "days_offset": 2, "status": "Booked", "payment": "Paid", "amount": 0.0},
            {"customer": "Lord Sterling", "phone": "+1 555-8102", "service": "Architectural Design Feasibility Review", "days_offset": -1, "status": "Completed", "payment": "Paid", "amount": 450.0}
        ],
        "industry_records": [
            {
                "title": "Bespoke TriBeCa & SoHo Penthouse VIP Showing Tour",
                "record_type": "tour_itinerary",
                "customer_phone": "+1 555-8101",
                "status": "Active",
                "data": {
                    "tour_date": "Tomorrow at 10:00 AM",
                    "client_target_budget": "$18,000,000 - $25,000,000 USD",
                    "tour_stops": [
                        {"order": 1, "address": "111 West 57th St, Penthouse 64", "time": "10:30 AM", "lockbox": "Concierge Check-in", "mls_id": "MLS# 994012", "notes": "Shoe covers mandatory. Key fob on file."},
                        {"order": 2, "address": "432 Park Avenue, Suite 78", "time": "12:15 PM", "lockbox": "Private Key Escort", "mls_id": "MLS# 994088", "notes": "Central Park panoramic views. High-speed private elevator."},
                        {"order": 3, "address": "56 Leonard Street, Penthouse 52", "time": "02:30 PM", "lockbox": "LB-4109", "mls_id": "MLS# 995123", "notes": "Cantilever terrace access with private infinity hot tub."}
                    ]
                }
            },
            {
                "title": "JPMorgan Private Bank Proof of Funds & Pre-Approval - Lady Catherine",
                "record_type": "proof_of_funds",
                "customer_phone": "+1 555-8101",
                "status": "Active",
                "data": {
                    "financial_institution": "JPMorgan Chase Private Bank",
                    "verified_liquid_funds": "$32,000,000 USD",
                    "earnest_money_deposit_capability": "Up to $3,500,000 wire within 2 business hours",
                    "validation_date": "2026-09-14",
                    "verifying_principal_broker": "Marcus Sterling (Licensed RE Broker)"
                }
            },
            {
                "title": "Commercial SoHo Mixed-Use Architectural Feasibility Study",
                "record_type": "zoning_feasibility",
                "customer_phone": "+1 555-8102",
                "status": "Completed",
                "data": {
                    "property_address": "184 Mercer Street, SoHo Historic District",
                    "acquisition_price": 14500000.0,
                    "gross_annual_rent": 1120000.0,
                    "operating_expenses": 320000.0,
                    "net_operating_income": 800000.0,
                    "projected_cap_rate": "5.52%",
                    "zoning_classification": "M1-5B (Commercial & Ground-Floor Retail Compliant)"
                }
            },
            {
                "title": "Escrow & Earnest Deposit Pipeline - Lady Catherine (111 W 57th St)",
                "record_type": "escrow_pipeline",
                "customer_phone": "+1 555-8101",
                "status": "Active",
                "data": {
                    "property_address": "111 West 57th Street, Penthouse 64",
                    "listing_price": 22500000.0,
                    "offer_price": 21800000.0,
                    "earnest_money_deposit": 2180000.0,
                    "escrow_company": "Stewart Title Guaranty Company",
                    "pipeline_stages": [
                        {"stage": "Offer Accepted", "status": "Completed", "date": "2026-09-12"},
                        {"stage": "Earnest Money Deposited", "status": "Completed", "date": "2026-09-14"},
                        {"stage": "Appraisal & Inspection", "status": "In Progress", "date": "2026-09-18"},
                        {"stage": "Title Search & Insurance", "status": "Pending", "date": None},
                        {"stage": "Closing & Key Handover", "status": "Pending", "date": None}
                    ],
                    "estimated_closing_date": "2026-10-15",
                    "mortgage_pre_approval": "Cash Purchase - No Mortgage Required"
                }
            }
        ]
    },
    {
        "name": "Vanguard Global Enterprise Solutions",
        "code": "ORG9",
        "sector": "Professional Services",
        "username": "org9",
        "plan": "Enterprise",
        "status": "Active",
        "branches": [
            {"name": "One World Trade Center HQ", "address": "285 Fulton St, Suite 75", "phone": "+1 555-0901", "tz": "America/New_York"}
        ],
        "staff": [
            {"username": "elizabeth_exec", "role": "Consultant"}
        ],
        "services": [
            {"name": "Enterprise Cloud Architecture Audit", "category": "IT", "price": 1200.0, "duration": 90},
            {"name": "AI Transformation & Workflow Blueprint", "category": "AI", "price": 1500.0, "duration": 120}
        ],
        "customers": [
            {"name": "William Sterling", "phone": "+1 555-9101", "email": "wsterling@example.com", "gender": "Male"},
            {"name": "Global Fintech Conglomerate", "phone": "+1 555-9102", "email": "cio@globalfintech.com", "gender": "Corporate"}
        ],
        "appointments": [
            {"customer": "William Sterling", "phone": "+1 555-9101", "service": "Enterprise Cloud Architecture Audit", "days_offset": 1, "status": "Booked", "payment": "Paid", "amount": 1200.0},
            {"customer": "Global Fintech Conglomerate", "phone": "+1 555-9102", "service": "AI Transformation & Workflow Blueprint", "days_offset": -1, "status": "Completed", "payment": "Paid", "amount": 1500.0}
        ],
        "industry_records": [
            {
                "title": "SOW Deliverables & Phase Gate Tracker - Hybrid Cloud Kubernetes",
                "record_type": "sow_deliverables",
                "customer_phone": "+1 555-9101",
                "status": "Active",
                "data": {
                    "sow_id": "SOW-2026-ENT-009",
                    "total_contract_value": 450000.0,
                    "current_active_phase": "Phase 2: Multi-Region Kubernetes Failover",
                    "phase_milestones": [
                        {"name": "Cloud Baseline Architecture & Threat Model", "sla_days": 30, "status": "Completed & Formally Signed Off"},
                        {"name": "Zero-Trust Service Mesh & IAM Hardening", "sla_days": 45, "status": "In Progress (85%)"},
                        {"name": "Production DR Chaos Testing & Cutover", "sla_days": 60, "status": "Scheduled for Q4"}
                    ],
                    "client_executive_lead": "William Sterling (Chief Information Officer)"
                }
            },
            {
                "title": "Multi-Region Cloud Architecture & SOC2 Type II Audit Dossier",
                "record_type": "architecture_dossier",
                "customer_phone": "+1 555-9102",
                "status": "Active",
                "data": {
                    "infrastructure_provider": "AWS + Google Cloud Hybrid Multi-Tenant",
                    "security_standards": ["SOC2 Type II", "HIPAA Omnibus", "ISO 27001", "PCI-DSS v4.0"],
                    "rto_rpo_targets": "RTO < 4 minutes, RPO < 15 seconds",
                    "automated_traffic_routing": "Cloudflare Global Anycast + AWS Route53 Failover",
                    "encryption_posture": "AES-256 at rest, TLS 1.3 in transit with Mutual TLS (mTLS)"
                }
            },
            {
                "title": "Executive Steering Committee - AI Automation Blueprint Q4",
                "record_type": "executive_briefing",
                "customer_phone": "+1 555-9101",
                "status": "Active",
                "data": {
                    "committee_attendees": ["Chief Executive Officer", "Chief Technology Officer", "Chief Risk Officer", "Lead Enterprise Architect"],
                    "consensus_decision": "Approved production rollout of generative clinical triage & WhatsApp conversational engine across 3 flagship branches.",
                    "allocated_capital_budget": "$350,000 Capex allocated for H1 implementation.",
                    "next_audit_date": "2026-10-15"
                }
            },
            {
                "title": "SLA Incident Log #INC-2026-047 - Global Fintech Conglomerate",
                "record_type": "sla_incident",
                "customer_phone": "+1 555-9102",
                "status": "Active",
                "data": {
                    "incident_id": "INC-2026-047",
                    "severity": "P2 - High",
                    "sla_target_response": "30 minutes",
                    "actual_response": "18 minutes",
                    "sla_met": True,
                    "description": "Kubernetes pod crash loop detected in us-east-1 production cluster. Auto-scaling triggered failover to eu-west-1.",
                    "root_cause": "Memory limit exceeded on data ingestion pod due to malformed CSV batch import.",
                    "resolution": "Memory limits increased to 4Gi. CSV validation pre-processor deployed. Incident resolved in 42 minutes.",
                    "escalation_tier": "Tier 2 - Senior DevOps Engineer",
                    "post_mortem_scheduled": "2026-09-19"
                }
            }
        ]
    }
]

SUBSCRIPTION_PLANS = [
    {
        "name": "Starter",
        "description": "Essential appointment scheduling for single-location clinics and studios.",
        "price": 49.0,
        "billing_cycle": "monthly",
        "feature_limits": {"branches": 1, "staff": 3, "appointments_per_month": 300, "whatsapp_integration": True}
    },
    {
        "name": "Professional",
        "description": "Robust suite with multi-branch management, advanced analytics, and custom WhatsApp automation.",
        "price": 149.0,
        "billing_cycle": "monthly",
        "feature_limits": {"branches": 5, "staff": 15, "appointments_per_month": 2500, "whatsapp_integration": True, "api_access": True}
    },
    {
        "name": "Enterprise",
        "description": "Unlimited capacity, dedicated HIPAA-compliant hosting, audit logs, and priority SLA.",
        "price": 499.0,
        "billing_cycle": "monthly",
        "feature_limits": {"branches": -1, "staff": -1, "appointments_per_month": -1, "whatsapp_integration": True, "api_access": True, "custom_domain": True}
    }
]

SECTOR_TEMPLATES = {
    "Hospital & Medical Clinic": ["Doctor Consultation", "Diagnostic Review", "Emergency Triage", "Prescription Refill"],
    "Premium Salon & Aesthetics Spa": ["Hair Styling & Cut", "Hydra-Facial", "Deep Tissue Massage", "Manicure & Pedicure"],
    "Wealth & Financial Advisory": ["Portfolio Audit", "Tax Advisory", "Wealth Management", "Retirement Planning"],
    "Life & General Insurance Agency": ["Policy Consultation", "Underwriting Review", "Claims Assistance", "Corporate Risk Audit"],
    "Luxury Retail & Personal Styling": ["VIP Fitting Session", "Runway Styling", "Bespoke Tailoring", "Personal Shopper"],
    "Academy & University Counseling": ["Admissions Strategy", "SOP Review", "Scholarship Counseling", "Mock Interview"],
    "Strategic Management & Legal Advisory": ["Corporate Counsel", "M&A Due Diligence", "IP Strategy", "Contract Review"],
    "Real Estate & Architecture Advisory": ["Penthouse Showing", "Commercial Site Tour", "Architectural Review", "Valuation Consultation"],
    "Custom Enterprise & Professional Services": ["Cloud Architecture Audit", "Security Assessment", "Digital Transformation", "Executive Briefing"]
}


def seed_all_sample_data(reset=False):
    """
    Idempotent seeding function.
    If reset=True, it clears application data tables safely without dropping alembic_version.
    """
    print("=" * 60)
    print("Starting AppointoCare Comprehensive Multi-Industry Data Migration")
    print("=" * 60)

    if reset:
        print("Reset flag detected: Safely clearing previous domain records with CASCADE...")
        table_list = [
            'payment_orders', 'provider_events', 'campaigns', 'notifications',
            'industry_records', 'message_logs', 'audit_logs',
            'appointment_transactions', 'organization_transactions',
            'appointments', 'patients', 'customers', 'services', 'branches',
            'users', 'subscriptions', 'subscription_plans', 'sector_templates',
            'organizations', 'admins'
        ]
        truncate_sql = f"TRUNCATE TABLE {', '.join(table_list)} RESTART IDENTITY CASCADE;"
        db.session.execute(db.text(truncate_sql))
        db.session.commit()
        print("âœ“ Previous domain records cleared.")

    # 1. SuperAdmin User
    admin_user = os.getenv("ADMIN_USERNAME", "superadmin")
    admin = Admin.query.filter_by(username=admin_user).first()
    if not admin:
        admin = Admin(
            username=admin_user,
            password=hash_password(DEFAULT_ADMIN_PASSWORD),
            role="SuperAdmin",
            created_at=datetime.utcnow()
        )
        db.session.add(admin)
        db.session.commit()
        print(f"âœ“ SuperAdmin created: {admin_user}")
    else:
        admin.password = hash_password(DEFAULT_ADMIN_PASSWORD)
        db.session.commit()
        print(f"âœ“ SuperAdmin verified: {admin_user}")

    # 2. Subscription Plans
    for plan_data in SUBSCRIPTION_PLANS:
        plan = SubscriptionPlan.query.filter_by(name=plan_data["name"]).first()
        if not plan:
            plan = SubscriptionPlan(
                name=plan_data["name"],
                description=plan_data["description"],
                price=plan_data["price"],
                billing_cycle=plan_data["billing_cycle"],
                feature_limits=plan_data["feature_limits"],
                is_active=True
            )
            db.session.add(plan)
        else:
            plan.price = plan_data["price"]
            plan.feature_limits = plan_data["feature_limits"]
            plan.description = plan_data["description"]
    db.session.commit()
    print("âœ“ Subscription Plans synchronized.")

    # 3. Sector Templates
    for template_name, services in SECTOR_TEMPLATES.items():
        template = SectorTemplate.query.filter_by(name=template_name).first()
        if not template:
            template = SectorTemplate(
                name=template_name,
                description=f"Standard preconfigured workflows for {template_name}",
                services=services,
                is_active=True
            )
            db.session.add(template)
        else:
            template.services = services
    db.session.commit()
    print("âœ“ Sector Templates synchronized.")

    # 4. Organizations, Branches, Staff, Services, Customers, Appointments, Industry Records
    now = datetime.utcnow()
    for org_data in SAMPLE_ORGANIZATIONS:
        org = Organization.query.filter_by(code=org_data["code"]).first()
        if not org:
            org = Organization(
                name=org_data["name"],
                code=org_data["code"],
                sector=org_data["sector"],
                username=org_data["username"],
                password=hash_password(DEFAULT_ORG_PASSWORD),
                subscription_status=org_data["status"],
                subscription_plan=org_data["plan"],
                subscription_start=now - timedelta(days=60),
                subscription_end=now + timedelta(days=300),
                next_billing_date=now + timedelta(days=30)
            )
            db.session.add(org)
            db.session.flush()
            print(f"  + Provisioned Organization: {org.name} ({org.code}) [{org.sector}]")
        else:
            org.name = org_data["name"]
            org.sector = org_data["sector"]
            org.password = hash_password(DEFAULT_ORG_PASSWORD)
            org.subscription_plan = org_data["plan"]
            org.subscription_status = org_data["status"]
            db.session.flush()

        # Organization Transaction (Subscription Invoice)
        existing_tx = OrganizationTransaction.query.filter_by(organization_id=org.id).first()
        if not existing_tx:
            plan_amt = 149.0 if org_data["plan"] == "Professional" else (499.0 if org_data["plan"] == "Enterprise" else 49.0)
            db.session.add(OrganizationTransaction(
                organization_id=org.id,
                amount=plan_amt,
                transaction_type="Subscription",
                payment_method="Card",
                invoice_id=f"INV-{org.code}-{now.strftime('%Y%m')}",
                status="Success",
                processed_by_type="Admin",
                processed_by_id=admin.id,
                remarks=f"Annual plan subscription payment for {org.name}"
            ))

        # Branches
        for branch_info in org_data["branches"]:
            branch = Branch.query.filter_by(organization_id=org.id, name=branch_info["name"]).first()
            if not branch:
                db.session.add(Branch(
                    organization_id=org.id,
                    name=branch_info["name"],
                    address=branch_info["address"],
                    phone=branch_info["phone"],
                    timezone=branch_info.get("tz", "America/New_York"),
                    is_active=True
                ))

        # Staff Users
        for staff_info in org_data["staff"]:
            staff = User.query.filter_by(organization_id=org.id, username=staff_info["username"]).first()
            if not staff:
                db.session.add(User(
                    organization_id=org.id,
                    username=staff_info["username"],
                    password=hash_password(DEFAULT_STAFF_PASSWORD),
                    role=staff_info["role"],
                    is_active=True
                ))
            else:
                staff.password = hash_password(DEFAULT_STAFF_PASSWORD)
                staff.role = staff_info["role"]
                staff.is_active = True

        # Services
        for svc_info in org_data["services"]:
            service = Service.query.filter_by(organization_id=org.id, name=svc_info["name"]).first()
            if not service:
                db.session.add(Service(
                    organization_id=org.id,
                    name=svc_info["name"],
                    category=svc_info["category"],
                    price=svc_info["price"],
                    duration_minutes=svc_info["duration"],
                    description=f"{svc_info['name']} provided by specialized professionals at {org.name}.",
                    active=True
                ))

        # Customers & Patients
        cust_map = {}
        for cust_info in org_data["customers"]:
            customer = Customer.query.filter_by(organization_id=org.id, phone=cust_info["phone"]).first()
            if not customer:
                customer = Customer(
                    organization_id=org.id,
                    name=cust_info["name"],
                    phone=cust_info["phone"],
                    email=cust_info["email"],
                    gender=cust_info["gender"],
                    source="Online Booking",
                    notes=f"Registered VIP Client with {org.name}"
                )
                db.session.add(customer)
                db.session.flush()

            patient = Patient.query.filter_by(organization_id=org.id, phone=cust_info["phone"]).first()
            if not patient:
                patient = Patient(
                    organization_id=org.id,
                    name=cust_info["name"],
                    phone=cust_info["phone"],
                    email=cust_info["email"],
                    gender=cust_info["gender"]
                )
                db.session.add(patient)
            cust_map[cust_info["phone"]] = customer.id

        db.session.flush()

        # Appointments
        appt_map = {}
        for appt_info in org_data["appointments"]:
            appt_time = (now + timedelta(days=appt_info["days_offset"])).replace(hour=10, minute=30, second=0, microsecond=0)
            existing_appt = Appointment.query.filter_by(
                organization_id=org.id,
                customer_phone=appt_info["phone"],
                status=appt_info["status"]
            ).first()

            if not existing_appt:
                appt = Appointment(
                    customer_name=appt_info["customer"],
                    customer_phone=appt_info["phone"],
                    appointment_date=appt_time,
                    status=appt_info["status"],
                    payment_status=appt_info["payment"],
                    organization_id=org.id
                )
                db.session.add(appt)
                db.session.flush()
                appt_map[appt_info["phone"]] = appt.id

                # Appointment Transaction
                if appt_info["payment"] == "Paid" and appt_info["amount"] > 0:
                    db.session.add(AppointmentTransaction(
                        appointment_id=appt.id,
                        organization_id=org.id,
                        amount=appt_info["amount"],
                        transaction_type="Payment",
                        payment_method="Card" if org.sector != "Healthcare" else "UPI",
                        transaction_reference=f"TXN-{appt.id}-{int(datetime.utcnow().timestamp())}",
                        status="Success",
                        processed_by_type="Organization",
                        processed_by_id=org.id,
                        remarks=f"Payment for {appt_info['service']}"
                    ))

                # MessageLog
                db.session.add(MessageLog(
                    organization_id=org.id,
                    recipient_number=appt_info["phone"],
                    message_type="WhatsApp",
                    message_content=f"Hello {appt_info['customer']}, your booking for {appt_info['service']} at {org.name} is confirmed for {appt_time.strftime('%b %d, %Y at %I:%M %p')}.",
                    status="Delivered",
                    sent_at=now - timedelta(hours=1),
                    related_appointment_id=appt.id
                ))
            else:
                appt_map[appt_info["phone"]] = existing_appt.id

        # Specialized Industry Records (Vault)
        for rec_info in org_data.get("industry_records", []):
            existing_rec = IndustryRecord.query.filter_by(
                organization_id=org.id,
                title=rec_info["title"]
            ).first()

            if not existing_rec:
                cust_phone = rec_info.get("customer_phone")
                c_id = cust_map.get(cust_phone)
                a_id = appt_map.get(cust_phone)

                ind_rec = IndustryRecord(
                    organization_id=org.id,
                    appointment_id=a_id,
                    customer_id=c_id,
                    sector=org.sector,
                    record_type=rec_info["record_type"],
                    title=rec_info["title"],
                    data=rec_info["data"],
                    status=rec_info.get("status", "Active"),
                    created_by_user=org_data["staff"][0]["username"] if org_data["staff"] else "staff",
                    created_at=now - timedelta(hours=4)
                )
                db.session.add(ind_rec)

        # Audit Logs for Organization
        db.session.add(AuditLog(
            organization_id=org.id,
            action="SECTOR_SUITE_INITIALIZED",
            details=f"Configured market-leading suite for {org.sector} with active add-ons",
            ip_address="127.0.0.1"
        ))

        # Organization In-App Notifications
        db.session.add(Notification(
            organization_id=org.id,
            recipient_type="organization",
            recipient_id=org.id,
            channel="in_app",
            title=f"Market-Ready {org.sector} Workspace Activated",
            message=f"Your specialized {org.sector} enterprise suite and modular SaaS add-ons are fully configured and ready for live operations.",
            status="unread",
            created_at=now - timedelta(hours=3)
        ))

        # SuperAdmin Platform Alert for this Organization
        db.session.add(Notification(
            organization_id=org.id,
            recipient_type="admin",
            recipient_id=admin.id,
            channel="in_app",
            title=f"Tenant Provisioned: {org.name} ({org.code})",
            message=f"{org.name} onboarded into {org.sector} sector cluster on {org.subscription_plan} tier.",
            status="unread",
            created_at=now - timedelta(hours=2)
        ))

        db.session.commit()

    print("=" * 60)
    print("âœ“ AppointoCare Sample Data Migration Completed Successfully!")
    print(f"  Organizations : {len(SAMPLE_ORGANIZATIONS)} Multi-Industry Tenants (ORG1 to ORG9)")
    print("  SuperAdmin    : superadmin / Admin@12345")
    print("  Org Admins    : org1..org9 / Org@12345")
    print("  Staff Users   : staff1, doc_sarah, alex_wealth, etc. / Staff@12345")
    print("=" * 60)


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        reset_requested = "--reset" in sys.argv or os.getenv("RESET_DATA", "false").lower() == "true"
        seed_all_sample_data(reset=reset_requested)
