from flask import Blueprint, request, jsonify
from app.models import Admin, Organization, User, db
from app.utils.hash_helper import verify_password, hash_password
from app.utils.jwt_helper import generate_access_token, generate_refresh_token
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt, decode_token
from datetime import timedelta

auth_bp = Blueprint("auth_bp", __name__)


def _build_claims(user, role, organization=None):
    claims = {"username": user.username, "role": role}
    if organization:
        claims.update({
            "organization_name": organization.name,
            "organization_id": str(organization.id)
        })
    elif role == "Organization":
        claims.update({
            "organization_name": user.name,
            "organization_id": str(user.id)
        })
    return claims


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")
    code = data.get("code")

    if not username or not password:
        return jsonify({"msg": "Username and password are required"}), 400

    # --- Admin login ---
    admin = Admin.query.filter_by(username=username).first()
    if admin:
        if verify_password(password, admin.password):
            claims = _build_claims(admin, "Admin")
            access_token = generate_access_token(admin.id, "Admin", extra_claims=claims)
            refresh_token = generate_refresh_token(admin.id, "Admin", extra_claims=claims)
            return jsonify({
                "access_token": access_token,
                "refresh_token": refresh_token,
                "role": "Admin",
                "username": admin.username
            }), 200
        return jsonify({"msg": "Invalid password"}), 401

    # --- Organization or staff login ---
    if not code:
        return jsonify({"msg": "Organization code is required"}), 400

    org = Organization.query.filter_by(code=code).first()
    if not org:
        return jsonify({"msg": "Invalid organization code"}), 401

    # Organization admin login
    if org.username == username:
        if verify_password(password, org.password):
            claims = _build_claims(org, "Organization", organization=org)
            access_token = generate_access_token(org.id, "Organization", extra_claims=claims)
            refresh_token = generate_refresh_token(org.id, "Organization", extra_claims=claims)
            return jsonify({
                "access_token": access_token,
                "refresh_token": refresh_token,
                "role": "Organization",
                "organization_id": str(org.id),
                "organization_name": org.name
            }), 200
        return jsonify({"msg": "Invalid password"}), 401

    # Organization staff login
    staff = User.query.filter_by(organization_id=org.id, username=username).first()
    if staff and verify_password(password, staff.password) and staff.is_active:
        claims = _build_claims(staff, staff.role, organization=org)
        access_token = generate_access_token(staff.id, staff.role, extra_claims=claims)
        refresh_token = generate_refresh_token(staff.id, staff.role, extra_claims=claims)
        return jsonify({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "role": staff.role,
            "organization_id": str(org.id),
            "organization_name": org.name,
            "username": staff.username
        }), 200

    return jsonify({"msg": "Invalid credentials"}), 401


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh_token():
    claims = get_jwt()
    identity = get_jwt_identity()
    role = claims.get("role")
    extra_claims = {
        "username": claims.get("username"),
        "organization_name": claims.get("organization_name"),
        "organization_id": claims.get("organization_id")
    }
    access_token = generate_access_token(identity, role, extra_claims=extra_claims)
    return jsonify({"access_token": access_token}), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    return jsonify({"msg": "Logged out"}), 200


@auth_bp.route("/change-password", methods=["POST"])
@jwt_required()
def change_password():
    claims = get_jwt()
    identity = get_jwt_identity()
    role = claims.get("role")

    data = request.json or {}
    old_password = data.get("old_password")
    new_password = data.get("new_password")

    if not old_password or not new_password:
        return jsonify({"msg": "old_password and new_password are required"}), 400

    if role == "Admin":
        user = Admin.query.get(identity)
    elif role == "Organization":
        user = Organization.query.get(identity)
    elif role in ["Manager", "Staff"]:
        user = User.query.get(identity)
    else:
        return jsonify({"msg": "Unauthorized"}), 403

    if not user or not verify_password(old_password, user.password):
        return jsonify({"msg": "Invalid credentials"}), 401

    user.password = hash_password(new_password)
    db.session.commit()
    return jsonify({"msg": "Password changed successfully"}), 200


@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.json or {}
    username = data.get("username")
    role = data.get("role")
    code = data.get("code")

    if not username or not role:
        return jsonify({"msg": "username and role are required"}), 400

    if role == "Admin":
        user = Admin.query.filter_by(username=username).first()
    elif role == "Organization":
        user = Organization.query.filter_by(username=username).first()
        if user and code and user.code != code:
            return jsonify({"msg": "Invalid organization code"}), 401
    elif role in ["Manager", "Staff"]:
        if not code:
            return jsonify({"msg": "Organization code is required"}), 400
        org = Organization.query.filter_by(code=code).first()
        if not org:
            return jsonify({"msg": "Invalid organization code"}), 401
        user = User.query.filter_by(username=username, organization_id=org.id).first()
    else:
        return jsonify({"msg": "Invalid role"}), 400

    if not user:
        return jsonify({"msg": "If the account exists, a reset token has been issued."}), 200

    extra_claims = _build_claims(user, role)
    reset_token = generate_access_token(
        user.id,
        role,
        extra_claims=extra_claims,
        expires_delta=timedelta(minutes=30)
    )

    return jsonify({
        "msg": "Password reset token generated.",
        "reset_token": reset_token
    }), 200


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.json or {}
    token = data.get("token")
    new_password = data.get("new_password")

    if not token or not new_password:
        return jsonify({"msg": "token and new_password are required"}), 400

    try:
        decoded = decode_token(token)
    except Exception:
        return jsonify({"msg": "Invalid or expired password reset token"}), 400

    role = decoded.get("role")
    identity = decoded.get("sub")

    if role == "Admin":
        user = Admin.query.get(identity)
    elif role == "Organization":
        user = Organization.query.get(identity)
    elif role in ["Manager", "Staff"]:
        user = User.query.get(identity)
    else:
        return jsonify({"msg": "Invalid token role"}), 400

    if not user:
        return jsonify({"msg": "User not found"}), 404

    user.password = hash_password(new_password)
    db.session.commit()

    return jsonify({"msg": "Password updated successfully"}), 200
