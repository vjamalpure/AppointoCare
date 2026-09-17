from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from app.models import db, AuditLog

audit_bp = Blueprint("audit_bp", __name__)


@audit_bp.route("", methods=["GET"])
@jwt_required()
def get_audit_logs():
    claims = get_jwt()
    role = claims.get("role")
    org_id = request.args.get("organization_id")

    query = AuditLog.query

    if role != "Admin":
        tenant_org = int(claims.get("organization_id") or 0)
        query = query.filter_by(organization_id=tenant_org)
    elif org_id and org_id != "ALL":
        query = query.filter_by(organization_id=int(org_id))

    action = request.args.get("action")
    if action:
        query = query.filter(AuditLog.action.ilike(f"%{action}%"))

    logs = query.order_by(AuditLog.created_at.desc()).limit(150).all()

    return jsonify([
        {
            "id": l.id,
            "organization_id": l.organization_id,
            "user_id": l.user_id,
            "user_role": l.user_role,
            "action": l.action,
            "entity": l.entity,
            "entity_id": l.entity_id,
            "details": l.details,
            "ip_address": l.ip_address,
            "timestamp": l.created_at.isoformat() if l.created_at else None,
            "created_at": l.created_at.isoformat() if l.created_at else None
        }
        for l in logs
    ])
