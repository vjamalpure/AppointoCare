from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.models import (
    db, CustomFieldDefinition, WorkflowDefinition, WorkflowTransitionHistory,
    IndustryRecord, Organization, AuditLog, Notification
)
from app.security import get_organization_id, require_roles
from datetime import datetime

workflows_bp = Blueprint("workflows_bp", __name__)
custom_fields_bp = Blueprint("custom_fields_bp", __name__)

ORG_ROLES = (
    "Admin", "SuperAdmin", "Organization", "Manager", "Staff",
    "Doctor", "Therapist", "Stylist", "Advisor", "Underwriter",
    "Broker", "Consultant", "Specialist"
)

# Standard Default Industry Workflow Definitions
DEFAULT_WORKFLOWS = {
    "Healthcare": {
        "name": "Clinical Patient Encounter Workflow",
        "initial_status": "Triage_Pending",
        "statuses": [
            {"id": "Triage_Pending", "label": "Triage Pending", "color": "#f59e0b", "sla_hours": 1},
            {"id": "In_Consultation", "label": "In Consultation", "color": "#3b82f6", "sla_hours": 2},
            {"id": "Rx_Issued", "label": "Prescription Issued", "color": "#10b981", "sla_hours": 4},
            {"id": "Followup_Scheduled", "label": "Follow-up Scheduled", "color": "#8b5cf6", "sla_hours": 24},
            {"id": "Encounter_Closed", "label": "Encounter Closed", "color": "#64748b", "sla_hours": 48}
        ],
        "transitions": [
            {"from": "Triage_Pending", "to": "In_Consultation", "label": "Begin Consultation", "required_role": "Doctor", "required_fields": ["triage_priority"]},
            {"from": "In_Consultation", "to": "Rx_Issued", "label": "Finalize Prescription", "required_role": "Doctor", "required_fields": ["diagnosis"]},
            {"from": "Rx_Issued", "to": "Followup_Scheduled", "label": "Schedule Follow-up", "required_role": "Staff", "required_fields": []},
            {"from": "Rx_Issued", "to": "Encounter_Closed", "label": "Close Encounter", "required_role": "Doctor", "required_fields": []},
            {"from": "Followup_Scheduled", "to": "Encounter_Closed", "label": "Complete Care Journey", "required_role": "Staff", "required_fields": []}
        ]
    },
    "Salon": {
        "name": "Spa & Salon Client Treatment Lifecycle",
        "initial_status": "Checked_In",
        "statuses": [
            {"id": "Checked_In", "label": "Checked In", "color": "#f59e0b", "sla_hours": 1},
            {"id": "Consultation", "label": "Color/Skin Consult", "color": "#ec4899", "sla_hours": 1},
            {"id": "In_Service", "label": "In Treatment", "color": "#3b82f6", "sla_hours": 3},
            {"id": "Completed", "label": "Service Completed", "color": "#10b981", "sla_hours": 4},
            {"id": "Paid_Closed", "label": "Billed & Closed", "color": "#64748b", "sla_hours": 24}
        ],
        "transitions": [
            {"from": "Checked_In", "to": "Consultation", "label": "Start Consultation", "required_role": "Stylist", "required_fields": []},
            {"from": "Consultation", "to": "In_Service", "label": "Commence Treatment", "required_role": "Therapist", "required_fields": []},
            {"from": "In_Service", "to": "Completed", "label": "Mark Completed", "required_role": "Staff", "required_fields": []},
            {"from": "Completed", "to": "Paid_Closed", "label": "Redeem & Settle Bill", "required_role": "Staff", "required_fields": []}
        ]
    },
    "Finance": {
        "name": "Wealth Management Advisory & Rebalance Workflow",
        "initial_status": "KYC_Pending",
        "statuses": [
            {"id": "KYC_Pending", "label": "KYC & AML Screening", "color": "#f59e0b", "sla_hours": 24},
            {"id": "Risk_Assessed", "label": "Risk Profile Approved", "color": "#3b82f6", "sla_hours": 48},
            {"id": "Proposal_Generated", "label": "Rebalance Plan Ready", "color": "#8b5cf6", "sla_hours": 72},
            {"id": "Client_Signed", "label": "Client Disclosures Signed", "color": "#10b981", "sla_hours": 96},
            {"id": "Execution_Complete", "label": "Portfolio Allocated", "color": "#64748b", "sla_hours": 120}
        ],
        "transitions": [
            {"from": "KYC_Pending", "to": "Risk_Assessed", "label": "Approve Risk Profile", "required_role": "Advisor", "required_fields": ["risk_score"]},
            {"from": "Risk_Assessed", "to": "Proposal_Generated", "label": "Draft Rebalance Plan", "required_role": "Advisor", "required_fields": []},
            {"from": "Proposal_Generated", "to": "Client_Signed", "label": "Record Client Consent", "required_role": "Staff", "required_fields": []},
            {"from": "Client_Signed", "to": "Execution_Complete", "label": "Execute Orders", "required_role": "Advisor", "required_fields": []}
        ]
    },
    "Insurance": {
        "name": "Underwriting & Claim Settlement Lifecycle",
        "initial_status": "Claim_Filed",
        "statuses": [
            {"id": "Claim_Filed", "label": "Claim Filed", "color": "#f59e0b", "sla_hours": 24},
            {"id": "Under_Review", "label": "Under Review", "color": "#3b82f6", "sla_hours": 48},
            {"id": "Documents_Verified", "label": "Docs Verified", "color": "#8b5cf6", "sla_hours": 72},
            {"id": "Settlement_Approved", "label": "Settlement Approved", "color": "#10b981", "sla_hours": 96},
            {"id": "Claim_Closed", "label": "Settled & Discharged", "color": "#64748b", "sla_hours": 120}
        ],
        "transitions": [
            {"from": "Claim_Filed", "to": "Under_Review", "label": "Assign Adjuster", "required_role": "Underwriter", "required_fields": []},
            {"from": "Under_Review", "to": "Documents_Verified", "label": "Verify Police/Medical Docs", "required_role": "Underwriter", "required_fields": []},
            {"from": "Documents_Verified", "to": "Settlement_Approved", "label": "Approve Payout", "required_role": "Underwriter", "required_fields": ["approved_amount"]},
            {"from": "Settlement_Approved", "to": "Claim_Closed", "label": "Discharge Payout", "required_role": "Staff", "required_fields": []}
        ]
    },
    "Retail": {
        "name": "Bespoke Garment Alteration & Order Pipeline",
        "initial_status": "Fitting_Measurement",
        "statuses": [
            {"id": "Fitting_Measurement", "label": "Fitting & Measurement", "color": "#f59e0b", "sla_hours": 24},
            {"id": "Cutting_Fabric", "label": "Cutting & Prep", "color": "#3b82f6", "sla_hours": 48},
            {"id": "In_Stitching", "label": "Master Stitching", "color": "#ec4899", "sla_hours": 72},
            {"id": "Quality_Check", "label": "QA Inspection", "color": "#8b5cf6", "sla_hours": 96},
            {"id": "Ready_For_Pickup", "label": "Ready for Pickup", "color": "#10b981", "sla_hours": 120},
            {"id": "Delivered", "label": "Client Collected", "color": "#64748b", "sla_hours": 144}
        ],
        "transitions": [
            {"from": "Fitting_Measurement", "to": "Cutting_Fabric", "label": "Send to Workshop", "required_role": "Staff", "required_fields": []},
            {"from": "Cutting_Fabric", "to": "In_Stitching", "label": "Begin Tailoring", "required_role": "Specialist", "required_fields": []},
            {"from": "In_Stitching", "to": "Quality_Check", "label": "Pass to QA", "required_role": "Specialist", "required_fields": []},
            {"from": "Quality_Check", "to": "Ready_For_Pickup", "label": "Notify Customer for Pickup", "required_role": "Staff", "required_fields": []},
            {"from": "Ready_For_Pickup", "to": "Delivered", "label": "Handover to Customer", "required_role": "Staff", "required_fields": []}
        ]
    },
    "Legal": {
        "name": "Litigation & Advisory Matter Lifecycle",
        "initial_status": "Intake_Conflict_Check",
        "statuses": [
            {"id": "Intake_Conflict_Check", "label": "Conflict Check", "color": "#f59e0b", "sla_hours": 24},
            {"id": "Retainer_Signed", "label": "Retainer Executed", "color": "#3b82f6", "sla_hours": 48},
            {"id": "Active_Matter", "label": "Active Matter", "color": "#8b5cf6", "sla_hours": 168},
            {"id": "Brief_Drafted", "label": "Filing Drafted", "color": "#10b981", "sla_hours": 240},
            {"id": "Matter_Concluded", "label": "Matter Concluded", "color": "#64748b", "sla_hours": 360}
        ],
        "transitions": [
            {"from": "Intake_Conflict_Check", "to": "Retainer_Signed", "label": "Clear Conflicts & Sign", "required_role": "Consultant", "required_fields": ["conflict_clearance"]},
            {"from": "Retainer_Signed", "to": "Active_Matter", "label": "Commence Legal Work", "required_role": "Staff", "required_fields": []},
            {"from": "Active_Matter", "to": "Brief_Drafted", "label": "Submit Discovery/Brief", "required_role": "Consultant", "required_fields": []},
            {"from": "Brief_Drafted", "to": "Matter_Concluded", "label": "Conclude Case & Close Retainer", "required_role": "Consultant", "required_fields": []}
        ]
    }
}

# Standard Default Industry Custom Field Definitions
DEFAULT_CUSTOM_FIELDS = {
    "Healthcare": [
        {"field_key": "blood_group", "field_label": "Blood Group", "field_type": "select", "options": ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"], "is_required": False},
        {"field_key": "emergency_contact", "field_label": "Emergency Contact Number", "field_type": "text", "is_required": True},
        {"field_key": "chronic_allergies", "field_label": "Drug Allergies & Notes", "field_type": "text", "is_required": False},
        {"field_key": "insurance_id", "field_label": "Insurance Policy / TPA ID", "field_type": "text", "is_required": False}
    ],
    "Salon": [
        {"field_key": "preferred_stylist", "field_label": "Preferred Senior Stylist", "field_type": "text", "is_required": False},
        {"field_key": "skin_sensitivity", "field_label": "Skin Sensitivity Level", "field_type": "select", "options": ["Normal", "Sensitive", "Hyper-Allergic"], "is_required": False},
        {"field_key": "patch_test_date", "field_label": "Patch Test Completion Date", "field_type": "date", "is_required": False}
    ],
    "Finance": [
        {"field_key": "risk_tolerance", "field_label": "Risk Tolerance Profile", "field_type": "select", "options": ["Conservative", "Moderate", "Aggressive", "Ultra-High Net Worth"], "is_required": True},
        {"field_key": "investment_horizon_yrs", "field_label": "Investment Horizon (Years)", "field_type": "number", "is_required": True, "default_value": "5"},
        {"field_key": "target_aum_lakhs", "field_label": "Target AUM (in Lakhs)", "field_type": "number", "is_required": False}
    ],
    "Insurance": [
        {"field_key": "policy_type", "field_label": "Policy Type", "field_type": "select", "options": ["Comprehensive Health", "Term Life", "Commercial Property", "Motor Fleet"], "is_required": True},
        {"field_key": "sum_insured_inr", "field_label": "Sum Insured (INR)", "field_type": "number", "is_required": True},
        {"field_key": "nominee_name", "field_label": "Nominee Legal Name", "field_type": "text", "is_required": True}
    ],
    "Retail": [
        {"field_key": "garment_style", "field_label": "Garment Style / Collection", "field_type": "text", "is_required": True},
        {"field_key": "fitting_urgency", "field_label": "Alteration Urgency Tier", "field_type": "select", "options": ["Standard (7 Days)", "Express (48 Hours)", "Emergency (24 Hours)"], "is_required": False},
        {"field_key": "fabric_type", "field_label": "Fabric & Material Care", "field_type": "text", "is_required": False}
    ],
    "Legal": [
        {"field_key": "matter_type", "field_label": "Matter Classification", "field_type": "select", "options": ["Corporate M&A", "Commercial Litigation", "Intellectual Property", "Employment Law"], "is_required": True},
        {"field_key": "opposing_counsel", "field_label": "Opposing Party / Counsel", "field_type": "text", "is_required": False},
        {"field_key": "statute_deadline", "field_label": "Statute of Limitations Date", "field_type": "date", "is_required": False}
    ],
    "Education": [
        {"field_key": "target_intake", "field_label": "Target Academic Intake", "field_type": "select", "options": ["Fall 2026", "Spring 2027", "Summer 2027"], "is_required": True},
        {"field_key": "target_country", "field_label": "Destination Country", "field_type": "select", "options": ["USA", "UK", "Canada", "Germany", "Australia", "Singapore"], "is_required": True},
        {"field_key": "ielts_toefl_score", "field_label": "Language Proficiency Score", "field_type": "text", "is_required": False}
    ],
    "Real Estate": [
        {"field_key": "property_category", "field_label": "Property Category", "field_type": "select", "options": ["Luxury Residential", "Commercial Office", "Retail Storefront", "Industrial Warehouse"], "is_required": True},
        {"field_key": "target_budget_range", "field_label": "Budget Bracket (INR / USD)", "field_type": "text", "is_required": True},
        {"field_key": "proof_of_funds_verified", "field_label": "Pre-Approval Verified", "field_type": "boolean", "default_value": "false", "is_required": False}
    ],
    "Professional Services": [
        {"field_key": "contract_model", "field_label": "Engagement Billing Model", "field_type": "select", "options": ["Time & Materials (T&M)", "Fixed Price Milestone", "Monthly Retainer", "Value-Based"], "is_required": True},
        {"field_key": "project_code", "field_label": "Enterprise Cost Center / Project Code", "field_key": "text", "is_required": True},
        {"field_key": "sla_response_hours", "field_label": "SLA Response Guarantee (Hours)", "field_type": "number", "default_value": "4", "is_required": False}
    ]
}


def _get_sector_key(sector_raw):
    s = (sector_raw or "").lower()
    if "health" in s or "clinic" in s or "hospital" in s:
        return "Healthcare"
    if "salon" in s or "spa" in s or "wellness" in s:
        return "Salon"
    if "fin" in s or "wealth" in s:
        return "Finance"
    if "insur" in s:
        return "Insurance"
    if "ret" in s or "couture" in s:
        return "Retail"
    if "edu" in s or "study" in s:
        return "Education"
    if "law" in s or "legal" in s or "consult" in s:
        return "Legal"
    if "real" in s or "estate" in s or "prop" in s:
        return "Real Estate"
    return "Professional Services"


# -----------------------------------------------------------------------------
# Custom Fields API Endpoints
# -----------------------------------------------------------------------------
@custom_fields_bp.route("/definitions", methods=["GET"])
@require_roles(*ORG_ROLES)
def get_custom_field_definitions():
    """Returns custom field definitions for the current tenant's sector."""
    claims = get_jwt()
    role = claims.get("role")
    org_id = get_organization_id() if role != "Admin" else int(request.args.get("organization_id") or 1)
    org = Organization.query.get(org_id)
    sector_key = _get_sector_key(org.sector if org else "Healthcare")

    # Fetch custom fields specifically configured for this org or global defaults
    fields = CustomFieldDefinition.query.filter(
        (CustomFieldDefinition.organization_id == org_id) | (CustomFieldDefinition.organization_id.is_(None)),
        CustomFieldDefinition.sector == sector_key
    ).all()

    # Auto-seed defaults if none exist in the database yet
    if not fields and sector_key in DEFAULT_CUSTOM_FIELDS:
        seeded = []
        for d in DEFAULT_CUSTOM_FIELDS[sector_key]:
            cf = CustomFieldDefinition(
                organization_id=org_id,
                sector=sector_key,
                entity_type="record",
                field_key=d.get("field_key"),
                field_label=d.get("field_label"),
                field_type=d.get("field_type", "text"),
                is_required=d.get("is_required", False),
                options=d.get("options", []),
                default_value=d.get("default_value")
            )
            db.session.add(cf)
            seeded.append(cf)
        db.session.commit()
        fields = seeded

    return jsonify({
        "organization_id": org_id,
        "sector": sector_key,
        "definitions": [
            {
                "id": f.id,
                "field_key": f.field_key,
                "field_label": f.field_label,
                "field_type": f.field_type,
                "is_required": f.is_required,
                "options": f.options or [],
                "default_value": f.default_value,
                "validation_rules": f.validation_rules or {}
            }
            for f in fields
        ]
    })


@custom_fields_bp.route("/definitions", methods=["POST"])
@require_roles("Admin", "Organization", "Manager")
def create_custom_field_definition():
    """Allows tenant administrators to add dynamic custom fields."""
    claims = get_jwt()
    role = claims.get("role")
    org_id = get_organization_id() if role != "Admin" else int(request.json.get("organization_id") or 1)
    org = Organization.query.get(org_id)
    sector_key = _get_sector_key(org.sector if org else "Healthcare")

    data = request.json or {}
    field_key = data.get("field_key", "").strip().lower().replace(" ", "_")
    field_label = data.get("field_label", "").strip()

    if not field_key or not field_label:
        return jsonify({"msg": "field_key and field_label are required"}), 400

    cf = CustomFieldDefinition(
        organization_id=org_id,
        sector=sector_key,
        entity_type=data.get("entity_type", "record"),
        field_key=field_key,
        field_label=field_label,
        field_type=data.get("field_type", "text"),
        is_required=bool(data.get("is_required", False)),
        options=data.get("options", []),
        default_value=str(data.get("default_value") or ""),
        validation_rules=data.get("validation_rules", {})
    )
    db.session.add(cf)
    db.session.commit()

    return jsonify({
        "msg": "Custom field created successfully",
        "custom_field": {
            "id": cf.id,
            "field_key": cf.field_key,
            "field_label": cf.field_label,
            "field_type": cf.field_type,
            "is_required": cf.is_required,
            "options": cf.options
        }
    }), 201


# -----------------------------------------------------------------------------
# Workflow Engine Endpoints
# -----------------------------------------------------------------------------
@workflows_bp.route("/definitions", methods=["GET"])
@require_roles(*ORG_ROLES)
def get_workflow_definitions():
    """Returns active workflow state machine and transition rules for current sector."""
    claims = get_jwt()
    role = claims.get("role")
    org_id = get_organization_id() if role != "Admin" else int(request.args.get("organization_id") or 1)
    org = Organization.query.get(org_id)
    sector_key = _get_sector_key(org.sector if org else "Healthcare")

    wf = WorkflowDefinition.query.filter_by(organization_id=org_id, sector=sector_key, is_active=True).first()
    if not wf:
        # Check global default or seed
        defaults = DEFAULT_WORKFLOWS.get(sector_key, DEFAULT_WORKFLOWS["Healthcare"])
        wf = WorkflowDefinition(
            organization_id=org_id,
            sector=sector_key,
            name=defaults["name"],
            entity_type="record",
            initial_status=defaults["initial_status"],
            statuses=defaults["statuses"],
            transitions=defaults["transitions"],
            is_active=True
        )
        db.session.add(wf)
        db.session.commit()

    return jsonify({
        "organization_id": org_id,
        "sector": sector_key,
        "workflow": {
            "id": wf.id,
            "name": wf.name,
            "initial_status": wf.initial_status,
            "statuses": wf.statuses,
            "transitions": wf.transitions
        }
    })


@workflows_bp.route("/records/<int:record_id>/transition", methods=["POST"])
@require_roles(*ORG_ROLES)
def execute_workflow_transition(record_id):
    """
    Executes a formal workflow transition for an IndustryRecord:
    - Validates transition is permitted from current status
    - Verifies required role and required field presence in record.data
    - Records immutable WorkflowTransitionHistory entry
    - Dispatches in-app event notification
    """
    claims = get_jwt()
    role = claims.get("role")
    user_id = claims.get("sub")
    org_id = get_organization_id() if role != "Admin" else None

    query = IndustryRecord.query.filter_by(id=record_id)
    if org_id:
        query = query.filter_by(organization_id=org_id)
    record = query.first()

    if not record:
        return jsonify({"msg": "Record not found or access denied"}), 404

    data = request.json or {}
    target_status = data.get("target_status")
    comment = data.get("comment", "")
    additional_data = data.get("additional_data", {})

    if not target_status:
        return jsonify({"msg": "target_status is required"}), 400

    sector_key = _get_sector_key(record.sector)
    wf = WorkflowDefinition.query.filter_by(organization_id=record.organization_id, sector=sector_key, is_active=True).first()
    if not wf:
        defaults = DEFAULT_WORKFLOWS.get(sector_key, DEFAULT_WORKFLOWS["Healthcare"])
        wf = WorkflowDefinition(
            organization_id=record.organization_id,
            sector=sector_key,
            name=defaults["name"],
            entity_type="record",
            initial_status=defaults["initial_status"],
            statuses=defaults["statuses"],
            transitions=defaults["transitions"],
            is_active=True
        )
        db.session.add(wf)
        db.session.commit()

    # Find matching transition rule
    allowed_transition = None
    current_status = record.status or wf.initial_status
    for t in (wf.transitions or []):
        if t.get("from") == current_status and t.get("to") == target_status:
            allowed_transition = t
            break

    # If not explicitly mapped, check if Admin/Manager override is requested
    if not allowed_transition and role not in ("Admin", "SuperAdmin", "Organization", "Manager"):
        return jsonify({
            "error": "INVALID_TRANSITION",
            "msg": f"Transition from '{current_status}' to '{target_status}' is not permitted by workflow rules."
        }), 400

    # Role authorization check
    if allowed_transition and allowed_transition.get("required_role"):
        req_role = allowed_transition["required_role"]
        if req_role != role and role not in ("Admin", "SuperAdmin", "Organization", "Manager"):
            return jsonify({
                "error": "ROLE_UNAUTHORIZED",
                "msg": f"Transition to '{target_status}' requires role '{req_role}', but current role is '{role}'."
            }), 403

    # Check required fields
    record_data = dict(record.data or {})
    if additional_data:
        record_data.update(additional_data)

    if allowed_transition and allowed_transition.get("required_fields"):
        missing = [f for f in allowed_transition["required_fields"] if f not in record_data or record_data[f] is None]
        if missing:
            return jsonify({
                "error": "REQUIRED_FIELDS_MISSING",
                "msg": f"Cannot transition to '{target_status}'. Missing required fields: {', '.join(missing)}",
                "missing_fields": missing
            }), 400

    # Execute state change
    prev_status = record.status
    record.status = target_status
    record.data = record_data
    record.updated_at = datetime.utcnow()

    # Append immutable transition history
    history = WorkflowTransitionHistory(
        organization_id=record.organization_id,
        record_id=record.id,
        from_status=prev_status,
        to_status=target_status,
        triggered_by_user=str(user_id),
        user_role=role,
        comment=comment,
        transition_metadata={"additional_data_keys": list(additional_data.keys())}
    )
    db.session.add(history)

    # Dispatch in-app notification
    notif = Notification(
        organization_id=record.organization_id,
        recipient_type="organization",
        channel="in_app",
        title=f"Workflow Transition: {record.title}",
        message=f"Record #{record.id} shifted from '{prev_status}' to '{target_status}' by {role}."
    )
    db.session.add(notif)

    # Audit log
    audit = AuditLog(
        organization_id=record.organization_id,
        action="WORKFLOW_TRANSITION_EXECUTED",
        entity="IndustryRecord",
        entity_id=record.id,
        details=f"Status changed from {prev_status} to {target_status}. Comment: {comment}",
        ip_address=request.remote_addr
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({
        "msg": f"Successfully transitioned record to '{target_status}'",
        "record_id": record.id,
        "previous_status": prev_status,
        "new_status": target_status,
        "history_id": history.id,
        "updated_at": record.updated_at.isoformat()
    })


@workflows_bp.route("/records/<int:record_id>/history", methods=["GET"])
@require_roles(*ORG_ROLES)
def get_workflow_history(record_id):
    """Returns chronological audit history of all transitions for a given record."""
    claims = get_jwt()
    role = claims.get("role")
    org_id = get_organization_id() if role != "Admin" else None

    query = IndustryRecord.query.filter_by(id=record_id)
    if org_id:
        query = query.filter_by(organization_id=org_id)
    record = query.first()

    if not record:
        return jsonify({"msg": "Record not found or access denied"}), 404

    entries = WorkflowTransitionHistory.query.filter_by(record_id=record_id).order_by(
        WorkflowTransitionHistory.created_at.desc()
    ).all()

    return jsonify({
        "record_id": record_id,
        "record_title": record.title,
        "current_status": record.status,
        "history": [
            {
                "id": h.id,
                "from_status": h.from_status,
                "to_status": h.to_status,
                "triggered_by_user": h.triggered_by_user,
                "user_role": h.user_role,
                "comment": h.comment,
                "created_at": h.created_at.isoformat() if h.created_at else None
            }
            for h in entries
        ]
    })
