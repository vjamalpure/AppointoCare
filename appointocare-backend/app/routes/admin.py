from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.models import db, Organization, Appointment, AppointmentTransaction, OrganizationTransaction, Admin, User
from app.utils.hash_helper import hash_password
from datetime import datetime
from sqlalchemy import extract


def parse_iso_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        return None


admin_bp = Blueprint("admin_bp", __name__)

# --------------------------------------
# Monthly Transaction Summary (for charts)
# --------------------------------------
@admin_bp.route("/transactions/summary", methods=["GET"])
@jwt_required()
def transactions_summary():
    claims = get_jwt()
    if claims.get("role") != "Admin":
        return jsonify({"msg": "Unauthorized"}), 403

    # Optional: filter by year
    year = request.args.get("year", datetime.utcnow().year, type=int)

    # Group by month for both OrganizationTransaction and AppointmentTransaction
    org_monthly = db.session.query(
        extract('month', OrganizationTransaction.created_at).label('month'),
        db.func.sum(OrganizationTransaction.amount).label('total')
    ).filter(
        extract('year', OrganizationTransaction.created_at) == year
    ).group_by('month').all()

    appt_monthly = db.session.query(
        extract('month', AppointmentTransaction.created_at).label('month'),
        db.func.sum(AppointmentTransaction.amount).label('total')
    ).filter(
        extract('year', AppointmentTransaction.created_at) == year
    ).group_by('month').all()

    # Merge both
    monthly_totals = {}
    for m, t in org_monthly:
        monthly_totals[m] = monthly_totals.get(m, 0) + (t or 0)
    for m, t in appt_monthly:
        monthly_totals[m] = monthly_totals.get(m, 0) + (t or 0)

    # Format for chart: [{month: 1, total: 1000}, ...]
    summary = [
        {"month": m, "total": monthly_totals[m]} for m in sorted(monthly_totals.keys())
    ]
    return jsonify(summary)

# --------------------------------------
# Admin Dashboard Summary
# --------------------------------------
@admin_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def admin_dashboard():
    claims = get_jwt()
    if claims.get("role") != "Admin":
        return jsonify({"msg": "Unauthorized"}), 403

    total_orgs = Organization.query.count()
    total_appointments = Appointment.query.count()
    booked = Appointment.query.filter_by(status="Booked").count()
    completed = Appointment.query.filter_by(status="Completed").count()
    cancelled = Appointment.query.filter_by(status="Cancelled").count()

    total_org_transactions = db.session.query(db.func.sum(OrganizationTransaction.amount)).scalar() or 0
    total_appt_transactions = db.session.query(db.func.sum(AppointmentTransaction.amount)).scalar() or 0
    total_transactions = total_org_transactions + total_appt_transactions

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_org_txn_count = db.session.query(db.func.count(OrganizationTransaction.id)).filter(
        OrganizationTransaction.created_at >= today_start
    ).scalar() or 0
    today_appt_txn_count = db.session.query(db.func.count(AppointmentTransaction.id)).filter(
        AppointmentTransaction.created_at >= today_start
    ).scalar() or 0
    today_transactions = today_org_txn_count + today_appt_txn_count

    today_org_amount = db.session.query(db.func.sum(OrganizationTransaction.amount)).filter(
        OrganizationTransaction.created_at >= today_start
    ).scalar() or 0
    today_appt_amount = db.session.query(db.func.sum(AppointmentTransaction.amount)).filter(
        AppointmentTransaction.created_at >= today_start
    ).scalar() or 0

    active_orgs = Organization.query.filter_by(subscription_status='Active').count()
    paused_orgs = Organization.query.filter_by(subscription_status='Paused').count()

    return jsonify({
        "total_organizations": total_orgs,
        "active_organizations": active_orgs,
        "paused_organizations": paused_orgs,
        "appointments": {
            "total": total_appointments,
            "booked": booked,
            "completed": completed,
            "cancelled": cancelled
        },
        "total_transactions": total_transactions,
        "today_transactions": today_transactions,
        "today_transaction_amount": today_org_amount + today_appt_amount
    })


# --------------------------------------
# Create Organization
# --------------------------------------
@admin_bp.route("/organization/create", methods=["POST"])
@jwt_required()
def create_organization():
    claims = get_jwt()
    if claims.get("role") != "Admin":
        return jsonify({"msg": "Unauthorized"}), 403

    data = request.json or {}
    org = Organization(
        name=data["name"],
        code=data["code"],
        sector=data["sector"],
        username=data["username"],
        password=hash_password(data["password"]),
        subscription_status=data.get("subscription_status", "Active"),
        subscription_plan=data.get("subscription_plan", "Basic")
    )
    db.session.add(org)
    db.session.commit()
    return jsonify({"msg": "Organization created", "organization_id": org.id}), 201


# --------------------------------------
# Update Organization
# --------------------------------------
@admin_bp.route("/organization/<int:org_id>/update", methods=["PATCH"])
@jwt_required()
def update_organization(org_id):
    claims = get_jwt()
    if claims.get("role") != "Admin":
        return jsonify({"msg": "Unauthorized"}), 403

    org = Organization.query.get_or_404(org_id)
    data = request.json or {}

    if "name" in data: org.name = data["name"]
    if "username" in data: org.username = data["username"]
    if "password" in data: org.password = hash_password(data["password"])
    if "sector" in data: org.sector = data["sector"]
    if "subscription_status" in data and data["subscription_status"] in ["Active","Paused","Stopped"]:
        org.subscription_status = data["subscription_status"]
    if "status" in data and data["status"] in ["Active","Paused","Stopped"]:
        org.subscription_status = data["status"]
    if "subscription_plan" in data:
        org.subscription_plan = data["subscription_plan"]
    if "subscription_start" in data:
        parsed = parse_iso_date(data["subscription_start"])
        if parsed:
            org.subscription_start = parsed
    if "subscription_end" in data:
        parsed = parse_iso_date(data["subscription_end"])
        if parsed:
            org.subscription_end = parsed
    if "next_billing_date" in data:
        parsed = parse_iso_date(data["next_billing_date"])
        if parsed:
            org.next_billing_date = parsed

    db.session.commit()
    return jsonify({"msg": "Organization updated successfully"})


# --------------------------------------
# Delete Organization
# --------------------------------------
@admin_bp.route("/organization/<int:org_id>/delete", methods=["DELETE"])
@jwt_required()
def delete_organization(org_id):
    claims = get_jwt()
    if claims.get("role") != "Admin":
        return jsonify({"msg": "Unauthorized"}), 403

    org = Organization.query.get_or_404(org_id)
    db.session.delete(org)
    db.session.commit()
    return jsonify({"msg": "Organization deleted successfully"})


# --------------------------------------
# List All Organizations
# --------------------------------------
@admin_bp.route("/organizations", methods=["GET"])
@jwt_required()
def list_organizations():
    claims = get_jwt()
    if claims.get("role") != "Admin":
        return jsonify({"msg": "Unauthorized"}), 403

    orgs = Organization.query.all()
    result = []
    for o in orgs:
        result.append({
            "id": o.id,
            "name": o.name,
            "code": o.code,
            "sector": o.sector,
            "subscription_status": o.subscription_status,
            "subscription_plan": o.subscription_plan,
            "subscription_start": o.subscription_start.isoformat() if o.subscription_start else None,
            "subscription_end": o.subscription_end.isoformat() if o.subscription_end else None,
            "next_billing_date": o.next_billing_date.isoformat() if o.next_billing_date else None,
            "user_count": User.query.filter_by(organization_id=o.id).count(),
            "created_at": o.created_at.isoformat(),
            "updated_at": o.updated_at.isoformat() if o.updated_at else None
        })
    return jsonify(result)


# --------------------------------------
# View All Subscriptions
@admin_bp.route("/subscriptions", methods=["GET"])
@jwt_required()
def list_subscriptions():
    claims = get_jwt()
    if claims.get("role") != "Admin":
        return jsonify({"msg": "Unauthorized"}), 403

    orgs = Organization.query.all()
    result = []
    for o in orgs:
        result.append({
            "id": o.id,
            "organization_id": o.id,
            "organization_name": o.name,
            "plan": o.subscription_plan,
            "status": o.subscription_status,
            "start_date": o.subscription_start.isoformat() if o.subscription_start else None,
            "end_date": o.subscription_end.isoformat() if o.subscription_end else None,
            "next_billing_date": o.next_billing_date.isoformat() if o.next_billing_date else None,
        })
    return jsonify(result)


# --------------------------------------
# Organization Users
# --------------------------------------
@admin_bp.route("/organization/<int:org_id>/users", methods=["GET"])
@jwt_required()
def organization_users(org_id):
    claims = get_jwt()
    if claims.get("role") != "Admin":
        return jsonify({"msg": "Unauthorized"}), 403

    users = User.query.filter_by(organization_id=org_id).all()
    result = [
        {
            "id": u.id,
            "username": u.username,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat(),
            "updated_at": u.updated_at.isoformat() if u.updated_at else None
        }
        for u in users
    ]
    return jsonify(result)


@admin_bp.route("/organization/<int:org_id>/user/create", methods=["POST"])
@jwt_required()
def create_organization_user(org_id):
    claims = get_jwt()
    if claims.get("role") != "Admin":
        return jsonify({"msg": "Unauthorized"}), 403

    data = request.json or {}
    org = Organization.query.get_or_404(org_id)
    user = User(
        organization_id=org.id,
        username=data["username"],
        password=hash_password(data["password"]),
        role=data.get("role", "Staff"),
        is_active=data.get("is_active", True)
    )
    db.session.add(user)
    db.session.commit()
    return jsonify({"msg": "Organization user created", "user_id": user.id}), 201


@admin_bp.route("/organization/<int:org_id>/user/<int:user_id>/update", methods=["PATCH"])
@jwt_required()
def update_organization_user(org_id, user_id):
    claims = get_jwt()
    if claims.get("role") != "Admin":
        return jsonify({"msg": "Unauthorized"}), 403

    user = User.query.filter_by(id=user_id, organization_id=org_id).first_or_404()
    data = request.json or {}
    if "username" in data:
        user.username = data["username"]
    if "password" in data and data["password"]:
        user.password = hash_password(data["password"])
    if "role" in data:
        user.role = data["role"]
    if "is_active" in data:
        user.is_active = bool(data["is_active"])

    db.session.commit()
    return jsonify({"msg": "Organization user updated successfully"})


@admin_bp.route("/organization/<int:org_id>/user/<int:user_id>/delete", methods=["DELETE"])
@jwt_required()
def delete_organization_user(org_id, user_id):
    claims = get_jwt()
    if claims.get("role") != "Admin":
        return jsonify({"msg": "Unauthorized"}), 403

    user = User.query.filter_by(id=user_id, organization_id=org_id).first_or_404()
    db.session.delete(user)
    db.session.commit()
    return jsonify({"msg": "Organization user deleted successfully"})


# --------------------------------------
# View All Appointments
# --------------------------------------
@admin_bp.route("/appointments", methods=["GET"])
@jwt_required()
def view_appointments():
    claims = get_jwt()
    if claims.get("role") != "Admin":
        return jsonify({"msg": "Unauthorized"}), 403

    org_id = request.args.get("organization_id")
    if org_id:
        appointments = Appointment.query.filter_by(organization_id=org_id).all()
    else:
        appointments = Appointment.query.all()

    result = []
    for a in appointments:
        result.append({
            "id": a.id,
            "customer_name": a.customer_name,
            "customer_phone": a.customer_phone,
            "appointment_date": a.appointment_date.isoformat(),
            "status": a.status,
            "payment_status": a.payment_status,
            "organization_id": a.organization_id,
            "created_at": a.created_at.isoformat(),
            "updated_at": a.updated_at.isoformat() if a.updated_at else None
        })
    return jsonify(result)


# --------------------------------------
# View All Transactions
# --------------------------------------
@admin_bp.route("/transactions", methods=["GET"])
@jwt_required()
def view_transactions():
    claims = get_jwt()
    if claims.get("role") != "Admin":
        return jsonify({"msg": "Unauthorized"}), 403

    org_id = request.args.get("organization_id")
    results = []

    # Organization-level transactions
    if org_id:
        org_txns = OrganizationTransaction.query.filter_by(organization_id=org_id).all()
        appt_txns = (
            db.session.query(AppointmentTransaction)
            .join(Appointment)
            .filter(Appointment.organization_id == org_id)
            .all()
        )
    else:
        org_txns = OrganizationTransaction.query.all()
        appt_txns = AppointmentTransaction.query.all()

    for t in org_txns:
        org = Organization.query.get(t.organization_id)
        results.append({
            "id": t.id,
            "organization_id": t.organization_id,
            "organization_name": org.name if org else None,
            "amount": t.amount,
            "transaction_type": t.transaction_type,
            "payment_method": t.payment_method,
            "status": t.status,
            "processed_by_type": t.processed_by_type,
            "created_at": t.created_at.isoformat(),
        })

    for t in appt_txns:
        org = Organization.query.get(t.organization_id)
        results.append({
            "id": t.id,
            "appointment_id": t.appointment_id,
            "organization_id": t.organization_id,
            "organization_name": org.name if org else None,
            "amount": t.amount,
            "transaction_type": t.transaction_type,
            "payment_method": t.payment_method,
            "status": t.status,
            "processed_by_type": t.processed_by_type,
            "created_at": t.created_at.isoformat(),
        })

    return jsonify(results)


# --------------------------------------
# Organization Settings
# --------------------------------------
@admin_bp.route("/organization/<int:org_id>/settings", methods=["PATCH"])
@jwt_required()
def update_organization_settings(org_id):
    claims = get_jwt()
    if claims.get("role") not in ["Admin", "SuperAdmin"]:
        return jsonify({"msg": "Unauthorized"}), 403
    org = Organization.query.get_or_404(org_id)
    data = request.json or {}
    if "name" in data: org.name = data["name"]
    if "sector" in data: org.sector = data["sector"]
    if "subscription_plan" in data: org.subscription_plan = data["subscription_plan"]
    if "subscription_status" in data: org.subscription_status = data["subscription_status"]
    db.session.commit()
    return jsonify({"msg": "Organization settings updated successfully"})


# --------------------------------------
# Toggle User Status
# --------------------------------------
@admin_bp.route("/organization/<int:org_id>/user/<int:user_id>/toggle-status", methods=["PATCH"])
@jwt_required()
def toggle_user_status(org_id, user_id):
    claims = get_jwt()
    if claims.get("role") not in ["Admin", "SuperAdmin"]:
        return jsonify({"msg": "Unauthorized"}), 403
    user = User.query.filter_by(id=user_id, organization_id=org_id).first_or_404()
    data = request.json or {}
    user.is_active = data.get("is_active", not user.is_active)
    db.session.commit()
    return jsonify({"msg": "User status updated", "is_active": user.is_active})


# --------------------------------------
# Broadcast Notification
# --------------------------------------
@admin_bp.route("/broadcast-notification", methods=["POST"])
@jwt_required()
def broadcast_notification():
    claims = get_jwt()
    if claims.get("role") not in ["Admin", "SuperAdmin"]:
        return jsonify({"msg": "Unauthorized"}), 403
    data = request.json or {}
    title = data.get("title", "Platform Announcement")
    message = data.get("message", "")
    target_org_id = data.get("organization_id")
    from app.models import Notification
    if target_org_id and target_org_id != "all":
        orgs = [Organization.query.get(int(target_org_id))]
    else:
        orgs = Organization.query.all()
    created = 0
    for org in orgs:
        if org:
            n = Notification(
                organization_id=org.id,
                title=title,
                message=message,
                status="unread"
            )
            db.session.add(n)
            created += 1
    db.session.commit()
    return jsonify({"msg": f"Broadcast sent to {created} organizations", "count": created})


# --------------------------------------
# Analytics Reports
# --------------------------------------
@admin_bp.route("/analytics-reports", methods=["GET"])
@jwt_required()
def analytics_reports():
    claims = get_jwt()
    if claims.get("role") not in ["Admin", "SuperAdmin"]:
        return jsonify({"msg": "Unauthorized"}), 403
    sector = request.args.get("sector")
    org_id = request.args.get("organization_id", type=int)
    query = Organization.query
    if sector and sector != "ALL":
        query = query.filter_by(sector=sector)
    if org_id:
        query = query.filter_by(id=org_id)
    orgs = query.all()
    org_ids = [o.id for o in orgs]
    appt_query = Appointment.query.filter(Appointment.organization_id.in_(org_ids)) if org_ids else Appointment.query.filter(False)
    total_appts = appt_query.count()
    completed_appts = appt_query.filter_by(status="Completed").count()
    cancelled_appts = appt_query.filter_by(status="Cancelled").count()
    total_rev = db.session.query(db.func.sum(AppointmentTransaction.amount)).join(Appointment).filter(Appointment.organization_id.in_(org_ids)).scalar() or 0 if org_ids else 0
    return jsonify({
        "total_organizations": len(orgs),
        "total_appointments": total_appts,
        "completed_appointments": completed_appts,
        "cancelled_appointments": cancelled_appts,
        "total_revenue": total_rev,
        "organizations": [{"id": o.id, "name": o.name, "sector": o.sector, "status": o.subscription_status} for o in orgs]
    })


# -----------------------------------------------------------------------------
# Superadmin Service Controls: Independent Feature Flag Toggles (WhatsApp & Razorpay)
# -----------------------------------------------------------------------------
@admin_bp.route("/tenants/<int:tenant_id>/toggle-service", methods=["PATCH"])
@admin_bp.route("/organizations/<int:tenant_id>/toggle-service", methods=["PATCH"])
@jwt_required()
def toggle_tenant_service(tenant_id):
    claims = get_jwt()
    if claims.get("role") not in ["Admin", "SuperAdmin"]:
        return jsonify({"msg": "Unauthorized. SuperAdmin privilege required."}), 403

    from app.models import WhatsAppConfig, PaymentConfig, ServiceStatus, AuditLog
    data = request.json or {}
    service_type = (data.get("service") or "").lower()
    new_status = (data.get("status") or "").upper()
    reason = data.get("reason") or "Superadmin administrative toggle"

    if service_type not in ["whatsapp", "razorpay"]:
        return jsonify({"msg": "Invalid service. Must be 'whatsapp' or 'razorpay'"}), 400

    if new_status not in ServiceStatus.CHOICES:
        return jsonify({"msg": f"Invalid status. Must be one of {ServiceStatus.CHOICES}"}), 400

    org = Organization.query.get_or_404(tenant_id)

    if service_type == "whatsapp":
        cfg = WhatsAppConfig.query.filter_by(tenant_id=tenant_id).first()
        if not cfg:
            cfg = WhatsAppConfig(tenant_id=tenant_id, waba_id=f"waba_{tenant_id}")
            db.session.add(cfg)
        cfg.service_status = new_status
        cfg.suspension_reason = reason if new_status != ServiceStatus.ACTIVE else None
        db.session.commit()
        response_payload = {
            "tenant_id": tenant_id,
            "tenant_name": org.name,
            "service": "whatsapp",
            "status": cfg.service_status,
            "waba_id": cfg.waba_id,
            "phone_number_id": cfg.phone_number_id,
            "suspension_reason": cfg.suspension_reason,
            "updated_at": cfg.updated_at.isoformat() if cfg.updated_at else None
        }
    else:
        cfg = PaymentConfig.query.filter_by(tenant_id=tenant_id).first()
        if not cfg:
            cfg = PaymentConfig(tenant_id=tenant_id, razorpay_account_id=f"acc_{tenant_id}")
            db.session.add(cfg)
        cfg.service_status = new_status
        cfg.suspension_reason = reason if new_status != ServiceStatus.ACTIVE else None
        db.session.commit()
        response_payload = {
            "tenant_id": tenant_id,
            "tenant_name": org.name,
            "service": "razorpay",
            "status": cfg.service_status,
            "razorpay_account_id": cfg.razorpay_account_id,
            "platform_commission_rate": cfg.platform_commission_rate,
            "suspension_reason": cfg.suspension_reason,
            "updated_at": cfg.updated_at.isoformat() if cfg.updated_at else None
        }

    # Audit Trail
    audit = AuditLog(
        organization_id=tenant_id,
        user_role=claims.get("role"),
        action="SERVICE_STATUS_CHANGED",
        entity=f"{service_type.upper()}_CONFIG",
        entity_id=cfg.id,
        details=f"Service {service_type} set to {new_status}. Reason: {reason}",
        ip_address=request.remote_addr
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({
        "msg": f"Service '{service_type}' successfully updated to {new_status}",
        "config": response_payload
    }), 200


@admin_bp.route("/tenants/<int:tenant_id>/services-status", methods=["GET"])
@admin_bp.route("/organizations/<int:tenant_id>/services-status", methods=["GET"])
@jwt_required()
def get_tenant_services_status(tenant_id):
    claims = get_jwt()
    if claims.get("role") not in ["Admin", "SuperAdmin"]:
        return jsonify({"msg": "Unauthorized"}), 403

    from app.models import WhatsAppConfig, PaymentConfig
    org = Organization.query.get_or_404(tenant_id)
    w_cfg = WhatsAppConfig.query.filter_by(tenant_id=tenant_id).first()
    p_cfg = PaymentConfig.query.filter_by(tenant_id=tenant_id).first()

    return jsonify({
        "tenant_id": tenant_id,
        "tenant_name": org.name,
        "services": {
            "whatsapp": {
                "status": w_cfg.service_status if w_cfg else "INACTIVE",
                "waba_id": w_cfg.waba_id if w_cfg else None,
                "phone_number_id": w_cfg.phone_number_id if w_cfg else None,
                "credit_line": w_cfg.meta_credit_line_status if w_cfg else "SHARED_MASTER",
                "suspension_reason": w_cfg.suspension_reason if w_cfg else None
            },
            "razorpay": {
                "status": p_cfg.service_status if p_cfg else "INACTIVE",
                "razorpay_account_id": p_cfg.razorpay_account_id if p_cfg else None,
                "commission_rate": p_cfg.platform_commission_rate if p_cfg else 0.05,
                "suspension_reason": p_cfg.suspension_reason if p_cfg else None
            }
        }
    })


