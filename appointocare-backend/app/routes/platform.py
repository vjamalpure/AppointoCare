from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt

from app.models import Branch, Campaign, Notification, SectorTemplate, SubscriptionPlan, db
from app.security import get_organization_id, require_roles

platform_bp = Blueprint("platform_bp", __name__)
ORG_ROLES = ("Organization", "Manager", "Staff")


def _date(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def _tenant_query(model):
    organization_id = get_organization_id()
    if organization_id is None:
        return model.query.filter(False)
    return model.query.filter_by(organization_id=organization_id)


@platform_bp.route("/plans", methods=["GET"])
@require_roles("Admin")
def plans():
    return jsonify([{
        "id": p.id, "name": p.name, "description": p.description, "price": p.price,
        "billing_cycle": p.billing_cycle, "feature_limits": p.feature_limits,
        "is_active": p.is_active,
    } for p in SubscriptionPlan.query.order_by(SubscriptionPlan.name).all()])


@platform_bp.route("/plans", methods=["POST"])
@require_roles("Admin")
def create_plan():
    data = request.get_json() or {}
    if not data.get("name"):
        return jsonify({"msg": "name is required"}), 400
    plan = SubscriptionPlan(
        name=data["name"], description=data.get("description"),
        price=float(data.get("price", 0)), billing_cycle=data.get("billing_cycle", "monthly"),
        feature_limits=data.get("feature_limits", {}), is_active=bool(data.get("is_active", True)),
    )
    db.session.add(plan)
    db.session.commit()
    return jsonify({"id": plan.id, "msg": "Plan created"}), 201


@platform_bp.route("/templates", methods=["GET"])
@require_roles("Admin", *ORG_ROLES)
def templates():
    return jsonify([{
        "id": t.id, "name": t.name, "description": t.description,
        "services": t.services, "is_active": t.is_active,
    } for t in SectorTemplate.query.filter_by(is_active=True).order_by(SectorTemplate.name).all()])


@platform_bp.route("/templates", methods=["POST"])
@require_roles("Admin")
def create_template():
    data = request.get_json() or {}
    if not data.get("name"):
        return jsonify({"msg": "name is required"}), 400
    template = SectorTemplate(
        name=data["name"], description=data.get("description"),
        services=data.get("services", []), is_active=bool(data.get("is_active", True)),
    )
    db.session.add(template)
    db.session.commit()
    return jsonify({"id": template.id, "msg": "Sector template created"}), 201


@platform_bp.route("/campaigns", methods=["GET"])
@require_roles(*ORG_ROLES)
def campaigns():
    return jsonify([{
        "id": c.id, "name": c.name, "channel": c.channel, "message": c.message,
        "audience_filter": c.audience_filter, "status": c.status,
        "scheduled_at": c.scheduled_at.isoformat() if c.scheduled_at else None,
        "sent_at": c.sent_at.isoformat() if c.sent_at else None,
    } for c in _tenant_query(Campaign).order_by(Campaign.created_at.desc()).all()])


@platform_bp.route("/campaigns", methods=["POST"])
@require_roles(*ORG_ROLES)
def create_campaign():
    data = request.get_json() or {}
    if not data.get("name") or not data.get("message"):
        return jsonify({"msg": "name and message are required"}), 400
    campaign = Campaign(
        organization_id=get_organization_id(), name=data["name"],
        channel=data.get("channel", "WhatsApp"), message=data["message"],
        audience_filter=data.get("audience_filter", {}),
        status="Scheduled" if data.get("scheduled_at") else "Draft",
        scheduled_at=_date(data.get("scheduled_at")),
    )
    db.session.add(campaign)
    db.session.commit()
    return jsonify({"id": campaign.id, "msg": "Campaign created"}), 201


@platform_bp.route("/notifications", methods=["GET"])
@require_roles(*ORG_ROLES)
def notifications():
    return jsonify([{
        "id": n.id, "channel": n.channel, "title": n.title, "message": n.message,
        "status": n.status, "created_at": n.created_at.isoformat(),
    } for n in _tenant_query(Notification).order_by(Notification.created_at.desc()).limit(100).all()])


@platform_bp.route("/notifications/<int:notification_id>/read", methods=["POST"])
@require_roles(*ORG_ROLES)
def mark_notification_read(notification_id):
    notification = _tenant_query(Notification).filter_by(id=notification_id).first_or_404()
    notification.status = "read"
    notification.read_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"msg": "Notification marked as read"})


@platform_bp.route("/branches", methods=["GET", "POST"])
@require_roles(*ORG_ROLES)
def branches():
    organization_id = get_organization_id()
    if request.method == "GET":
        return jsonify([{
            "id": b.id, "name": b.name, "address": b.address, "phone": b.phone,
            "timezone": b.timezone, "is_active": b.is_active,
        } for b in _tenant_query(Branch).order_by(Branch.name).all()])
    data = request.get_json() or {}
    if not data.get("name"):
        return jsonify({"msg": "name is required"}), 400
    branch = Branch(
        organization_id=organization_id, name=data["name"], address=data.get("address"),
        phone=data.get("phone"), timezone=data.get("timezone", "UTC"),
        is_active=bool(data.get("is_active", True)),
    )
    db.session.add(branch)
    db.session.commit()
    return jsonify({"id": branch.id, "msg": "Branch created"}), 201


@platform_bp.route("/reports/summary", methods=["GET"])
@require_roles("Admin", *ORG_ROLES)
def report_summary():
    from app.models import Appointment, AppointmentTransaction, Customer

    query_org = request.args.get("organization_id", type=int) if get_jwt().get("role") == "Admin" else get_organization_id()
    appointment_query = Appointment.query
    customer_query = Customer.query
    transaction_query = AppointmentTransaction.query
    if query_org:
        appointment_query = appointment_query.filter_by(organization_id=query_org)
        customer_query = customer_query.filter_by(organization_id=query_org)
        transaction_query = transaction_query.filter_by(organization_id=query_org)
    return jsonify({
        "appointments": appointment_query.count(),
        "customers": customer_query.count(),
        "revenue": float(db.session.query(db.func.coalesce(db.func.sum(AppointmentTransaction.amount), 0)).filter(
            AppointmentTransaction.organization_id == query_org if query_org else True
        ).scalar() or 0),
    })
