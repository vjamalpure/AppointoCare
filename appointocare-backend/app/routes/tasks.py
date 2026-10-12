from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from app.models import db, TaskItem, Customer, Appointment, AuditLog
from datetime import datetime, timedelta

tasks_bp = Blueprint("tasks_bp", __name__)

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


@tasks_bp.route("", methods=["GET"])
@tasks_bp.route("/all", methods=["GET"])
@jwt_required()
def get_tasks():
    claims = get_jwt()
    if claims.get("role") not in ALLOWED_ROLES:
        return jsonify({"msg": "Unauthorized"}), 403

    org_id = _get_org_id()
    query = TaskItem.query.filter_by(organization_id=org_id)

    status = request.args.get("status")
    if status and status != "ALL":
        query = query.filter_by(status=status)

    priority = request.args.get("priority")
    if priority and priority != "ALL":
        query = query.filter_by(priority=priority)

    assigned_to = request.args.get("assigned_to")
    if assigned_to:
        query = query.filter(TaskItem.assigned_to_name.ilike(f"%{assigned_to}%"))

    customer_id = request.args.get("customer_id")
    if customer_id:
        query = query.filter_by(customer_id=int(customer_id))

    q = request.args.get("q")
    if q:
        query = query.filter(
            db.or_(
                TaskItem.title.ilike(f"%{q}%"),
                TaskItem.description.ilike(f"%{q}%"),
                TaskItem.tags.ilike(f"%{q}%")
            )
        )

    tasks = query.order_by(TaskItem.created_at.desc()).all()

    # Automatically check and mark overdue items
    now = datetime.utcnow()
    results = []
    for t in tasks:
        is_overdue = t.status not in ["Completed", "Cancelled"] and t.due_date and t.due_date < now
        if is_overdue and t.status != "Overdue":
            t.status = "Overdue"
            db.session.add(t)

        results.append({
            "id": t.id,
            "organization_id": t.organization_id,
            "title": t.title,
            "description": t.description,
            "priority": t.priority,
            "status": "Overdue" if is_overdue else t.status,
            "assigned_to_name": t.assigned_to_name or "Unassigned",
            "customer_id": t.customer_id,
            "appointment_id": t.appointment_id,
            "due_date": t.due_date.isoformat() if t.due_date else None,
            "reminder_at": t.reminder_at.isoformat() if t.reminder_at else None,
            "escalation_level": t.escalation_level,
            "completed_at": t.completed_at.isoformat() if t.completed_at else None,
            "tags": t.tags,
            "created_at": t.created_at.isoformat() if t.created_at else None
        })

    db.session.commit()
    return jsonify(results), 200


@tasks_bp.route("", methods=["POST"])
@jwt_required()
def create_task():
    claims = get_jwt()
    if claims.get("role") not in ALLOWED_ROLES:
        return jsonify({"msg": "Unauthorized"}), 403

    org_id = _get_org_id()
    data = request.json or {}

    title = data.get("title", "").strip()
    if not title:
        return jsonify({"msg": "title is required"}), 400

    due_date = None
    if data.get("due_date"):
        try:
            d_str = data["due_date"].replace("Z", "+00:00")
            due_date = datetime.fromisoformat(d_str)
        except Exception:
            due_date = datetime.utcnow() + timedelta(days=2)

    task = TaskItem(
        organization_id=org_id,
        title=title,
        description=data.get("description"),
        priority=data.get("priority", "Medium"),
        status="Pending",
        assigned_to_user_id=data.get("assigned_to_user_id"),
        assigned_to_name=data.get("assigned_to_name", "Unassigned"),
        customer_id=data.get("customer_id"),
        appointment_id=data.get("appointment_id"),
        due_date=due_date,
        tags=data.get("tags", "General")
    )
    db.session.add(task)
    db.session.commit()

    return jsonify({
        "msg": "Task created successfully",
        "task": {
            "id": task.id,
            "title": task.title,
            "priority": task.priority,
            "status": task.status,
            "assigned_to_name": task.assigned_to_name,
            "due_date": task.due_date.isoformat() if task.due_date else None
        }
    }), 201


@tasks_bp.route("/<int:task_id>", methods=["PUT"])
@jwt_required()
def update_task(task_id):
    claims = get_jwt()
    if claims.get("role") not in ALLOWED_ROLES:
        return jsonify({"msg": "Unauthorized"}), 403

    org_id = _get_org_id()
    task = TaskItem.query.filter_by(id=task_id, organization_id=org_id).first_or_404()
    data = request.json or {}

    if "status" in data:
        task.status = data["status"]
        if task.status == "Completed":
            task.completed_at = datetime.utcnow()

    if "priority" in data:
        task.priority = data["priority"]

    if "assigned_to_name" in data:
        task.assigned_to_name = data["assigned_to_name"]

    if "description" in data:
        task.description = data["description"]

    if "title" in data:
        task.title = data["title"]

    db.session.commit()
    return jsonify({
        "msg": "Task updated successfully",
        "task": {
            "id": task.id,
            "title": task.title,
            "status": task.status,
            "priority": task.priority,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None
        }
    }), 200


@tasks_bp.route("/<int:task_id>/escalate", methods=["POST"])
@jwt_required()
def escalate_task(task_id):
    claims = get_jwt()
    if claims.get("role") not in ALLOWED_ROLES:
        return jsonify({"msg": "Unauthorized"}), 403

    org_id = _get_org_id()
    task = TaskItem.query.filter_by(id=task_id, organization_id=org_id).first_or_404()

    task.escalation_level += 1
    task.priority = "Urgent"

    # Log escalation in AuditLog
    audit = AuditLog(
        organization_id=org_id,
        action="TASK_ESCALATED",
        details=f"Task {task.id} ('{task.title}') escalated to Level {task.escalation_level}",
        user_role=claims.get("role") or "Staff",
        ip_address=request.remote_addr or "127.0.0.1"
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({
        "msg": f"Task escalated to Level {task.escalation_level}",
        "task_id": task.id,
        "escalation_level": task.escalation_level,
        "priority": task.priority
    }), 200


@tasks_bp.route("/summary", methods=["GET"])
@jwt_required()
def get_task_summary():
    claims = get_jwt()
    if claims.get("role") not in ALLOWED_ROLES:
        return jsonify({"msg": "Unauthorized"}), 403

    org_id = _get_org_id()
    tasks = TaskItem.query.filter_by(organization_id=org_id).all()
    now = datetime.utcnow()

    total = len(tasks)
    pending = sum(1 for t in tasks if t.status in ["Pending", "In_Progress"])
    urgent = sum(1 for t in tasks if t.priority == "Urgent" and t.status != "Completed")
    overdue = sum(1 for t in tasks if t.status not in ["Completed", "Cancelled"] and t.due_date and t.due_date < now)
    completed = sum(1 for t in tasks if t.status == "Completed")

    return jsonify({
        "total": total,
        "pending": pending,
        "urgent": urgent,
        "overdue": overdue,
        "completed": completed
    }), 200
