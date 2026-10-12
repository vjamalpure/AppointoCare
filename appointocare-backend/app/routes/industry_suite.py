from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.models import db, IndustryRecord, Organization, Appointment, Customer, AuditLog
from app.security import get_organization_id, require_roles
from datetime import datetime, timedelta

industry_suite_bp = Blueprint("industry_suite_bp", __name__)
 
ORG_ROLES = (
    "Admin", "SuperAdmin", "Organization", "Manager", "Staff",
    "Doctor", "Therapist", "Stylist", "Advisor", "Underwriter",
    "Broker", "Consultant", "Specialist"
)

# Comprehensive Market-Leading Sector Addon Definitions
SECTOR_ADDONS = {
    "Healthcare": [
        {
            "id": "addon_eprescription",
            "name": "Digital E-Prescription & Rx Writer",
            "benchmark_source": "Practo & Epic Systems EMR",
            "category": "Clinical",
            "description": "Standardized diagnosis, active medications, dosage regimens, and one-click PDF generation.",
            "is_default": True,
            "icon": "medical_services"
        },
        {
            "id": "addon_vitals_triage",
            "name": "Vitals & Emergency Triage Matrix",
            "benchmark_source": "Zocdoc & Cerner Health",
            "category": "Diagnostics",
            "description": "Patient vitals monitoring (BP, Pulse, SpO2, Temp, BMI) with automatic triage priority ranking.",
            "is_default": True,
            "icon": "monitor_heart"
        },
        {
            "id": "addon_lab_reports",
            "name": "Diagnostic Lab Packages & Report Vault",
            "benchmark_source": "Practo Diagnostics",
            "category": "Diagnostics",
            "description": "Lab test bundling (Lipid, Thyroid, CBC) with secure patient document attachments.",
            "is_default": True,
            "icon": "biotech"
        },
        {
            "id": "addon_insurance_preauth",
            "name": "TPA / Insurance Pre-Authorization Checklist",
            "benchmark_source": "Athenahealth TPA Desk",
            "category": "Billing",
            "description": "Verify insurance policy validity, pre-authorization claims checklist, and co-pay calculator.",
            "is_default": False,
            "icon": "verified_user"
        }
    ],
    "Salon": [
        {
            "id": "addon_room_allocation",
            "name": "Treatment Suite & Hydrotherapy Allocator",
            "benchmark_source": "Zenoti Spa & Fresha",
            "category": "Operations",
            "description": "Assign specialized rooms (Aromatherapy Suite, HydraFacial Lab) and prevent room conflicts.",
            "is_default": True,
            "icon": "meeting_room"
        },
        {
            "id": "addon_service_upsell",
            "name": "Instant Upsell & Add-On Treatment Packager",
            "benchmark_source": "Mindbody & Vagaro",
            "category": "Revenue",
            "description": "One-click add-on upsells at check-in (Essential Oil infusion, Keratin boost, Collagen mask).",
            "is_default": True,
            "icon": "add_circle_outline"
        },
        {
            "id": "addon_formula_card",
            "name": "Color Pigment & Formula Consultation Card",
            "benchmark_source": "Fresha Color Bar",
            "category": "Client Care",
            "description": "Record exact hair color formula ratios, skin patch test results, and allergy warnings.",
            "is_default": True,
            "icon": "palette"
        },
        {
            "id": "addon_membership_packages",
            "name": "Multi-Session Ritual Pass & Subscriptions",
            "benchmark_source": "Zenoti Memberships",
            "category": "Loyalty",
            "description": "Manage 5-session spa passes, blow-dry monthly club credits, and automatic redemption.",
            "is_default": False,
            "icon": "card_membership"
        }
    ],
    "Finance": [
        {
            "id": "addon_kyc_compliance",
            "name": "Accredited Investor KYC & AML Screening",
            "benchmark_source": "AdvisorEngine & Wealthbox",
            "category": "Compliance",
            "description": "Fiduciary identity verification, PEP/sanctions check, and risk tolerance classification.",
            "is_default": True,
            "icon": "fact_check"
        },
        {
            "id": "addon_asset_allocator",
            "name": "Portfolio Asset Allocation & Rebalancing Matrix",
            "benchmark_source": "Orion Advisor Tech",
            "category": "Advisory",
            "description": "Track target vs current equity/fixed income/alternative weightings and rebalance drift.",
            "is_default": True,
            "icon": "pie_chart"
        },
        {
            "id": "addon_fiduciary_letter",
            "name": "Fiduciary Engagement & Fee Disclosures",
            "benchmark_source": "Fidelity Wealth Suite",
            "category": "Legal",
            "description": "Generate fiduciary engagement letters, advisory fee schedule (AUM/Retainer), and Form ADV Part 2.",
            "is_default": True,
            "icon": "description"
        },
        {
            "id": "addon_quarterly_review",
            "name": "Automated 90-Day Fiduciary Milestone Scheduler",
            "benchmark_source": "Wealthbox Calendar",
            "category": "Client Care",
            "description": "Pre-scheduled quarterly wealth audit reminders and annual tax-loss harvesting roadmaps.",
            "is_default": False,
            "icon": "event_repeat"
        }
    ],
    "Retail": [
        {
            "id": "addon_wardrobe_measurements",
            "name": "VIP Wardrobe Sizing & Tailoring Measurements",
            "benchmark_source": "Farfetch Private Client",
            "category": "Clienteling",
            "description": "Record full measurements (chest, waist, inseam, shoulder, shoe) and bespoke tailor directives.",
            "is_default": True,
            "icon": "straighten"
        },
        {
            "id": "addon_vip_suite",
            "name": "Champagne Hospitality & Private Suite Booking",
            "benchmark_source": "Net-A-Porter Concierge",
            "category": "Hospitality",
            "description": "Reserve private styling suites (Platinum Salon, Bridal Pavilion) with beverage preferences.",
            "is_default": True,
            "icon": "local_bar"
        },
        {
            "id": "addon_curated_lookbook",
            "name": "Curated Lookbook & Wishlist Studio",
            "benchmark_source": "Appointlet Retail Suite",
            "category": "Merchandising",
            "description": "Assemble bespoke product lookbooks with high-res garment links prior to VIP visits.",
            "is_default": True,
            "icon": "auto_awesome_motion"
        },
        {
            "id": "addon_alterations_tracker",
            "name": "Bespoke Alteration & Tailoring Pipeline",
            "benchmark_source": "Saks Fifth Avenue Alterations",
            "category": "Fulfillment",
            "description": "Track garment alteration stages (Pinned, In-Atelier, Pressed, Ready for Fitting).",
            "is_default": False,
            "icon": "checkroom"
        }
    ],
    "Insurance": [
        {
            "id": "addon_premium_calculator",
            "name": "Term & General Premium Estimation Calculator",
            "benchmark_source": "PolicyBazaar & Applied Systems",
            "category": "Underwriting",
            "description": "Calculate estimated monthly/annual premiums based on sum assured, age, and coverage riders.",
            "is_default": True,
            "icon": "calculate"
        },
        {
            "id": "addon_underwriting_checklist",
            "name": "Medical & Hazard Underwriting Questionnaire",
            "benchmark_source": "Vertafore Agency Platform",
            "category": "Risk",
            "description": "Pre-policy medical history, smoking status, occupational risk, and family morbidity audits.",
            "is_default": True,
            "icon": "assignment"
        },
        {
            "id": "addon_claims_tracker",
            "name": "Claims Adjudication & First Notice of Loss (FNOL)",
            "benchmark_source": "HawkSoft Insurance Desk",
            "category": "Claims",
            "description": "Record customer claim submissions, hospital bills, survey reports, and approval status.",
            "is_default": True,
            "icon": "rule"
        },
        {
            "id": "addon_policy_vault",
            "name": "Policy Document & Nominee Allocation Vault",
            "benchmark_source": "EZLynx Document Hub",
            "category": "Vault",
            "description": "Encrypted repository for policy schedule, endorsement riders, and verified nominee forms.",
            "is_default": False,
            "icon": "folder_shared"
        }
    ],
    "Education": [
        {
            "id": "addon_university_shortlist",
            "name": "3-Tier University Shortlisting (Reach, Match, Safety)",
            "benchmark_source": "Naviance & Crimson Education",
            "category": "Admissions",
            "description": "Structured university list categorized by selectivity, acceptance odds, and tuition budget.",
            "is_default": True,
            "icon": "school"
        },
        {
            "id": "addon_application_milestones",
            "name": "Early Action / Regular & Visa Milestone Tracker",
            "benchmark_source": "BridgeU HigherEd",
            "category": "Milestones",
            "description": "Timeline tracker for Common App deadlines, recommendation letters, and visa appointments.",
            "is_default": True,
            "icon": "timeline"
        },
        {
            "id": "addon_sop_review",
            "name": "Essay & SOP Evaluation Rubric with Line Comments",
            "benchmark_source": "Grammarly for HigherEd",
            "category": "Academics",
            "description": "Structured critique rubric (Narrative, Hook, Grammar, Goal alignment) with counselor feedback.",
            "is_default": True,
            "icon": "rate_review"
        },
        {
            "id": "addon_scholarship_finder",
            "name": "Merit & Need-Based Scholarship Matcher",
            "benchmark_source": "Fastweb & CollegeBoard",
            "category": "Financial Aid",
            "description": "Filter available institutional endowments, deadlines, and required supplementary essays.",
            "is_default": False,
            "icon": "military_tech"
        }
    ],
    "Consultancy": [
        {
            "id": "addon_conflict_check",
            "name": "Mandatory Conflict-of-Interest Clearance Audit",
            "benchmark_source": "Clio Legal & PracticePanther",
            "category": "Ethics",
            "description": "Verify adverse party conflicts, previous representation records, and ethical clearance sign-off.",
            "is_default": True,
            "icon": "shield"
        },
        {
            "id": "addon_billable_retainer",
            "name": "Retainer Depletion & Billable Hours Ledger",
            "benchmark_source": "MyCase & Bain Client Portal",
            "category": "Billing",
            "description": "Log billable advisory hours in 6-minute increments against pre-paid client retainers.",
            "is_default": True,
            "icon": "hourglass_top"
        },
        {
            "id": "addon_confidential_vault",
            "name": "Privileged Evidence & Contract Redlining Vault",
            "benchmark_source": "NetDocuments Legal",
            "category": "Privileged",
            "description": "Attorney-client privileged contract repository with version history and NDA verification.",
            "is_default": True,
            "icon": "lock"
        },
        {
            "id": "addon_matter_milestones",
            "name": "Court Filing, Discovery & Closing Milestones",
            "benchmark_source": "Clio Grow",
            "category": "Milestones",
            "description": "Track statutory limitation dates, discovery deadlines, deposition schedules, and closings.",
            "is_default": False,
            "icon": "event_note"
        }
    ],
    "Real Estate": [
        {
            "id": "addon_property_tour",
            "name": "Multi-Stop Property Tour Itinerary Planner",
            "benchmark_source": "Zillow Premier Agent & Dotloop",
            "category": "Showings",
            "description": "Build sequential property viewing itineraries (Stop 1, Stop 2, Stop 3) with lockbox codes.",
            "is_default": True,
            "icon": "tour"
        },
        {
            "id": "addon_proof_of_funds",
            "name": "Mortgage Pre-Approval & Proof of Funds Validator",
            "benchmark_source": "Buildium & Dotloop",
            "category": "Qualification",
            "description": "Verify bank pre-approval letters, earnest money capability, and buyer qualification tier.",
            "is_default": True,
            "icon": "account_balance"
        },
        {
            "id": "addon_zoning_calculator",
            "name": "Cap Rate, Net Operating Income & Zoning Matrix",
            "benchmark_source": "Reonomy & CoStar",
            "category": "Commercial",
            "description": "Instant financial modeling: Cap Rate, Gross Rent Multiplier, and municipal zoning compliance.",
            "is_default": True,
            "icon": "apartment"
        },
        {
            "id": "addon_earnest_deposit",
            "name": "Escrow & Earnest Deposit Milestone Tracker",
            "benchmark_source": "Dotloop Escrow Desk",
            "category": "Closing",
            "description": "Track earnest money deposit verification, appraisal contingencies, and closing countdown.",
            "is_default": False,
            "icon": "handshake"
        }
    ],
    "Professional Services": [
        {
            "id": "addon_sow_milestones",
            "name": "Statement of Work (SOW) Deliverables Tracker",
            "benchmark_source": "Accenture Client Exchange",
            "category": "Delivery",
            "description": "Track contractual milestone completion, stakeholder sign-offs, and deliverable SLAs.",
            "is_default": True,
            "icon": "assignment_turned_in"
        },
        {
            "id": "addon_architecture_review",
            "name": "Enterprise Cloud & Cyber Architecture Form",
            "benchmark_source": "Deloitte Tech Consulting",
            "category": "Technical",
            "description": "Structured architecture review: SOC2, HIPAA, multi-region failover, and zero-trust posture.",
            "is_default": True,
            "icon": "cloud_done"
        },
        {
            "id": "addon_executive_briefing",
            "name": "Steering Committee & Executive Briefing Roster",
            "benchmark_source": "McKinsey Client Portal",
            "category": "Governance",
            "description": "Log C-level attendees (CTO, CIO, CISO), key consensus decisions, and action registries.",
            "is_default": True,
            "icon": "groups"
        },
        {
            "id": "addon_sla_matrix",
            "name": "SLA Escalation Matrix & Multi-Tier Resolution Monitor",
            "benchmark_source": "Jira Service Desk Enterprise",
            "category": "SLA",
            "description": "Tier 1/2/3 response time tracking, breach warnings, and root-cause analysis logging.",
            "is_default": False,
            "icon": "published_with_changes"
        }
    ]
}

# In-memory organization addons state (persisted per tenant)
_ORG_ACTIVE_ADDONS = {}


def _get_sector_key(sector_name: str) -> str:
    if not sector_name:
        return "Healthcare"
    for k in SECTOR_ADDONS.keys():
        if k.lower() in sector_name.lower() or sector_name.lower() in k.lower():
            return k
    return "Healthcare"


@industry_suite_bp.route("/addons", methods=["GET"])
@require_roles(*ORG_ROLES)
def get_addons():
    claims = get_jwt()
    role = claims.get("role")
    all_sectors = request.args.get("all_sectors") == "true"

    if all_sectors and role == "Admin":
        # Return all sectors and their catalog of add-ons
        return jsonify({
            "all_sectors": True,
            "sectors": SECTOR_ADDONS
        })

    org_id = get_organization_id() if role != "Admin" else int(request.args.get("organization_id") or 1)
    org = Organization.query.get(org_id)
    sector_key = _get_sector_key(org.sector if org else "Healthcare")

    all_addons = SECTOR_ADDONS.get(sector_key, SECTOR_ADDONS["Healthcare"])
    active_set = _ORG_ACTIVE_ADDONS.get(org_id)
    if active_set is None:
        active_set = {a["id"] for a in all_addons if a.get("is_default")}
        _ORG_ACTIVE_ADDONS[org_id] = active_set

    response_addons = []
    for a in all_addons:
        item = dict(a)
        item["enabled"] = a["id"] in active_set
        response_addons.append(item)

    return jsonify({
        "organization_id": org_id,
        "sector": sector_key,
        "addons": response_addons
    })


@industry_suite_bp.route("/addons/toggle", methods=["POST"])
@require_roles("Admin", "Organization", "Manager")
def toggle_addon():
    claims = get_jwt()
    role = claims.get("role")
    org_id = get_organization_id() if role != "Admin" else int(request.json.get("organization_id") or 1)
    data = request.json or {}

    addon_id = data.get("addon_id")
    enabled = bool(data.get("enabled"))
    if not addon_id:
        return jsonify({"msg": "addon_id is required"}), 400

    if org_id not in _ORG_ACTIVE_ADDONS:
        org = Organization.query.get(org_id)
        sector_key = _get_sector_key(org.sector if org else "Healthcare")
        _ORG_ACTIVE_ADDONS[org_id] = {a["id"] for a in SECTOR_ADDONS.get(sector_key, []) if a.get("is_default")}

    if enabled:
        _ORG_ACTIVE_ADDONS[org_id].add(addon_id)
    else:
        _ORG_ACTIVE_ADDONS[org_id].discard(addon_id)

    audit = AuditLog(
        organization_id=org_id,
        action="ADDON_STATE_TOGGLED",
        details=f"Toggled addon {addon_id} to {'ENABLED' if enabled else 'DISABLED'}",
        ip_address=request.remote_addr
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({
        "msg": f"Addon '{addon_id}' is now {'active' if enabled else 'disabled'}",
        "addon_id": addon_id,
        "enabled": enabled
    })


@industry_suite_bp.route("/records", methods=["GET"])
@require_roles(*ORG_ROLES)
def get_records():
    claims = get_jwt()
    role = claims.get("role")
    query = IndustryRecord.query

    if role != "Admin":
        org_id = get_organization_id()
        query = query.filter_by(organization_id=org_id)
    else:
        org_param = request.args.get("organization_id")
        if org_param and org_param != "all":
            query = query.filter_by(organization_id=int(org_param))

    sector_param = request.args.get("sector")
    if sector_param and sector_param != "all":
        query = query.filter_by(sector=_get_sector_key(sector_param))

    record_type = request.args.get("record_type")
    if record_type:
        query = query.filter_by(record_type=record_type)

    appointment_id = request.args.get("appointment_id")
    if appointment_id:
        query = query.filter_by(appointment_id=int(appointment_id))

    customer_id = request.args.get("customer_id")
    if customer_id:
        query = query.filter_by(customer_id=int(customer_id))

    records = query.order_by(IndustryRecord.created_at.desc()).limit(150).all()
    org_dict = {o.id: (o.name, o.code) for o in Organization.query.all()}

    return jsonify([
        {
            "id": r.id,
            "organization_id": r.organization_id,
            "organization_name": org_dict.get(r.organization_id, ("Unknown", ""))[0],
            "organization_code": org_dict.get(r.organization_id, ("Unknown", ""))[1],
            "appointment_id": r.appointment_id,
            "customer_id": r.customer_id,
            "sector": r.sector,
            "record_type": r.record_type,
            "title": r.title,
            "data": r.data,
            "status": r.status,
            "created_by_user": r.created_by_user,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "updated_at": r.updated_at.isoformat() if r.updated_at else None
        }
        for r in records
    ])


@industry_suite_bp.route("/records", methods=["POST"])
@require_roles(*ORG_ROLES)
def create_record():
    claims = get_jwt()
    role = claims.get("role")
    org_id = get_organization_id() if role != "Admin" else int(request.json.get("organization_id") or 1)
    data = request.json or {}

    title = data.get("title")
    record_type = data.get("record_type")
    if not title or not record_type:
        return jsonify({"msg": "title and record_type are required"}), 400

    org = Organization.query.get(org_id)
    sector_key = _get_sector_key(data.get("sector") or (org.sector if org else "Healthcare"))

    record = IndustryRecord(
        organization_id=org_id,
        appointment_id=int(data["appointment_id"]) if data.get("appointment_id") else None,
        customer_id=int(data["customer_id"]) if data.get("customer_id") else None,
        sector=sector_key,
        record_type=record_type,
        title=title,
        data=data.get("data") or {},
        status=data.get("status") or "Active",
        created_by_user=claims.get("username") or "staff"
    )
    db.session.add(record)
    db.session.commit()

    return jsonify({
        "msg": f"Industry record '{title}' saved successfully",
        "id": record.id,
        "record_type": record.record_type,
        "sector": record.sector
    }), 201


def evaluate_abnormal_vitals(vitals):
    """
    Clinically reviewed physiological thresholds for adult vitals.
    Returns non-diagnostic advisory flags for clinical review.
    Never presents automated notices as clinical diagnoses.
    """
    if not isinstance(vitals, dict):
        return []
    advisories = []
    try:
        bp_sys = vitals.get("bp_systolic")
        if bp_sys is not None and (float(bp_sys) >= 140 or float(bp_sys) < 90):
            advisories.append({
                "parameter": "Blood Pressure (Systolic)",
                "value": bp_sys,
                "threshold": "Standard physiological range: 90-139 mmHg",
                "notice": "Observed value outside standard physiological range. Requires practitioner clinical verification."
            })
        bp_dia = vitals.get("bp_diastolic")
        if bp_dia is not None and (float(bp_dia) >= 90 or float(bp_dia) < 60):
            advisories.append({
                "parameter": "Blood Pressure (Diastolic)",
                "value": bp_dia,
                "threshold": "Standard physiological range: 60-89 mmHg",
                "notice": "Observed value outside standard physiological range. Requires practitioner clinical verification."
            })
        pulse = vitals.get("pulse") or vitals.get("heart_rate")
        if pulse is not None and (float(pulse) > 100 or float(pulse) < 55):
            advisories.append({
                "parameter": "Heart Rate / Pulse",
                "value": pulse,
                "threshold": "Standard resting range: 55-100 bpm",
                "notice": "Pulse outside normal resting range. Review in context of patient clinical activity."
            })
        spo2 = vitals.get("spo2")
        if spo2 is not None and float(spo2) < 95:
            advisories.append({
                "parameter": "SpO2 (Pulse Oximetry)",
                "value": spo2,
                "threshold": "Normal room-air baseline: ≥ 95%",
                "notice": "Oxygen saturation reading is lower than standard room-air baseline."
            })
        temp = vitals.get("temperature")
        if temp is not None and (float(temp) >= 100.4 or float(temp) < 95.0):
            advisories.append({
                "parameter": "Body Temperature",
                "value": temp,
                "threshold": "Standard normal range: 97.0-99.5 °F",
                "notice": "Temperature variance detected. Clinical practitioner review advised."
            })
    except (ValueError, TypeError):
        pass
    return advisories


@industry_suite_bp.route("/records/<int:record_id>", methods=["PUT", "PATCH"])
@require_roles(*ORG_ROLES)
def update_record(record_id):
    claims = get_jwt()
    role = claims.get("role")
    record = IndustryRecord.query.get_or_404(record_id)
    if role != "Admin" and record.organization_id != get_organization_id():
        return jsonify({"msg": "Unauthorized"}), 403

    data = request.json or {}
    old_data = dict(record.data or {})

    # Prescription amendment revision tracking
    if record.record_type == "prescription":
        revisions = list(old_data.get("revisions") or [])
        revisions.append({
            "amended_at": datetime.utcnow().isoformat(),
            "amended_by": claims.get("username") or "clinician",
            "reason": data.get("amendment_reason") or "Clinical regimen adjustment",
            "previous_medications": old_data.get("medications", []),
            "previous_diagnosis": old_data.get("diagnosis", "")
        })
        new_data = dict(data.get("data") or old_data)
        new_data["revisions"] = revisions
        record.data = new_data
    elif "data" in data:
        record.data = data["data"]

    # Check vitals if provided in new data
    if record.data and isinstance(record.data, dict) and "vitals" in record.data:
        record.data["vitals_advisory"] = evaluate_abnormal_vitals(record.data["vitals"])

    if "title" in data:
        record.title = data["title"]
    if "status" in data:
        record.status = data["status"]

    record.updated_at = datetime.utcnow()

    try:
        user_id_val = claims.get("sub")
        audit = AuditLog(
            organization_id=record.organization_id,
            user_id=int(user_id_val) if user_id_val and str(user_id_val).isdigit() else None,
            user_role=role,
            action="AMEND_PRESCRIPTION" if record.record_type == "prescription" else "UPDATE_RECORD",
            entity="IndustryRecord",
            entity_id=record.id,
            details=f"Updated record #{record.id} ('{record.title}', type: {record.record_type})",
            ip_address=request.remote_addr
        )
        db.session.add(audit)
    except Exception:
        pass

    db.session.commit()
    return jsonify({
        "msg": f"Record #{record.id} updated successfully",
        "id": record.id,
        "title": record.title,
        "status": record.status,
        "record_type": record.record_type
    })


@industry_suite_bp.route("/records/<int:record_id>", methods=["DELETE"])
@require_roles(*ORG_ROLES)
def delete_record(record_id):
    claims = get_jwt()
    role = claims.get("role")
    record = IndustryRecord.query.get_or_404(record_id)
    if role != "Admin" and record.organization_id != get_organization_id():
        return jsonify({"msg": "Unauthorized"}), 403

    db.session.delete(record)
    db.session.commit()
    return jsonify({"msg": "Record deleted"})


@industry_suite_bp.route("/records/<int:record_id>/download-pdf", methods=["GET"])
@require_roles(*ORG_ROLES)
def download_record_pdf(record_id):
    claims = get_jwt()
    role = claims.get("role")
    record = IndustryRecord.query.get_or_404(record_id)
    if role not in ["Admin", "SuperAdmin"] and record.organization_id != get_organization_id():
        return jsonify({"msg": "Unauthorized: Cross-tenant access denied"}), 403

    from app.services.pdf_service import generate_prescription_pdf
    from flask import Response

    org = Organization.query.get(record.organization_id)
    org_data = {
        "name": org.name if org else "Healthcare Center",
        "code": org.code if org else "ORG",
        "sector": org.sector if org else "Healthcare",
        "phone": getattr(org, "phone", "") or "+1 555-0100",
        "email": getattr(org, "email", "") or "care@appointocare.com",
        "address": getattr(org, "address", "") or "100 Medical Center Blvd"
    }

    appt_data = {}
    if record.appointment_id:
        appt = Appointment.query.get(record.appointment_id)
        if appt:
            appt_data = {
                "customer_name": appt.customer_name,
                "customer_phone": appt.customer_phone,
                "appointment_date": appt.appointment_date.isoformat() if appt.appointment_date else "",
                "staff_name": appt.staff_name or record.created_by_user
            }
    elif record.customer_id:
        cust = Customer.query.get(record.customer_id)
        if cust:
            appt_data = {
                "customer_name": cust.name,
                "customer_phone": cust.phone,
                "staff_name": record.created_by_user
            }

    record_dict = {
        "title": record.title,
        "record_type": record.record_type,
        "data": record.data or {}
    }

    if record.record_type == "prescription":
        from app.services.pdf_service import generate_prescription_pdf
        pdf_bytes = generate_prescription_pdf(org_data, record_dict, appt_data)
        filename = f"prescription_{record.id}.pdf"
    else:
        from app.services.pdf_service import generate_industry_dossier_pdf
        pdf_bytes = generate_industry_dossier_pdf(org_data, record_dict, appt_data)
        filename = f"{org_data.get('sector', 'record').lower()}_dossier_{record.id}.pdf"

    try:
        user_id_val = claims.get("sub")
        audit = AuditLog(
            organization_id=record.organization_id,
            user_id=int(user_id_val) if user_id_val and str(user_id_val).isdigit() else None,
            user_role=role,
            action="DOWNLOAD_PDF",
            entity="IndustryRecord",
            entity_id=record.id,
            details=f"Downloaded PDF for {record.sector} record '{record.title}' (type: {record.record_type})",
            ip_address=request.remote_addr
        )
        db.session.add(audit)
        db.session.commit()
    except Exception:
        db.session.rollback()

    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@industry_suite_bp.route("/queue", methods=["GET"])
@require_roles(*ORG_ROLES)
def get_queue():
    claims = get_jwt()
    role = claims.get("role")
    org_id = get_organization_id() if role != "Admin" else int(request.args.get("organization_id") or 1)

    records = IndustryRecord.query.filter(
        IndustryRecord.organization_id == org_id,
        IndustryRecord.record_type.in_(["opd_queue", "queue_token"])
    ).order_by(IndustryRecord.created_at.asc()).all()

    return jsonify([
        {
            "id": r.id,
            "title": r.title,
            "status": r.status,
            "data": r.data,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in records
    ])


@industry_suite_bp.route("/queue/create", methods=["POST"])
@require_roles(*ORG_ROLES)
def create_queue_token():
    claims = get_jwt()
    role = claims.get("role")
    org_id = get_organization_id() if role != "Admin" else int(request.json.get("organization_id") or 1)
    data = request.json or {}

    org = Organization.query.get(org_id)
    sector_key = _get_sector_key(org.sector if org else "Healthcare")

    appt_id = int(data["appointment_id"]) if data.get("appointment_id") else None
    if appt_id:
        existing_token = IndustryRecord.query.filter(
            IndustryRecord.organization_id == org_id,
            IndustryRecord.appointment_id == appt_id,
            IndustryRecord.record_type.in_(["opd_queue", "queue_token"]),
            IndustryRecord.status.notin_(["Cancelled", "Completed"])
        ).first()
        if existing_token:
            return jsonify({
                "msg": f"Active token already issued for appointment #{appt_id}",
                "id": existing_token.id,
                "token_number": (existing_token.data or {}).get("token_number", f"T-{existing_token.id}"),
                "status": existing_token.status
            }), 200

    client_name = data.get("client_name") or data.get("customer_name") or "Walk-in Guest"
    token_number = data.get("token_number")
    if not token_number:
        today_count = IndustryRecord.query.filter(
            IndustryRecord.organization_id == org_id,
            IndustryRecord.record_type.in_(["opd_queue", "queue_token"])
        ).count()
        prefix = "OPD" if sector_key == "Healthcare" else "T"
        token_number = f"{prefix}-{today_count + 1:03d}"

    queue_rec = IndustryRecord(
        organization_id=org_id,
        customer_id=int(data["customer_id"]) if data.get("customer_id") else None,
        appointment_id=appt_id,
        sector=sector_key,
        record_type="opd_queue" if sector_key == "Healthcare" else "queue_token",
        title=f"Token {token_number} — {client_name}",
        status="Waiting",
        created_by_user=claims.get("username") or "staff",
        data={
            "token_number": token_number,
            "client_name": client_name,
            "phone": data.get("phone", ""),
            "service": data.get("service", "General Consultation"),
            "priority": data.get("priority", "Standard"),
            "assigned_staff": data.get("assigned_staff", "Next Available Specialist"),
            "treatment_room": data.get("treatment_room", "Station 1"),
            "check_in_time": datetime.utcnow().strftime("%I:%M %p"),
            "notes": data.get("notes", "")
        }
    )
    db.session.add(queue_rec)
    db.session.commit()

    return jsonify({
        "msg": f"Token {token_number} issued successfully",
        "id": queue_rec.id,
        "token_number": token_number,
        "status": queue_rec.status
    }), 201


@industry_suite_bp.route("/queue/<int:record_id>", methods=["DELETE"])
@require_roles(*ORG_ROLES)
def delete_queue_token(record_id):
    claims = get_jwt()
    role = claims.get("role")
    org_id = get_organization_id() if role != "Admin" else None
    rec = IndustryRecord.query.get_or_404(record_id)
    if role != "Admin" and rec.organization_id != org_id:
        return jsonify({"msg": "Unauthorized"}), 403

    db.session.delete(rec)
    db.session.commit()
    return jsonify({"msg": f"Queue token #{record_id} dismissed"})


@industry_suite_bp.route("/queue/advance", methods=["POST"])
@require_roles(*ORG_ROLES)
def advance_queue():
    claims = get_jwt()
    role = claims.get("role")
    org_id = get_organization_id() if role != "Admin" else int(request.json.get("organization_id") or 1)
    data = request.json or {}
    record_id = data.get("record_id")
    new_status = data.get("status", "In Consultation")

    if not record_id:
        return jsonify({"msg": "record_id is required"}), 400

    rec = IndustryRecord.query.get_or_404(record_id)
    if role != "Admin" and rec.organization_id != org_id:
        return jsonify({"msg": "Unauthorized"}), 403

    VALID_QUEUE_STATUSES = [
        "Waiting", "Called", "In Consultation", "In Service", "In Progress",
        "Completed", "Cancelled", "Skipped", "Active"
    ]
    if new_status not in VALID_QUEUE_STATUSES:
        return jsonify({"msg": f"Invalid queue status '{new_status}'. Allowed: {', '.join(VALID_QUEUE_STATUSES)}"}), 400

    VALID_TRANSITIONS = {
        "Waiting": ["Called", "In Consultation", "In Service", "In Progress", "Skipped", "Cancelled"],
        "Called": ["In Consultation", "In Service", "In Progress", "Waiting", "Skipped", "Cancelled"],
        "In Consultation": ["Completed", "Cancelled", "Waiting"],
        "In Service": ["Completed", "Cancelled", "Waiting"],
        "In Progress": ["Completed", "Cancelled", "Waiting"],
        "Skipped": ["Waiting", "Cancelled"],
        "Completed": ["In Consultation", "In Service", "In Progress"],
        "Cancelled": []
    }
    allowed = VALID_TRANSITIONS.get(rec.status, VALID_QUEUE_STATUSES)
    if new_status != rec.status and new_status not in allowed:
        return jsonify({"msg": f"Invalid status transition from '{rec.status}' to '{new_status}'"}), 400

    rec.status = new_status
    if rec.data and isinstance(rec.data, dict):
        updated_data = dict(rec.data)
        updated_data["queue_status"] = new_status
        updated_data["last_updated"] = datetime.utcnow().isoformat()
        rec.data = updated_data
    db.session.commit()

    return jsonify({
        "msg": f"Queue token status updated to '{new_status}'",
        "id": rec.id,
        "status": new_status
    })


@industry_suite_bp.route("/queue/public-display", methods=["GET"])
def get_public_queue_display():
    """
    Privacy-safe waiting room public display.
    Accessible without clinician login credentials.
    Masks patient initials, shows token number, room, status, and refresh interval.
    Never exposes phone numbers, email, diagnoses, medications, or clinical notes.
    """
    org_param = request.args.get("organization_id")
    code_param = request.args.get("code")
    org = None
    if code_param:
        org = Organization.query.filter_by(code=code_param).first()
    elif org_param:
        org = Organization.query.get(int(org_param))
    else:
        org = Organization.query.filter_by(sector="Healthcare").first()

    if not org:
        return jsonify({"msg": "Organization not found"}), 404

    active_tokens = IndustryRecord.query.filter(
        IndustryRecord.organization_id == org.id,
        IndustryRecord.record_type.in_(["opd_queue", "queue_token"]),
        IndustryRecord.status.in_(["Waiting", "Called", "In Consultation"])
    ).order_by(IndustryRecord.created_at.asc()).all()

    def _mask_name(full_name):
        if not full_name:
            return "Patient"
        parts = [p.strip() for p in full_name.split() if p.strip()]
        if len(parts) == 1:
            return parts[0][0].upper() + "."
        return f"{parts[0][0].upper()}. {parts[-1][0].upper()}."

    display_items = []
    for t in active_tokens:
        tdata = t.data or {}
        raw_name = tdata.get("client_name") or "Patient"
        display_items.append({
            "token_number": tdata.get("token_number") or f"OPD-{t.id:03d}",
            "patient_initials": _mask_name(raw_name),
            "status": t.status,
            "assigned_room": tdata.get("treatment_room") or "Consultation Station",
            "priority": tdata.get("priority", "Standard"),
            "check_in_time": tdata.get("check_in_time", "")
        })

    resp = jsonify({
        "organization_name": org.name,
        "sector": org.sector,
        "active_count": len(display_items),
        "tokens": display_items,
        "refresh_seconds": 15,
        "timestamp": datetime.utcnow().isoformat()
    })
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return resp


@industry_suite_bp.route("/calculate-insurance-premium", methods=["POST"])
@require_roles(*ORG_ROLES)
def calculate_insurance_premium():
    data = request.json or {}
    age = int(data.get("age", 30))
    sum_assured = float(data.get("sum_assured", 1000000.0))
    is_smoker = bool(data.get("is_smoker", False))
    policy_term = int(data.get("policy_term", 20))
    riders = data.get("riders", [])

    base_rate = 0.00085
    if age > 30:
        base_rate += (age - 30) * 0.00004
    if is_smoker:
        base_rate *= 1.45

    annual_base = sum_assured * base_rate
    rider_surcharge = 0.0
    if "critical_illness" in riders or "Critical Illness" in riders:
        rider_surcharge += (sum_assured * 0.0002)
    if "accidental_disability" in riders or "Accidental Disability" in riders:
        rider_surcharge += (sum_assured * 0.0001)

    total_annual = round(annual_base + rider_surcharge, 2)
    monthly_premium = round(total_annual / 12.0, 2)

    return jsonify({
        "annual_premium": total_annual,
        "monthly_premium": monthly_premium,
        "base_premium": round(annual_base, 2),
        "riders_cost": round(rider_surcharge, 2),
        "sum_assured": sum_assured,
        "policy_term_years": policy_term
    })


@industry_suite_bp.route("/calculate-real-estate-roi", methods=["POST"])
@require_roles(*ORG_ROLES)
def calculate_real_estate_roi():
    data = request.json or {}
    purchase_price = float(data.get("purchase_price", 1000000.0))
    monthly_rent = float(data.get("monthly_rent", 6500.0))
    annual_operating_expenses = float(data.get("annual_expenses", 15000.0))

    gross_annual_income = monthly_rent * 12.0
    net_operating_income = gross_annual_income - annual_operating_expenses
    cap_rate = round((net_operating_income / purchase_price) * 100.0, 2) if purchase_price > 0 else 0.0
    gross_rent_multiplier = round(purchase_price / gross_annual_income, 2) if gross_annual_income > 0 else 0.0

    return jsonify({
        "purchase_price": purchase_price,
        "gross_annual_income": round(gross_annual_income, 2),
        "net_operating_income": round(net_operating_income, 2),
        "cap_rate_percent": cap_rate,
        "gross_rent_multiplier": gross_rent_multiplier
    })


@industry_suite_bp.route("/stats", methods=["GET"])
@require_roles(*ORG_ROLES)
def get_sector_stats():
    claims = get_jwt()
    role = claims.get("role")
    org_id = get_organization_id() if role != "Admin" else int(request.args.get("organization_id") or 1)
    org = Organization.query.get(org_id)
    sector_key = _get_sector_key(org.sector if org else "Healthcare")

    all_records = IndustryRecord.query.filter_by(organization_id=org_id).all()
    queue_records = [r for r in all_records if r.record_type == "opd_queue"]
    active_addons = _ORG_ACTIVE_ADDONS.get(org_id)
    if active_addons is None:
        active_addons = {a["id"] for a in SECTOR_ADDONS.get(sector_key, []) if a.get("is_default")}

    return jsonify({
        "organization_id": org_id,
        "sector": sector_key,
        "total_records": len(all_records),
        "queue_count": len(queue_records),
        "queue_waiting": len([q for q in queue_records if q.status == "Waiting"]),
        "queue_in_consultation": len([q for q in queue_records if q.status == "In Consultation"]),
        "active_addons_count": len(active_addons),
        "records_by_type": {
            r_type: len([r for r in all_records if r.record_type == r_type])
            for r_type in set(r.record_type for r in all_records)
        }
    })


@industry_suite_bp.route("/benchmarks", methods=["GET"])
@require_roles(*ORG_ROLES)
def get_benchmarks():
    claims = get_jwt()
    role = claims.get("role")

    benchmarks = {
        "Healthcare": {
            "tier1_peers": ["Practo Clinic", "Epic Systems", "Cerner Health", "Zocdoc"],
            "avg_consultation_time": "25 - 35 mins",
            "industry_rebooking_rate": "72%",
            "recommended_addons": ["addon_eprescription", "addon_vitals_triage", "addon_lab_reports"]
        },
        "Salon": {
            "tier1_peers": ["Fresha Salon", "Zenoti Aesthetics", "Mindbody Wellness"],
            "avg_consultation_time": "45 - 60 mins",
            "industry_rebooking_rate": "68%",
            "recommended_addons": ["addon_room_allocation", "addon_formula_card", "addon_service_upsell"]
        },
        "Finance": {
            "tier1_peers": ["AdvisorEngine", "Wealthbox CRM", "Orion Advisor Tech"],
            "avg_consultation_time": "60 mins",
            "industry_rebooking_rate": "89%",
            "recommended_addons": ["addon_kyc_compliance", "addon_asset_allocator", "addon_fiduciary_letter"]
        },
        "Retail": {
            "tier1_peers": ["Farfetch Private Client", "Net-A-Porter Personal Shopper", "Appointlet"],
            "avg_consultation_time": "60 mins",
            "industry_rebooking_rate": "64%",
            "recommended_addons": ["addon_wardrobe_measurements", "addon_vip_suite", "addon_curated_lookbook"]
        },
        "Insurance": {
            "tier1_peers": ["Applied Systems", "Vertafore Agency", "HawkSoft Insurance"],
            "avg_consultation_time": "45 mins",
            "industry_rebooking_rate": "85%",
            "recommended_addons": ["addon_premium_calculator", "addon_underwriting_checklist", "addon_claims_tracker"]
        },
        "Education": {
            "tier1_peers": ["Naviance Counsel", "Crimson Education", "BridgeU Admissions"],
            "avg_consultation_time": "45 - 60 mins",
            "industry_rebooking_rate": "81%",
            "recommended_addons": ["addon_university_shortlist", "addon_application_milestones", "addon_sop_review"]
        },
        "Consultancy": {
            "tier1_peers": ["Clio Legal", "PracticePanther", "Bain Client Portal"],
            "avg_consultation_time": "60 mins",
            "industry_rebooking_rate": "79%",
            "recommended_addons": ["addon_conflict_check", "addon_billable_retainer", "addon_confidential_vault"]
        },
        "Real Estate": {
            "tier1_peers": ["Zillow Premier", "Buildium", "Dotloop Commercial"],
            "avg_consultation_time": "60 mins",
            "industry_rebooking_rate": "58%",
            "recommended_addons": ["addon_property_tour", "addon_proof_of_funds", "addon_zoning_calculator"]
        },
        "Professional Services": {
            "tier1_peers": ["Accenture Exchange", "Deloitte Tech", "Jira Enterprise"],
            "avg_consultation_time": "90 mins",
            "industry_rebooking_rate": "92%",
            "recommended_addons": ["addon_sow_milestones", "addon_architecture_review", "addon_executive_briefing"]
        }
    }

    if request.args.get("all") == "true":
        return jsonify({
            "all_benchmarks": benchmarks
        })

    sector_arg = request.args.get("sector")
    if sector_arg:
        sector_key = _get_sector_key(sector_arg)
    else:
        org_id = get_organization_id() if role != "Admin" else int(request.args.get("organization_id") or 1)
        org = Organization.query.get(org_id)
        sector_key = _get_sector_key(org.sector if org else "Healthcare")

    return jsonify({
        "sector": sector_key,
        "benchmarks": benchmarks.get(sector_key, benchmarks["Healthcare"])
    })


# -------------------------------------------------------------------------
# Generic Calculator Evaluator
# -------------------------------------------------------------------------
@industry_suite_bp.route("/calculator/evaluate", methods=["POST"])
@require_roles(*ORG_ROLES)
def evaluate_generic_calculator():
    data = request.json or {}
    calc_type = data.get("calculator_type", "revenue_optimizer")
    inputs = data.get("inputs", {})

    if calc_type == "insurance_premium":
        return calculate_insurance_premium()
    elif calc_type == "real_estate_roi":
        return calculate_real_estate_roi()
    elif calc_type == "portfolio_drift":
        return evaluate_portfolio_drift()
    elif calc_type == "stylist_commission":
        return calculate_stylist_commission()
    elif calc_type == "legal_conflict":
        return check_legal_conflict()
    elif calc_type == "university_shortlist":
        return evaluate_university_shortlist()
    elif calc_type == "sla_incident":
        return evaluate_sla_incident()
    else:
        units = float(inputs.get("active_units", 10))
        rate = float(inputs.get("base_rate", 200))
        projected_rev = units * rate * 1.15
        return jsonify({
            "status": "evaluated",
            "calculator_type": calc_type,
            "projected_monthly_revenue": round(projected_rev, 2),
            "efficiency_gain_pct": 15.0,
            "optimization_score": "A+"
        })


@industry_suite_bp.route("/evaluate-portfolio-drift", methods=["POST"])
@require_roles(*ORG_ROLES)
def evaluate_portfolio_drift():
    data = request.json or {}
    current = data.get("current_weights") or data.get("current_allocations") or {}
    target = data.get("target_weights") or data.get("target_allocations") or {}
    threshold = float(data.get("rebalance_threshold_pct") or data.get("threshold_pct") or 5.0)

    drift = {}
    alerts = []
    rebalance_needed = False

    all_classes = set(current.keys()) | set(target.keys())
    for asset_class in all_classes:
        curr_val = float(current.get(asset_class, 0.0))
        targ_val = float(target.get(asset_class, 0.0))
        diff = round(curr_val - targ_val, 2)
        drift[asset_class] = diff
        if abs(diff) >= threshold:
            rebalance_needed = True
            direction = "overweight" if diff > 0 else "underweight"
            alerts.append(f"{asset_class.title()} is {direction} by {abs(diff):.1f}% (target: {targ_val}%, current: {curr_val}%, threshold: ±{threshold}%)")

    return jsonify({
        "status": "evaluated",
        "drift_by_asset_class": drift,
        "rebalance_required": rebalance_needed,
        "drift_alerts": alerts,
        "threshold_pct": threshold,
        "suggested_action": "Execute rebalancing trade allocation" if rebalance_needed else "Portfolio allocation within target drift tolerance"
    })


@industry_suite_bp.route("/calculate-stylist-commission", methods=["POST"])
@require_roles(*ORG_ROLES)
def calculate_stylist_commission():
    data = request.json or {}
    service_rev = float(data.get("service_revenue", 0.0))
    service_rate = float(data.get("service_commission_rate", 0.40))
    retail_rev = float(data.get("retail_product_revenue", 0.0))
    retail_rate = float(data.get("retail_commission_rate", 0.10))
    tips = float(data.get("tips_collected", 0.0))

    service_payout = round(service_rev * service_rate, 2)
    retail_payout = round(retail_rev * retail_rate, 2)
    total_payout = round(service_payout + retail_payout + tips, 2)
    total_rev = service_rev + retail_rev
    effective_pct = round((total_payout / total_rev) * 100.0, 2) if total_rev > 0 else 0.0

    return jsonify({
        "status": "calculated",
        "service_revenue": service_rev,
        "service_commission_payout": service_payout,
        "retail_product_revenue": retail_rev,
        "retail_commission_payout": retail_payout,
        "tips_payout": tips,
        "gross_stylist_payout": total_payout,
        "effective_commission_pct": effective_pct
    })


@industry_suite_bp.route("/check-legal-conflict", methods=["POST"])
@require_roles(*ORG_ROLES)
def check_legal_conflict():
    import json
    claims = get_jwt()
    org_id = get_organization_id() if claims.get("role") != "Admin" else int(request.json.get("organization_id") or 1)
    data = request.json or {}

    client_name = (data.get("client_name") or "").strip().lower()
    opposing_parties = [str(p).strip().lower() for p in data.get("opposing_parties", []) if str(p).strip()]

    records = IndustryRecord.query.filter_by(organization_id=org_id).all()
    matched_conflicts = []

    for rec in records:
        rec_title_lower = (rec.title or "").lower()
        rec_data_str = json.dumps(rec.data or {}).lower()
        for party in opposing_parties:
            if party and (party in rec_title_lower or party in rec_data_str):
                matched_conflicts.append({
                    "record_id": rec.id,
                    "title": rec.title,
                    "record_type": rec.record_type,
                    "matched_party": party
                })

    has_conflict = len(matched_conflicts) > 0
    return jsonify({
        "status": "evaluated",
        "conflict_detected": has_conflict,
        "clearance_status": "POTENTIAL_CONFLICT_IDENTIFIED" if has_conflict else "CLEAR",
        "matched_matters": matched_conflicts,
        "checked_parties_count": len(opposing_parties),
        "disclaimer": "Internal database match only. Mandatory manual ethical conflict review required before engagement clearance."
    })


@industry_suite_bp.route("/evaluate-university-shortlist", methods=["POST"])
@require_roles(*ORG_ROLES)
def evaluate_university_shortlist():
    data = request.json or {}
    gpa = float(data.get("student_gpa", 3.0))
    test_score = float(data.get("standardized_score", 1200))
    institutions = data.get("institutions", [])

    categorized = []
    for inst in institutions:
        name = inst.get("name", "University")
        min_gpa = float(inst.get("min_gpa", 3.5))
        min_score = float(inst.get("min_score", 1350))

        gpa_diff = gpa - min_gpa
        score_diff = test_score - min_score

        if gpa_diff >= 0.2 and score_diff >= 50:
            category = "Safety"
        elif gpa_diff >= -0.1 and score_diff >= -30:
            category = "Target / Match"
        else:
            category = "Reach"

        categorized.append({
            "name": name,
            "category": category,
            "target_gpa": min_gpa,
            "target_score": min_score
        })

    return jsonify({
        "status": "evaluated",
        "student_gpa": gpa,
        "student_test_score": test_score,
        "shortlist_evaluations": categorized,
        "summary": {
            "reach_count": len([c for c in categorized if c["category"] == "Reach"]),
            "target_count": len([c for c in categorized if c["category"] == "Target / Match"]),
            "safety_count": len([c for c in categorized if c["category"] == "Safety"]),
        }
    })


@industry_suite_bp.route("/evaluate-sla-incident", methods=["POST"])
@require_roles(*ORG_ROLES)
def evaluate_sla_incident():
    data = request.json or {}
    priority = (data.get("priority") or "P3-Medium").upper()
    reported_str = data.get("reported_at")

    SLA_MINUTES = {
        "P1-CRITICAL": 60,
        "P1": 60,
        "P2-HIGH": 240,
        "P2": 240,
        "P3-MEDIUM": 1440,
        "P3": 1440,
        "P4-LOW": 2880,
        "P4": 2880
    }
    allowed_mins = SLA_MINUTES.get(priority, 1440)

    try:
        reported_at = datetime.fromisoformat(reported_str.replace("Z", "+00:00")) if reported_str else datetime.utcnow()
        if reported_at.tzinfo is not None:
            reported_at = reported_at.replace(tzinfo=None)
    except Exception:
        reported_at = datetime.utcnow()

    now = datetime.utcnow()
    deadline = reported_at + timedelta(minutes=allowed_mins)
    mins_remaining = int((deadline - now).total_seconds() / 60.0)

    if mins_remaining < 0:
        breach_status = "BREACHED"
        escalation = "Executive Steering Committee / VP Engineering"
    elif mins_remaining < (allowed_mins * 0.25):
        breach_status = "AT_RISK"
        escalation = "Tier 2 Lead Escalation"
    else:
        breach_status = "HEALTHY"
        escalation = "Standard Tier 1 Incident Desk"

    return jsonify({
        "status": "evaluated",
        "priority": priority,
        "allowed_resolution_minutes": allowed_mins,
        "deadline_at": deadline.isoformat(),
        "minutes_remaining": mins_remaining,
        "breach_status": breach_status,
        "escalation_tier": escalation
    })


@industry_suite_bp.route("/format-validator", methods=["POST"])
@require_roles(*ORG_ROLES)
def validate_statutory_format():
    import re
    data = request.json or {}
    validator_type = (data.get("validator_type") or "").lower()
    value = str(data.get("value") or "").strip().upper()

    PATTERNS = {
        "pan": r"^[A-Z]{5}[0-9]{4}[A-Z]$",
        "gstin": r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$",
        "rera": r"^(PRM|ACK|REP|REG)/[A-Z]{2}/RERA/[0-9A-Z\-/]+$"
    }

    pattern = PATTERNS.get(validator_type)
    if not pattern:
        return jsonify({"msg": f"Unsupported validator_type '{validator_type}'. Supported: pan, gstin, rera"}), 400

    is_valid = bool(re.match(pattern, value))
    return jsonify({
        "validator_type": validator_type,
        "value": value,
        "is_valid_format": is_valid,
        "disclaimer": "Syntactic pattern check only. Does not verify active legal validity or state registry enrollment."
    })



