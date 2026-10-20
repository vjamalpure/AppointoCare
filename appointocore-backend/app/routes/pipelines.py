from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from app.models import db, BusinessPipeline, AuditLog
from datetime import datetime

pipelines_bp = Blueprint("pipelines_bp", __name__)

ALLOWED_ROLES = (
    "Admin", "SuperAdmin", "Organization", "Manager", "Staff",
    "Doctor", "Therapist", "Stylist", "Advisor", "Underwriter",
    "Broker", "Consultant", "Specialist", "Counselor"
)


def _get_org_id():
    claims = get_jwt()
    if claims.get("role") in ["Admin", "SuperAdmin"]:
        data = request.json or {}
        param_org = request.args.get("organization_id") or data.get("organization_id")
        return int(param_org) if param_org else int(claims.get("organization_id") or 1)
    return int(claims.get("organization_id") or get_jwt_identity())


DEFAULT_STAGES_BY_SECTOR = {
    "Healthcare": [
        {"id": "inquiry", "name": "Patient Inquiry", "order": 1, "probability": 25},
        {"id": "triage", "name": "Clinical Triage", "order": 2, "probability": 50},
        {"id": "consultation", "name": "Doctor Consultation", "order": 3, "probability": 75},
        {"id": "treatment", "name": "Treatment Plan Active", "order": 4, "probability": 90},
        {"id": "follow_up", "name": "Discharged / Follow-up", "order": 5, "probability": 100}
    ],
    "Real Estate": [
        {"id": "lead", "name": "Property Lead", "order": 1, "probability": 15},
        {"id": "site_visit", "name": "Site Visit Scheduled", "order": 2, "probability": 40},
        {"id": "offer_made", "name": "Offer Submitted", "order": 3, "probability": 70},
        {"id": "escrow", "name": "Under Escrow Review", "order": 4, "probability": 90},
        {"id": "closed", "name": "Deal Closed & Commission Split", "order": 5, "probability": 100}
    ],
    "Insurance": [
        {"id": "inquiry", "name": "Quote Request", "order": 1, "probability": 20},
        {"id": "quote_sent", "name": "Multi-Carrier Comparison Sent", "order": 2, "probability": 50},
        {"id": "underwriting", "name": "Underwriting Review", "order": 3, "probability": 75},
        {"id": "policy_issued", "name": "Policy Issued & Bound", "order": 4, "probability": 100}
    ],
    "Education": [
        {"id": "inquiry", "name": "Prospective Student", "order": 1, "probability": 20},
        {"id": "shortlist", "name": "University Shortlist", "order": 2, "probability": 45},
        {"id": "applied", "name": "Application Lodged", "order": 3, "probability": 70},
        {"id": "offer_received", "name": "University Offer Received", "order": 4, "probability": 85},
        {"id": "visa_stamped", "name": "Visa Approved & Enrolled", "order": 5, "probability": 100}
    ],
    "Finance": [
        {"id": "prospect", "name": "Wealth Prospect", "order": 1, "probability": 20},
        {"id": "kyc_risk", "name": "Suitability & KYC Intake", "order": 2, "probability": 50},
        {"id": "proposal", "name": "Allocation Proposal", "order": 3, "probability": 80},
        {"id": "onboarded", "name": "Mandate Executed", "order": 4, "probability": 100}
    ],
    "Consultancy": [
        {"id": "lead", "name": "Prospective Client", "order": 1, "probability": 25},
        {"id": "conflict_check", "name": "Conflict Clearance Search", "order": 2, "probability": 60},
        {"id": "engagement", "name": "Retainer Agreement Sent", "order": 3, "probability": 85},
        {"id": "active_matter", "name": "Matter Active", "order": 4, "probability": 100}
    ],
    "Professional Services": [
        {"id": "discovery", "name": "SOW Discovery", "order": 1, "probability": 30},
        {"id": "sow_draft", "name": "SOW Drafting", "order": 2, "probability": 60},
        {"id": "approved", "name": "Client Sign-off", "order": 3, "probability": 90},
        {"id": "delivering", "name": "Active Sprint Delivery", "order": 4, "probability": 100}
    ],
    "Retail": [
        {"id": "inquiry", "name": "Client VIP Inquiry", "order": 1, "probability": 30},
        {"id": "fitting", "name": "Fitting / Styling Session", "order": 2, "probability": 60},
        {"id": "alteration", "name": "In Tailoring / Alteration", "order": 3, "probability": 85},
        {"id": "fulfilled", "name": "Delivered / Completed", "order": 4, "probability": 100}
    ],
    "Salon": [
        {"id": "booked", "name": "VIP Consultation Booked", "order": 1, "probability": 40},
        {"id": "in_treatment", "name": "Treatment In Progress", "order": 2, "probability": 80},
        {"id": "post_care", "name": "Completed & Rebooking Scheduled", "order": 3, "probability": 100}
    ]
}


@pipelines_bp.route("", methods=["GET"])
@jwt_required()
def get_pipelines():
    claims = get_jwt()
    if claims.get("role") not in ALLOWED_ROLES:
        return jsonify({"msg": "Unauthorized"}), 403

    org_id = _get_org_id()
    sector = request.args.get("sector")

    query = BusinessPipeline.query.filter_by(organization_id=org_id)
    if sector:
        query = query.filter_by(sector=sector)

    pipelines = query.all()

    # If none exist, auto-seed sector default
    if not pipelines and sector:
        default_stages = DEFAULT_STAGES_BY_SECTOR.get(sector, [
            {"id": "lead", "name": "New Lead", "order": 1, "probability": 25},
            {"id": "contacted", "name": "Contacted", "order": 2, "probability": 50},
            {"id": "proposal", "name": "Proposal", "order": 3, "probability": 75},
            {"id": "won", "name": "Won", "order": 4, "probability": 100}
        ])
        pipe = BusinessPipeline(
            organization_id=org_id,
            sector=sector,
            name=f"{sector} Deal Pipeline",
            stages=default_stages,
            deals=[
                {
                    "id": f"deal-{int(datetime.utcnow().timestamp())}",
                    "title": f"Primary {sector} Client Engagement",
                    "stage_id": default_stages[0]["id"],
                    "value": 45000,
                    "customer_name": "Premium Enterprise Account",
                    "owner": claims.get("sub") or "Specialist",
                    "created_at": datetime.utcnow().isoformat()
                }
            ]
        )
        db.session.add(pipe)
        db.session.commit()
        pipelines = [pipe]

    return jsonify([
        {
            "id": p.id,
            "organization_id": p.organization_id,
            "sector": p.sector,
            "name": p.name,
            "stages": p.stages or [],
            "deals": p.deals or [],
            "deal_count": len(p.deals or []),
            "pipeline_value": sum(d.get("value", 0) for d in (p.deals or []))
        }
        for p in pipelines
    ]), 200


@pipelines_bp.route("/<int:pipeline_id>/deals", methods=["POST"])
@jwt_required()
def add_deal(pipeline_id):
    claims = get_jwt()
    if claims.get("role") not in ALLOWED_ROLES:
        return jsonify({"msg": "Unauthorized"}), 403

    org_id = _get_org_id()
    pipe = BusinessPipeline.query.filter_by(id=pipeline_id, organization_id=org_id).first_or_404()
    data = request.json or {}

    title = data.get("title", "").strip()
    if not title:
        return jsonify({"msg": "title is required"}), 400

    stage_id = data.get("stage_id")
    if not stage_id and pipe.stages:
        stage_id = pipe.stages[0]["id"]

    new_deal = {
        "id": f"deal-{int(datetime.utcnow().timestamp())}",
        "title": title,
        "stage_id": stage_id,
        "value": float(data.get("value") or 0.0),
        "customer_id": data.get("customer_id"),
        "customer_name": data.get("customer_name") or "New Client",
        "owner": data.get("owner") or claims.get("sub") or "Staff",
        "notes": data.get("notes", ""),
        "created_at": datetime.utcnow().isoformat()
    }

    current_deals = list(pipe.deals or [])
    current_deals.append(new_deal)
    pipe.deals = current_deals
    db.session.commit()

    return jsonify({"msg": "Deal added successfully", "deal": new_deal}), 201


@pipelines_bp.route("/<int:pipeline_id>/deals/<deal_id>/move", methods=["PUT"])
@jwt_required()
def move_deal(pipeline_id, deal_id):
    claims = get_jwt()
    if claims.get("role") not in ALLOWED_ROLES:
        return jsonify({"msg": "Unauthorized"}), 403

    org_id = _get_org_id()
    pipe = BusinessPipeline.query.filter_by(id=pipeline_id, organization_id=org_id).first_or_404()
    data = request.json or {}
    new_stage = data.get("stage_id")
    if not new_stage:
        return jsonify({"msg": "stage_id is required"}), 400

    current_deals = list(pipe.deals or [])
    target_deal = None
    for d in current_deals:
        if d.get("id") == deal_id:
            old_stage = d.get("stage_id")
            d["stage_id"] = new_stage
            d["updated_at"] = datetime.utcnow().isoformat()
            target_deal = d
            break

    if not target_deal:
        return jsonify({"msg": "Deal not found"}), 404

    pipe.deals = current_deals
    db.session.commit()

    return jsonify({"msg": "Deal moved successfully", "deal": target_deal}), 200
