from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from app.models import db, MessageLog, Organization

whatsapp_bp = Blueprint("whatsapp_bp", __name__)


@whatsapp_bp.route("/send", methods=["POST"])
@jwt_required()
def send_whatsapp_message():
    claims = get_jwt()
    role = claims.get("role")
    data = request.json or {}

    organization_id = data.get("organization_id")
    if role != "Admin":
        organization_id = int(claims.get("organization_id") or 0)
    elif not organization_id:
        return jsonify({"msg": "organization_id is required for admin requests"}), 400

    recipient_number = data.get("recipient_number") or data.get("phone")
    message_text = data.get("message") or data.get("message_content")
    if not recipient_number or not message_text:
        return jsonify({"msg": "recipient_number and message are required"}), 400

    message_log = MessageLog(
        organization_id=int(organization_id),
        recipient_number=recipient_number,
        message_type="WhatsApp",
        message_content=message_text,
        status="Queued",
        sent_at=None,
        remarks=None
    )
    db.session.add(message_log)
    db.session.commit()

    # TODO: wire this to a real WhatsApp provider, webhook, or Celery task.
    # Optionally enqueue an asynchronous task if Celery is available
    try:
        from app.tasks import send_whatsapp_message as send_whatsapp_task
        send_whatsapp_task.delay(message_log.organization_id, recipient_number, message_text)
    except Exception:
        pass

    return jsonify({
        "msg": "WhatsApp message queued",
        "message_id": message_log.id
    }), 202


@whatsapp_bp.route("/history", methods=["GET"])
@jwt_required()
def whatsapp_history():
    claims = get_jwt()
    role = claims.get("role")
    organization_id = request.args.get("organization_id")

    if role == "Admin":
        if organization_id:
            logs = MessageLog.query.filter_by(organization_id=int(organization_id)).all()
        else:
            logs = MessageLog.query.all()
    else:
        logs = MessageLog.query.filter_by(organization_id=int(claims.get("organization_id") or 0)).all()

    return jsonify([
        {
            "id": l.id,
            "organization_id": l.organization_id,
            "recipient_number": l.recipient_number,
            "message_type": l.message_type,
            "message_content": l.message_content,
            "status": l.status,
            "sent_at": l.sent_at.isoformat() if l.sent_at else None,
            "remarks": l.remarks,
            "created_at": l.created_at.isoformat(),
            "updated_at": l.updated_at.isoformat() if l.updated_at else None,
        }
        for l in logs
    ])
