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
