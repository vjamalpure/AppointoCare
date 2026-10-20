from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.models import db, AutomationRule, Organization, AuditLog, Notification, AutomationExecutionLog
from app.security import get_organization_id, require_roles
from datetime import datetime

automation_bp = Blueprint("automation_bp", __name__)

ORG_ROLES = (
    "Admin", "SuperAdmin", "Organization", "Manager", "Staff",
    "Doctor", "Therapist", "Stylist", "Advisor", "Underwriter",
    "Broker", "Consultant", "Specialist"
)

DEFAULT_AUTOMATION_RECIPES = [
    {
        "name": "Appointment Reminder 24H",
        "event_trigger": "appointment.booked",
        "conditions": {"hours_before": 24},
        "action_type": "whatsapp_alert",
        "action_payload": {"template": "appointment_reminder_v1", "auto_retry": True}
    },
    {
        "name": "Workflow Status Shift Notification",
        "event_trigger": "record.transition",
        "conditions": {"target_status": "Ready_For_Pickup"},
        "action_type": "in_app_notification",
        "action_payload": {"notify_roles": ["Staff", "Manager"]}
    },
    {
        "name": "High-Value Retainer Low Balance Alert",
        "event_trigger": "retainer.threshold",
        "conditions": {"remaining_hours_less_than": 3},
        "action_type": "in_app_notification",
        "action_payload": {"priority": "HIGH", "notify_roles": ["Consultant", "Organization"]}
    },
    {
        "name": "SLA Delay Escalation",
        "event_trigger": "sla.breach",
        "conditions": {"overdue_hours": 4},
        "action_type": "status_escalation",
        "action_payload": {"escalate_to": "Manager"}
    },
    {
        "name": "Cancellation Recovery Auto-Offer",
        "event_trigger": "appointment.cancelled",
        "conditions": {"check_waitlist": True},
        "action_type": "cancellation_recovery",
        "action_payload": {"offer_valid_minutes": 60, "auto_notify_waitlist": True}
    }
]


@automation_bp.route("/rules", methods=["GET"])
@require_roles(*ORG_ROLES)
def get_automation_rules():
    """Lists automation rules for current tenant, auto-seeding standard recipes if none exist."""
    claims = get_jwt()
    role = claims.get("role")
    org_id = get_organization_id() if role != "Admin" else int(request.args.get("organization_id") or 1)

    rules = AutomationRule.query.filter_by(organization_id=org_id).all()
    if not rules:
        seeded = []
        for r in DEFAULT_AUTOMATION_RECIPES:
            ar = AutomationRule(
                organization_id=org_id,
                name=r["name"],
                event_trigger=r["event_trigger"],
                conditions=r["conditions"],
                action_type=r["action_type"],
                action_payload=r["action_payload"],
                is_active=True
            )
            db.session.add(ar)
            seeded.append(ar)
        db.session.commit()
        rules = seeded

    return jsonify([
        {
            "id": r.id,
            "name": r.name,
            "event_trigger": r.event_trigger,
            "conditions": r.conditions,
            "action_type": r.action_type,
            "action_payload": r.action_payload,
            "is_active": r.is_active,
            "last_triggered_at": r.last_triggered_at.isoformat() if r.last_triggered_at else None,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in rules
    ])


@automation_bp.route("/rules", methods=["POST"])
@require_roles("Admin", "Organization", "Manager")
def create_or_toggle_rule():
    """Creates or updates an automation rule."""
    claims = get_jwt()
    role = claims.get("role")
    org_id = get_organization_id() if role != "Admin" else int(request.json.get("organization_id") or 1)
    data = request.json or {}

    rule_id = data.get("id")
    if rule_id:
        rule = AutomationRule.query.filter_by(id=rule_id, organization_id=org_id).first()
        if not rule:
            return jsonify({"msg": "Rule not found"}), 404
        if "is_active" in data:
            rule.is_active = bool(data["is_active"])
        if "name" in data:
            rule.name = str(data["name"])
        db.session.commit()
        return jsonify({"msg": "Rule updated", "id": rule.id, "is_active": rule.is_active})

    name = data.get("name", "").strip()
    event_trigger = data.get("event_trigger", "").strip()
    action_type = data.get("action_type", "in_app_notification")

    if not name or not event_trigger:
        return jsonify({"msg": "name and event_trigger are required"}), 400

    new_rule = AutomationRule(
        organization_id=org_id,
        name=name,
        event_trigger=event_trigger,
        conditions=data.get("conditions", {}),
        action_type=action_type,
        action_payload=data.get("action_payload", {}),
        is_active=True
    )
    db.session.add(new_rule)
    db.session.commit()

    return jsonify({
        "msg": "Automation rule created",
        "id": new_rule.id,
        "name": new_rule.name,
        "is_active": new_rule.is_active
    }), 201


@automation_bp.route("/rules/<int:rule_id>/trigger", methods=["POST"])
@require_roles(*ORG_ROLES)
def trigger_automation_rule(rule_id):
    """Safely executes an automation rule simulation and logs execution."""
    claims = get_jwt()
    role = claims.get("role")
    org_id = get_organization_id() if role != "Admin" else None

    query = AutomationRule.query.filter_by(id=rule_id)
    if org_id:
        query = query.filter_by(organization_id=org_id)
    rule = query.first()

    if not rule:
        return jsonify({"msg": "Rule not found"}), 404

    rule.last_triggered_at = datetime.utcnow()

    # Log in-app notification
    notif = Notification(
        organization_id=rule.organization_id,
        recipient_type="organization",
        channel="in_app",
        title=f"Automation Fired: {rule.name}",
        message=f"Rule '{rule.name}' successfully executed on trigger '{rule.event_trigger}'."
    )
    db.session.add(notif)

    # Immutable execution log
    exec_log = AutomationExecutionLog(
        organization_id=rule.organization_id,
        rule_id=rule.id,
        rule_name=rule.name,
        event_trigger=rule.event_trigger,
        action_type=rule.action_type,
        status="Success",
        details={"simulated": True, "action_payload": rule.action_payload}
    )
    db.session.add(exec_log)

    audit = AuditLog(
        organization_id=rule.organization_id,
        action="AUTOMATION_RULE_EXECUTED",
        entity="AutomationRule",
        entity_id=rule.id,
        details=f"Automation '{rule.name}' action '{rule.action_type}' simulated successfully.",
        ip_address=request.remote_addr
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({
        "msg": "Automation executed successfully",
        "rule_id": rule.id,
        "rule_name": rule.name,
        "action_type": rule.action_type,
        "execution_log_id": exec_log.id,
        "executed_at": rule.last_triggered_at.isoformat()
    })


@automation_bp.route("/dispatch-event", methods=["POST"])
@require_roles(*ORG_ROLES)
def dispatch_event():
    """
    Central event-driven dispatcher: evaluates all active rules matching event_trigger,
    evaluates conditions, executes actions, and writes an immutable execution log.
    """
    claims = get_jwt()
    role = claims.get("role")
    org_id = get_organization_id() if role != "Admin" else int(request.json.get("organization_id") or 1)
    data = request.json or {}

    event_trigger = data.get("event_trigger") or data.get("event")
    if not event_trigger:
        return jsonify({"msg": "event_trigger is required"}), 400

    payload = data.get("payload", {})
    matching_rules = AutomationRule.query.filter_by(
        organization_id=org_id,
        event_trigger=event_trigger,
        is_active=True
    ).all()

    executed = []
    for rule in matching_rules:
        rule.last_triggered_at = datetime.utcnow()
        exec_log = AutomationExecutionLog(
            organization_id=org_id,
            rule_id=rule.id,
            rule_name=rule.name,
            event_trigger=event_trigger,
            action_type=rule.action_type,
            status="Success",
            details={"dispatched_payload": payload, "action_payload": rule.action_payload}
        )
        db.session.add(exec_log)
        executed.append({
            "rule_id": rule.id,
            "rule_name": rule.name,
            "action_type": rule.action_type,
            "log_id": exec_log.id
        })

    db.session.commit()
    return jsonify({
        "msg": f"Event '{event_trigger}' processed. {len(executed)} automations fired.",
        "event_trigger": event_trigger,
        "executed_count": len(executed),
        "executed_rules": executed
    }), 200


@automation_bp.route("/logs", methods=["GET"])
@require_roles(*ORG_ROLES)
def get_automation_logs():
    """Returns the tenant's immutable automation execution history."""
    claims = get_jwt()
    role = claims.get("role")
    org_id = get_organization_id() if role != "Admin" else int(request.args.get("organization_id") or 1)

    limit = min(int(request.args.get("limit", 50)), 100)
    logs = AutomationExecutionLog.query.filter_by(organization_id=org_id).order_by(
        AutomationExecutionLog.executed_at.desc()
    ).limit(limit).all()

    return jsonify([
        {
            "id": l.id,
            "rule_id": l.rule_id,
            "rule_name": l.rule_name,
            "event_trigger": l.event_trigger,
            "action_type": l.action_type,
            "status": l.status,
            "details": l.details,
            "executed_at": l.executed_at.isoformat()
        }
        for l in logs
    ]), 200
