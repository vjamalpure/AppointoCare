from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from app.models import db, Notification, Organization
from datetime import datetime

notifications_bp = Blueprint("notifications_bp", __name__)

ALLOWED_ROLES = [
    "Admin", "SuperAdmin", "Organization", "Manager", "Staff",
    "Doctor", "Therapist", "Stylist", "Advisor", "Analyst", "Underwriter",
    "Broker", "Consultant", "Specialist", "Counselor", "Partner",
    "Receptionist", "Agent", "Lawyer", "Nurse", "Accountant", "Assistant"
]


def _is_authorized(role, claims):
    return (
        role in ALLOWED_ROLES or
        role in ["Admin", "SuperAdmin"] or
        bool(claims.get("organization_id"))
    )


@notifications_bp.route("", methods=["GET"])
@jwt_required()
def get_notifications():
    claims = get_jwt()
    role = claims.get("role")
    if not _is_authorized(role, claims):
        return jsonify({"msg": "Unauthorized"}), 403

    query = Notification.query

    if role in ["Admin", "SuperAdmin"]:
        # Platform-wide or filtered by organization_id
        org_param = request.args.get("organization_id")
        if org_param and org_param != "all":
            query = query.filter_by(organization_id=int(org_param))
    else:
        org_id = int(claims.get("organization_id") or get_jwt_identity())
        query = query.filter_by(organization_id=org_id)

    category = request.args.get("category")
    if category and category != "all":
        query = query.filter(Notification.title.ilike(f"%{category}%") | Notification.message.ilike(f"%{category}%"))

    if request.args.get("unread_only") == "true":
        query = query.filter_by(status="unread")

    search = request.args.get("search")
    if search:
        query = query.filter(Notification.title.ilike(f"%{search}%") | Notification.message.ilike(f"%{search}%"))

    items = query.order_by(Notification.created_at.desc()).limit(150).all()

    notifs = []
    by_cat = {"booking": 0, "payment": 0, "organization": 0, "complaint": 0, "inquiry": 0, "triage": 0, "system": 0}
    unread_count = 0

    for n in items:
        is_read = n.status == "read"
        if not is_read:
            unread_count += 1

        # Categorize
        lower_txt = f"{n.title} {n.message}".lower()
        if "booking" in lower_txt or "appointment" in lower_txt:
            cat = "booking"
        elif "payment" in lower_txt or "invoice" in lower_txt or "fee" in lower_txt:
            cat = "payment"
        elif "complaint" in lower_txt:
            cat = "complaint"
        elif "triage" in lower_txt or "vitals" in lower_txt or "rx" in lower_txt:
            cat = "triage"
        elif "organization" in lower_txt or "tenant" in lower_txt:
            cat = "organization"
        else:
            cat = "system"

        by_cat[cat] = by_cat.get(cat, 0) + 1

        notifs.append({
            "id": n.id,
            "organization_id": n.organization_id,
            "category": cat,
            "title": n.title,
            "message": n.message,
            "is_read": is_read,
            "severity": "warning" if "alert" in lower_txt or "urgent" in lower_txt else ("success" if "confirmed" in lower_txt or "completed" in lower_txt else "info"),
            "timestamp": n.created_at.isoformat() if n.created_at else datetime.utcnow().isoformat()
        })

    return jsonify({
        "notifications": notifs,
        "unread_count": unread_count,
        "role": role,
        "stats": {
            "total": len(items),
            "unread": unread_count,
            "by_category": by_cat
        }
    })


@notifications_bp.route("/<int:notif_id>/read", methods=["POST"])
@jwt_required()
def mark_read(notif_id):
    claims = get_jwt()
    if not _is_authorized(claims.get("role"), claims):
        return jsonify({"msg": "Unauthorized"}), 403

    n = Notification.query.get_or_404(notif_id)
    n.status = "read"
    n.read_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"msg": "Marked as read", "id": n.id})


@notifications_bp.route("/mark-all-read", methods=["POST"])
@jwt_required()
def mark_all_read():
    claims = get_jwt()
    role = claims.get("role")
    if not _is_authorized(role, claims):
        return jsonify({"msg": "Unauthorized"}), 403

    query = Notification.query.filter_by(status="unread")
    if role not in ["Admin", "SuperAdmin"]:
        org_id = int(claims.get("organization_id") or get_jwt_identity())
        query = query.filter_by(organization_id=org_id)

    for n in query.all():
        n.status = "read"
        n.read_at = datetime.utcnow()
    db.session.commit()
    return jsonify({"msg": "All notifications marked as read"})


@notifications_bp.route("/<int:notif_id>", methods=["DELETE"])
@jwt_required()
def delete_notification(notif_id):
    claims = get_jwt()
    if not _is_authorized(claims.get("role"), claims):
        return jsonify({"msg": "Unauthorized"}), 403

    n = Notification.query.get_or_404(notif_id)
    db.session.delete(n)
    db.session.commit()
    return jsonify({"msg": "Notification deleted"})


@notifications_bp.route("/clear-all", methods=["DELETE"])
@jwt_required()
def clear_all():
    claims = get_jwt()
    role = claims.get("role")
    if not _is_authorized(role, claims):
        return jsonify({"msg": "Unauthorized"}), 403

    query = Notification.query.filter_by(status="read")
    if role not in ["Admin", "SuperAdmin"]:
        org_id = int(claims.get("organization_id") or get_jwt_identity())
        query = query.filter_by(organization_id=org_id)

    for n in query.all():
        db.session.delete(n)
    db.session.commit()
    return jsonify({"msg": "Read notifications cleared"})


@notifications_bp.route("/simulate", methods=["POST"])
@jwt_required()
def simulate_notification():
    claims = get_jwt()
    data = request.json or {}
    sim_type = data.get("type", "booking_new")
    org_id = int(data.get("organization_id") or claims.get("organization_id") or 1)

    title_map = {
        "booking_new": "New Appointment Confirmed",
        "booking_cancelled": "Appointment Cancellation Notice",
        "payment_success": "Payment Received via Razorpay",
        "triage_alert": "Urgent Triage Alert",
        "system_update": "Platform Security & Maintenance Advisory"
    }

    n = Notification(
        organization_id=org_id,
        recipient_type="organization",
        channel="in_app",
        title=title_map.get(sim_type, "Platform Notification"),
        message=f"Simulated test event for {sim_type} triggered at {datetime.utcnow().strftime('%I:%M %p')}.",
        status="unread",
        created_at=datetime.utcnow()
    )
    db.session.add(n)
    db.session.commit()
    return jsonify({"msg": "Notification simulated", "id": n.id}), 201
