from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.models import db, Service, Organization, AuditLog
from app.security import require_roles

service_bp = Blueprint("service_bp", __name__)

SECTOR_SERVICES_PRESETS = {
    "Healthcare": [
        {"name": "General Physician Consultation", "category": "Consultation", "price": 60.0, "duration_minutes": 30, "description": "Comprehensive physical examination and vitals check."},
        {"name": "Specialist Evaluation (Cardiology/ENT)", "category": "Specialist", "price": 120.0, "duration_minutes": 45, "description": "In-depth diagnostic assessment and treatment plan."},
        {"name": "Comprehensive Health & Blood Panel", "category": "Diagnostics", "price": 150.0, "duration_minutes": 60, "description": "Full blood screening and metabolic evaluation."},
        {"name": "Dental Cleaning & Oral Exam", "category": "Dental", "price": 85.0, "duration_minutes": 45, "description": "Ultrasonic plaque removal and oral health review."},
        {"name": "Physiotherapy Rehabilitation", "category": "Therapy", "price": 90.0, "duration_minutes": 60, "description": "Musculoskeletal assessment and guided kinetic therapy."}
    ],
    "Finance": [
        {"name": "Personal Loan & Mortgage Consultation", "category": "Lending", "price": 75.0, "duration_minutes": 45, "description": "Mortgage pre-approval, rate locking, and amortisation review."},
        {"name": "Investment & Wealth Portfolio Review", "category": "Wealth", "price": 180.0, "duration_minutes": 60, "description": "Asset allocation analysis, risk indexing, and wealth growth roadmap."},
        {"name": "Tax Filing & Assessment Planning", "category": "Tax", "price": 110.0, "duration_minutes": 45, "description": "Capital gains review, deductor analysis, and corporate filing."},
        {"name": "Business Audit & Credit Structuring", "category": "Corporate", "price": 250.0, "duration_minutes": 90, "description": "Commercial underwriting, debt facility structuring, and working capital review."}
    ],
    "Retail": [
        {"name": "VIP Private Styling & Fitting", "category": "Styling", "price": 100.0, "duration_minutes": 60, "description": "One-on-one session with senior stylist in private VIP lounge."},
        {"name": "Bridal & Bespoke Wardrobe Session", "category": "Custom", "price": 220.0, "duration_minutes": 90, "description": "Tailored bridal styling, fabric swatches, and bespoke measurements."},
        {"name": "High-Jewelry Private Viewing Suite", "category": "Jewelry", "price": 150.0, "duration_minutes": 45, "description": "Chamber viewing of rare gems and certified fine timepieces."},
        {"name": "In-Store Product Demo & Fitting", "category": "General", "price": 40.0, "duration_minutes": 30, "description": "Personalized walkthrough and fitting of new arrivals."}
    ],
    "Insurance": [
        {"name": "Term & Life Insurance Policy Advisory", "category": "Life", "price": 65.0, "duration_minutes": 45, "description": "Comprehensive term coverage evaluation and estate liquidity planning."},
        {"name": "Health Insurance Claims Review", "category": "Health", "price": 50.0, "duration_minutes": 30, "description": "Claims adjudication review, pre-authorization, and rider checks."},
        {"name": "Commercial & Motor Risk Assessment", "category": "Commercial", "price": 120.0, "duration_minutes": 60, "description": "Asset liability auditing, fleet risk management, and indemnity limits."}
    ],
    "Education": [
        {"name": "Academic Course Guidance & Planning", "category": "Counseling", "price": 60.0, "duration_minutes": 45, "description": "Curriculum selection, prerequisite verification, and semester roadmapping."},
        {"name": "University Admission Interview Prep", "category": "Admissions", "price": 120.0, "duration_minutes": 60, "description": "Simulated admissions panel interview, feedback, and SOP polishing."},
        {"name": "Career Counseling & Aptitude Analysis", "category": "Career", "price": 95.0, "duration_minutes": 60, "description": "Psychometric evaluation review and industry career trajectory mapping."},
        {"name": "1-on-1 Academic Tutoring Session", "category": "Tutoring", "price": 50.0, "duration_minutes": 45, "description": "Targeted subject mastery and exam coaching with faculty tutor."}
    ],
    "Salon": [
        {"name": "Master Haircut & Keratin Treatment", "category": "Hair", "price": 85.0, "duration_minutes": 60, "description": "Precision stylist cut, scalp treatment, and keratin infusion."},
        {"name": "Holistic Spa & Aromatherapy Massage", "category": "Spa", "price": 110.0, "duration_minutes": 60, "description": "Swedish pressure therapy with botanical essential oils."},
        {"name": "Hydra-Facial & Skin Revitalisation", "category": "Skin", "price": 95.0, "duration_minutes": 50, "description": "Deep pore vortex extraction, peptide infusion, and antioxidant therapy."},
        {"name": "Deluxe Manicure & Pedicure Suite", "category": "Nails", "price": 55.0, "duration_minutes": 45, "description": "Exfoliating sea salt scrub, cuticle care, and gel polish."}
    ],
    "Consultancy": [
        {"name": "Corporate Business Strategy Session", "category": "Management", "price": 200.0, "duration_minutes": 60, "description": "Strategic market expansion, competitive positioning, and KPI framework."},
        {"name": "Legal Counsel & Contract Review", "category": "Legal", "price": 250.0, "duration_minutes": 60, "description": "Commercial contract drafting, NDA risk assessment, and regulatory review."},
        {"name": "Cloud Architecture & Cyber Review", "category": "Tech", "price": 195.0, "duration_minutes": 75, "description": "AWS/GCP infrastructure security audit and cloud cost optimization."},
        {"name": "HR Operations & Talent Audit", "category": "HR", "price": 140.0, "duration_minutes": 45, "description": "Organizational restructuring, compensation benchmark, and retention analysis."}
    ],
    "Real Estate": [
        {"name": "VIP Property Tour & Site Inspection", "category": "Viewing", "price": 75.0, "duration_minutes": 60, "description": "Private guided tour of luxury residences or commercial developments."},
        {"name": "Commercial Lease & Zoning Consultation", "category": "Commercial", "price": 150.0, "duration_minutes": 60, "description": "Zoning ordinances, cap rate projections, and tenant agreement advisory."},
        {"name": "Real Estate Valuation & Appraisal Review", "category": "Valuation", "price": 120.0, "duration_minutes": 45, "description": "Comparative market analysis, structural appraisal, and tax assessments."}
    ],
    "Professional Services": [
        {"name": "Enterprise Cloud Architecture Audit", "category": "IT", "price": 1200.0, "duration_minutes": 90, "description": "High-availability multi-region enterprise infrastructure review."},
        {"name": "AI Transformation & Workflow Blueprint", "category": "AI", "price": 1500.0, "duration_minutes": 120, "description": "Executive briefing on generative AI deployment, compliance, and ROI."}
    ]
}


@service_bp.route("", methods=["GET"])
@service_bp.route("/all", methods=["GET"])
@require_roles("Admin", "Organization", "Manager", "Staff")
def get_services():
    claims = get_jwt()
    role = claims.get("role")
    organization_id = request.args.get("organization_id")

    if role == "Admin":
        if organization_id:
            services = Service.query.filter_by(organization_id=int(organization_id)).all()
        else:
            services = Service.query.all()
    else:
        org_id = int(claims.get("organization_id") or 0)
        services = Service.query.filter_by(organization_id=org_id).all()

    return jsonify([
        {
            "id": s.id,
            "organization_id": s.organization_id,
            "name": s.name,
            "description": s.description,
            "category": s.category,
            "price": s.price,
            "duration_minutes": s.duration_minutes,
            "active": s.active,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "updated_at": s.updated_at.isoformat() if s.updated_at else None,
        }
        for s in services
    ])


@service_bp.route("", methods=["POST"])
@service_bp.route("/create", methods=["POST"])
@require_roles("Admin", "Organization", "Manager", "Staff")
def create_service():
    claims = get_jwt()
    role = claims.get("role")
    data = request.json or {}

    if role == "Admin":
        if not data.get("organization_id"):
            return jsonify({"msg": "organization_id is required for admin-created services"}), 400
        organization_id = int(data["organization_id"])
    else:
        organization_id = int(claims.get("organization_id") or 0)

    if not data.get("name"):
        return jsonify({"msg": "name is required"}), 400

    service = Service(
        organization_id=organization_id,
        name=data["name"],
        description=data.get("description"),
        category=data.get("category", "General"),
        price=float(data.get("price", 0.0)),
        duration_minutes=int(data.get("duration_minutes", 30)),
        active=data.get("active", True)
    )
    db.session.add(service)
    db.session.commit()

    return jsonify({"msg": "Service created successfully", "service_id": service.id, "id": service.id}), 201


@service_bp.route("/<int:service_id>", methods=["GET"])
@require_roles("Admin", "Organization", "Manager", "Staff")
def get_single_service(service_id):
    claims = get_jwt()
    role = claims.get("role")
    service = Service.query.get_or_404(service_id)

    if role != "Admin" and service.organization_id != int(claims.get("organization_id") or 0):
        return jsonify({"msg": "Unauthorized"}), 403

    return jsonify({
        "id": service.id,
        "organization_id": service.organization_id,
        "name": service.name,
        "description": service.description,
        "category": service.category,
        "price": service.price,
        "duration_minutes": service.duration_minutes,
        "active": service.active,
        "created_at": service.created_at.isoformat() if service.created_at else None,
        "updated_at": service.updated_at.isoformat() if service.updated_at else None
    })


@service_bp.route("/<int:service_id>", methods=["PUT", "PATCH"])
@require_roles("Admin", "Organization", "Manager", "Staff")
def update_service(service_id):
    claims = get_jwt()
    role = claims.get("role")
    data = request.json or {}

    service = Service.query.get_or_404(service_id)
    if role != "Admin" and service.organization_id != int(claims.get("organization_id") or 0):
        return jsonify({"msg": "Unauthorized"}), 403

    if "name" in data:
        service.name = data["name"]
    if "description" in data:
        service.description = data["description"]
    if "category" in data:
        service.category = data["category"]
    if "price" in data:
        service.price = float(data["price"])
    if "duration_minutes" in data:
        service.duration_minutes = int(data["duration_minutes"])
    if "active" in data:
        service.active = bool(data["active"])

    db.session.commit()
    return jsonify({"msg": "Service updated successfully", "id": service.id})


@service_bp.route("/<int:service_id>", methods=["DELETE"])
@require_roles("Admin", "Organization", "Manager", "Staff")
def delete_service(service_id):
    claims = get_jwt()
    role = claims.get("role")
    service = Service.query.get_or_404(service_id)

    if role != "Admin" and service.organization_id != int(claims.get("organization_id") or 0):
        return jsonify({"msg": "Unauthorized"}), 403

    db.session.delete(service)
    db.session.commit()
    return jsonify({"msg": "Service deleted successfully"})


@service_bp.route("/import-sector", methods=["POST"])
@require_roles("Admin", "Organization", "Manager", "Staff")
def import_sector_template():
    claims = get_jwt()
    role = claims.get("role")
    data = request.json or {}

    if role == "Admin":
        organization_id = int(data.get("organization_id") or 1)
    else:
        organization_id = int(claims.get("organization_id") or 0)

    sector_req = data.get("sector") or "Healthcare"

    # Find matching presets
    matching_key = None
    for k in SECTOR_SERVICES_PRESETS.keys():
        if k.lower() in sector_req.lower() or sector_req.lower() in k.lower():
            matching_key = k
            break
    if not matching_key:
        matching_key = "Healthcare"

    presets = SECTOR_SERVICES_PRESETS.get(matching_key, [])
    created = []

    for p in presets:
        existing = Service.query.filter_by(organization_id=organization_id, name=p["name"]).first()
        if not existing:
            svc = Service(
                organization_id=organization_id,
                name=p["name"],
                description=p.get("description"),
                category=p.get("category", "General"),
                price=float(p.get("price", 0.0)),
                duration_minutes=int(p.get("duration_minutes", 30)),
                active=True
            )
            db.session.add(svc)
            created.append(svc)

    db.session.commit()

    # Log audit
    audit = AuditLog(
        organization_id=organization_id,
        user_id=int(claims.get("sub") or 0) if claims.get("sub") and str(claims.get("sub")).isdigit() else None,
        user_role=role,
        action="IMPORT_SECTOR_SERVICES",
        entity="ServiceCatalog",
        entity_id=organization_id,
        details=f"Imported {len(created)} services for sector '{matching_key}' into Organization #{organization_id}",
        ip_address=request.remote_addr
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({
        "msg": f"Imported {len(created)} standard {matching_key} services successfully",
        "imported_count": len(created),
        "sector": matching_key
    }), 200
