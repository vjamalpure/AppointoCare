from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from app.models import db, Customer, Organization, Appointment, MessageLog, AppointmentTransaction, AuditLog

customer_bp = Blueprint("customer_bp", __name__)


@customer_bp.route("", methods=["GET"])
@customer_bp.route("/all", methods=["GET"])
@jwt_required()
def get_customers():
    claims = get_jwt()
    role = claims.get("role")
    org_id = request.args.get("organization_id")

    query = Customer.query
    if role in ["Admin", "SuperAdmin"]:
        if org_id and org_id != "ALL":
            query = query.filter_by(organization_id=int(org_id))
    else:
        org_id = int(claims.get("organization_id") or 0)
        query = query.filter_by(organization_id=org_id)

    q = request.args.get("q") or request.args.get("search")
    if q:
        query = query.filter(
            db.or_(
                Customer.name.ilike(f"%{q}%"),
                Customer.phone.ilike(f"%{q}%"),
                Customer.email.ilike(f"%{q}%")
            )
        )

    customers = query.order_by(Customer.created_at.desc()).all()

    return jsonify([
        {
            "id": c.id,
            "organization_id": c.organization_id,
            "name": c.name,
            "phone": c.phone,
            "email": c.email,
            "gender": c.gender,
            "dob": c.dob.isoformat() if c.dob else None,
            "address": c.address,
            "tags": c.tags or "General",
            "notes": c.notes,
            "source": c.source or "Direct",
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "updated_at": c.updated_at.isoformat() if c.updated_at else None,
        }
        for c in customers
    ])


@customer_bp.route("", methods=["POST"])
@customer_bp.route("/create", methods=["POST"])
@jwt_required()
def create_customer():
    claims = get_jwt()
    role = claims.get("role")
    data = request.json or {}

    if role in ["Admin", "SuperAdmin"]:
        organization_id = data.get("organization_id") or claims.get("organization_id") or 1
    else:
        organization_id = int(claims.get("organization_id") or 0)

    if not data.get("name") or not data.get("phone"):
        return jsonify({"msg": "name and phone are required"}), 400

    phone = str(data["phone"]).strip()
    check_duplicate = data.get("check_duplicate", False)
    existing = Customer.query.filter_by(organization_id=int(organization_id), phone=phone).first()
    if existing and check_duplicate and not data.get("allow_duplicate", False):
        return jsonify({
            "msg": f"Patient with phone '{phone}' already registered in this organization",
            "existing_customer_id": existing.id,
            "existing_name": existing.name
        }), 409

    customer = Customer(
        organization_id=int(organization_id),
        name=data["name"],
        phone=phone,
        email=data.get("email"),
        gender=data.get("gender", "Female"),
        dob=data.get("dob"),
        address=data.get("address"),
        tags=data.get("tags", "General"),
        notes=data.get("notes"),
        source=data.get("source", "AppointoCare Web Intake")
    )
    db.session.add(customer)

    # Sync with Patient model if not already present
    from app.models import Patient
    patient = Patient.query.filter_by(organization_id=int(organization_id), phone=phone).first()
    if not patient:
        patient = Patient(
            organization_id=int(organization_id),
            name=data["name"],
            phone=phone,
            email=data.get("email"),
            gender=data.get("gender", "Female"),
            address=data.get("address")
        )
        db.session.add(patient)

    db.session.commit()

    return jsonify({
        "msg": "Customer created successfully",
        "customer_id": customer.id,
        "id": customer.id,
        "name": customer.name,
        "phone": customer.phone
    }), 201


@customer_bp.route("/<int:customer_id>", methods=["GET"])
@jwt_required()
def get_customer(customer_id):
    claims = get_jwt()
    role = claims.get("role")
    customer = Customer.query.get_or_404(customer_id)

    if role != "Admin" and customer.organization_id != int(claims.get("organization_id") or 0):
        return jsonify({"msg": "Unauthorized"}), 403

    return jsonify({
        "id": customer.id,
        "organization_id": customer.organization_id,
        "name": customer.name,
        "phone": customer.phone,
        "email": customer.email,
        "gender": customer.gender,
        "dob": customer.dob.isoformat() if customer.dob else None,
        "address": customer.address,
        "tags": customer.tags,
        "notes": customer.notes,
        "source": customer.source,
        "created_at": customer.created_at.isoformat() if customer.created_at else None,
        "updated_at": customer.updated_at.isoformat() if customer.updated_at else None,
    })


@customer_bp.route("/<int:customer_id>", methods=["PUT", "PATCH"])
@jwt_required()
def update_customer(customer_id):
    claims = get_jwt()
    role = claims.get("role")
    data = request.json or {}

    customer = Customer.query.get_or_404(customer_id)
    if role != "Admin" and customer.organization_id != int(claims.get("organization_id") or 0):
        return jsonify({"msg": "Unauthorized"}), 403

    if "name" in data:
        customer.name = data["name"]
    if "phone" in data:
        customer.phone = data["phone"]
    if "email" in data:
        customer.email = data["email"]
    if "gender" in data:
        customer.gender = data["gender"]
    if "dob" in data:
        customer.dob = data["dob"]
    if "address" in data:
        customer.address = data["address"]
    if "tags" in data:
        customer.tags = data["tags"]
    if "notes" in data:
        customer.notes = data["notes"]
    if "source" in data:
        customer.source = data["source"]

    db.session.commit()
    return jsonify({"msg": "Customer updated successfully", "id": customer.id})


@customer_bp.route("/<int:customer_id>", methods=["DELETE"])
@jwt_required()
def delete_customer(customer_id):
    claims = get_jwt()
    role = claims.get("role")
    customer = Customer.query.get_or_404(customer_id)

    if role != "Admin" and customer.organization_id != int(claims.get("organization_id") or 0):
        return jsonify({"msg": "Unauthorized"}), 403

    db.session.delete(customer)
    db.session.commit()
    return jsonify({"msg": "Customer deleted successfully"})


@customer_bp.route("/<int:customer_id>/timeline", methods=["GET"])
@jwt_required()
def get_customer_timeline(customer_id):
    claims = get_jwt()
    role = claims.get("role")
    customer = Customer.query.get_or_404(customer_id)

    if role != "Admin" and customer.organization_id != int(claims.get("organization_id") or 0):
        return jsonify({"msg": "Unauthorized"}), 403

    # Gather appointments
    appts = Appointment.query.filter(
        Appointment.organization_id == customer.organization_id,
        db.or_(Appointment.customer_phone == customer.phone, Appointment.customer_name == customer.name)
    ).order_by(Appointment.appointment_date.desc()).all()

    appt_ids = [a.id for a in appts]

    # Gather messages
    msgs = MessageLog.query.filter(
        MessageLog.organization_id == customer.organization_id,
        MessageLog.recipient_number == customer.phone
    ).order_by(MessageLog.created_at.desc()).all()

    # Gather clinical encounters, prescriptions, and diagnostics from IndustryRecord
    from app.models import IndustryRecord
    records = IndustryRecord.query.filter(
        IndustryRecord.organization_id == customer.organization_id,
        db.or_(
            IndustryRecord.customer_id == customer.id,
            IndustryRecord.appointment_id.in_(appt_ids) if appt_ids else False
        )
    ).order_by(IndustryRecord.created_at.desc()).all()

    # Gather billing transactions
    txns = AppointmentTransaction.query.filter(
        AppointmentTransaction.organization_id == customer.organization_id,
        AppointmentTransaction.appointment_id.in_(appt_ids) if appt_ids else False
    ).order_by(AppointmentTransaction.created_at.desc()).all()

    timeline = []
    for a in appts:
        timeline.append({
            "type": "appointment",
            "title": f"Appointment: {a.status}",
            "description": f"Scheduled on {a.appointment_date.strftime('%Y-%m-%d %H:%M') if a.appointment_date else 'N/A'}. Provider: {a.staff_name or 'General'} | Payment: {a.payment_status}",
            "date": a.appointment_date.isoformat() if a.appointment_date else a.created_at.isoformat(),
            "status": a.status,
            "payment_status": a.payment_status,
            "appointment_id": a.id
        })

    for m in msgs:
        timeline.append({
            "type": "whatsapp",
            "title": f"WhatsApp ({m.status})",
            "description": m.message_content,
            "date": m.created_at.isoformat() if m.created_at else None,
            "status": m.status
        })

    for r in records:
        rec_label = r.record_type.replace('_', ' ').title()
        timeline.append({
            "type": "clinical_record",
            "record_type": r.record_type,
            "title": f"{rec_label}: {r.title}",
            "description": f"Status: {r.status} | Practitioner: {r.created_by_user or 'Specialist'}",
            "date": r.created_at.isoformat() if r.created_at else None,
            "status": r.status,
            "record_id": r.id
        })

    for t in txns:
        timeline.append({
            "type": "billing",
            "title": f"Receipt: ₹{t.amount} ({t.payment_method})",
            "description": f"{t.transaction_type} | Status: {t.status}",
            "date": t.created_at.isoformat() if t.created_at else None,
            "status": t.status,
            "amount": t.amount,
            "transaction_id": t.id
        })

    timeline.sort(key=lambda x: x.get("date") or "", reverse=True)

    return jsonify({
        "customer": {
            "id": customer.id,
            "name": customer.name,
            "phone": customer.phone,
            "email": customer.email,
            "tags": customer.tags,
            "notes": customer.notes,
            "source": customer.source
        },
        "timeline": timeline,
        "total_appointments": len(appts),
        "total_messages": len(msgs),
        "total_clinical_records": len(records),
        "total_transactions": len(txns)
    })


@customer_bp.route("/history", methods=["GET"])
@jwt_required()
def get_customer_history():
    claims = get_jwt()
    role = claims.get("role")
    phone = request.args.get("phone")
    name = request.args.get("name")
    org_id = int(claims.get("organization_id") or 0) if role != "Admin" else request.args.get("organization_id")

    query = Appointment.query
    if org_id:
        query = query.filter(Appointment.organization_id == int(org_id))
    if phone:
        query = query.filter(Appointment.customer_phone.ilike(f"%{phone}%"))
    if name:
        query = query.filter(Appointment.customer_name.ilike(f"%{name}%"))

    appts = query.order_by(Appointment.appointment_date.desc()).limit(20).all()

    return jsonify([
        {
            "id": a.id,
            "customer_name": a.customer_name,
            "customer_phone": a.customer_phone,
            "appointment_date": a.appointment_date.isoformat() if a.appointment_date else None,
            "status": a.status,
            "payment_status": a.payment_status,
            "organization_id": a.organization_id
        }
        for a in appts
    ])


@customer_bp.route("/export", methods=["GET"])
@jwt_required()
def export_customers():
    claims = get_jwt()
    role = claims.get("role")
    
    query = Customer.query
    if role in ["Admin", "SuperAdmin"]:
        org_id = request.args.get("organization_id")
        if org_id and org_id != "ALL":
            query = query.filter_by(organization_id=int(org_id))
    else:
        scoped_org_id = int(claims.get("organization_id") or 0)
        query = query.filter_by(organization_id=scoped_org_id)

    tag = request.args.get("tag")
    if tag:
        query = query.filter(Customer.tags.ilike(f"%{tag}%"))

    q = request.args.get("q") or request.args.get("search")
    if q:
        query = query.filter(
            db.or_(
                Customer.name.ilike(f"%{q}%"),
                Customer.phone.ilike(f"%{q}%"),
                Customer.email.ilike(f"%{q}%")
            )
        )

    customers = query.order_by(Customer.created_at.desc()).all()

    # Record audit log
    try:
        user_id_val = claims.get("sub")
        org_id_for_log = int(claims.get("organization_id") or 0)
        audit = AuditLog(
            organization_id=org_id_for_log,
            user_id=int(user_id_val) if user_id_val and str(user_id_val).isdigit() else None,
            user_role=role,
            action="EXPORT_CUSTOMERS",
            entity="Customer",
            details=f"Exported {len(customers)} customer records (tag filter: {tag or 'None'}, search: {q or 'None'})",
            ip_address=request.remote_addr
        )
        db.session.add(audit)
        db.session.commit()
    except Exception:
        db.session.rollback()

    return jsonify({
        "count": len(customers),
        "exported_at": datetime.utcnow().isoformat(),
        "customers": [
            {
                "id": c.id,
                "organization_id": c.organization_id,
                "name": c.name,
                "phone": c.phone,
                "email": c.email,
                "gender": c.gender,
                "dob": c.dob.isoformat() if c.dob else None,
                "address": c.address,
                "tags": c.tags,
                "notes": c.notes,
                "source": c.source,
                "created_at": c.created_at.isoformat() if c.created_at else None
            }
            for c in customers
        ]
    })

