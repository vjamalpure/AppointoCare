from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from app.models import db, CustomerDocument, DocumentVersion, ApprovalRecord, AuditLog
from datetime import datetime, timedelta
import hashlib

documents_bp = Blueprint("documents_bp", __name__)

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


@documents_bp.route("/<int:doc_id>/versions", methods=["GET"])
@jwt_required()
def get_document_versions(doc_id):
    claims = get_jwt()
    if claims.get("role") not in ALLOWED_ROLES:
        return jsonify({"msg": "Unauthorized"}), 403

    org_id = _get_org_id()
    doc = CustomerDocument.query.filter_by(id=doc_id, organization_id=org_id).first_or_404()
    versions = DocumentVersion.query.filter_by(customer_document_id=doc.id).order_by(DocumentVersion.version_number.desc()).all()

    return jsonify([
        {
            "id": v.id,
            "version_number": v.version_number,
            "file_name": v.file_name,
            "file_size": v.file_size,
            "access_level": v.access_level,
            "expiry_date": v.expiry_date.isoformat() if v.expiry_date else None,
            "uploaded_by": v.uploaded_by,
            "download_count": v.download_count,
            "change_notes": v.change_notes,
            "created_at": v.created_at.isoformat() if v.created_at else None
        }
        for v in versions
    ]), 200


@documents_bp.route("/<int:doc_id>/versions", methods=["POST"])
@jwt_required()
def add_document_version(doc_id):
    claims = get_jwt()
    if claims.get("role") not in ALLOWED_ROLES:
        return jsonify({"msg": "Unauthorized"}), 403

    org_id = _get_org_id()
    doc = CustomerDocument.query.filter_by(id=doc_id, organization_id=org_id).first_or_404()
    data = request.json or {}

    file_name = data.get("file_name", doc.file_name)
    existing_count = DocumentVersion.query.filter_by(customer_document_id=doc.id).count()
    next_version = existing_count + 1

    expiry_date = None
    if data.get("expiry_date"):
        try:
            exp_str = data["expiry_date"].replace("Z", "+00:00")
            expiry_date = datetime.fromisoformat(exp_str)
        except Exception:
            expiry_date = datetime.utcnow() + timedelta(days=365)

    version = DocumentVersion(
        organization_id=org_id,
        customer_document_id=doc.id,
        version_number=next_version,
        file_name=file_name,
        file_size=int(data.get("file_size") or doc.file_size or 1024),
        storage_url_or_content=data.get("storage_url") or doc.storage_url_or_content,
        access_level=data.get("access_level", "Customer_Facing"),
        expiry_date=expiry_date,
        uploaded_by=claims.get("sub") or "Staff",
        change_notes=data.get("change_notes", f"Revision {next_version}")
    )
    db.session.add(version)

    # Update main doc status
    doc.file_name = file_name
    db.session.commit()

    return jsonify({
        "msg": f"Version {next_version} added successfully",
        "version": {
            "id": version.id,
            "version_number": version.version_number,
            "file_name": version.file_name,
            "access_level": version.access_level,
            "uploaded_by": version.uploaded_by
        }
    }), 201


@documents_bp.route("/<int:doc_id>/audit-download", methods=["POST"])
@jwt_required()
def audit_document_download(doc_id):
    claims = get_jwt()
    org_id = _get_org_id()
    doc = CustomerDocument.query.filter_by(id=doc_id, organization_id=org_id).first_or_404()

    latest_version = DocumentVersion.query.filter_by(customer_document_id=doc.id).order_by(DocumentVersion.version_number.desc()).first()
    if latest_version:
        latest_version.download_count += 1

    # Log in audit table
    audit = AuditLog(
        organization_id=org_id,
        action=f"DOCUMENT_DOWNLOAD: {doc.file_name} (ID: {doc.id})",
        details=f"Downloaded by {claims.get('sub') or 'User'}",
        user_role=claims.get("role") or "Staff",
        ip_address=request.remote_addr or "127.0.0.1"
    )
    db.session.add(audit)
    db.session.commit()

    return jsonify({
        "msg": "Download recorded",
        "doc_id": doc.id,
        "download_count": latest_version.download_count if latest_version else 1
    }), 200


@documents_bp.route("/approvals", methods=["POST"])
@jwt_required()
def create_approval():
    claims = get_jwt()
    org_id = _get_org_id()
    data = request.json or {}

    entity_type = data.get("entity_type", "treatment_plan")
    entity_id = int(data.get("entity_id") or 1)
    signee_name = data.get("signee_name") or claims.get("sub") or "Authorized Signee"

    # Generate verifiable signature hash
    raw_sig = f"{org_id}:{entity_type}:{entity_id}:{signee_name}:{datetime.utcnow().isoformat()}"
    sig_hash = hashlib.sha256(raw_sig.encode()).hexdigest()[:24].upper()

    approval = ApprovalRecord(
        organization_id=org_id,
        entity_type=entity_type,
        entity_id=entity_id,
        signee_name=signee_name,
        signee_email=data.get("signee_email"),
        signee_role=claims.get("role") or "Customer",
        status="Approved",
        signature_hash=f"SIG-{sig_hash}",
        ip_address=request.remote_addr or "127.0.0.1",
        notes=data.get("notes", "Electronic acknowledgement verified")
    )
    db.session.add(approval)
    db.session.commit()

    return jsonify({
        "msg": "Electronic acknowledgement recorded successfully",
        "approval": {
            "id": approval.id,
            "entity_type": approval.entity_type,
            "entity_id": approval.entity_id,
            "signee_name": approval.signee_name,
            "signature_hash": approval.signature_hash,
            "signed_at": approval.signed_at.isoformat()
        }
    }), 201


@documents_bp.route("/approvals", methods=["GET"])
@jwt_required()
def get_approvals():
    claims = get_jwt()
    if claims.get("role") not in ALLOWED_ROLES:
        return jsonify({"msg": "Unauthorized"}), 403

    org_id = _get_org_id()
    approvals = ApprovalRecord.query.filter_by(organization_id=org_id).order_by(ApprovalRecord.signed_at.desc()).all()

    return jsonify([
        {
            "id": a.id,
            "entity_type": a.entity_type,
            "entity_id": a.entity_id,
            "signee_name": a.signee_name,
            "signee_role": a.signee_role,
            "status": a.status,
            "signature_hash": a.signature_hash,
            "ip_address": a.ip_address,
            "notes": a.notes,
            "signed_at": a.signed_at.isoformat() if a.signed_at else None
        }
        for a in approvals
    ]), 200
