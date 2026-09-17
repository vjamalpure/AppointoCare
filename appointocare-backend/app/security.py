from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt, jwt_required


SUPER_ADMIN = "Admin"
ORGANIZATION_ADMIN = "Organization"
ORGANIZATION_MANAGER = "Manager"
ORGANIZATION_STAFF = "Staff"
CUSTOMER = "Customer"
SPECIALIST_ROLES = {
    "Doctor", "Therapist", "Stylist", "Advisor", "Analyst", "Underwriter",
    "Broker", "Consultant", "Specialist", "Counselor", "Partner",
    "Receptionist", "Agent", "Lawyer", "Nurse", "Accountant", "Assistant"
}
ORGANIZATION_ROLES = {
    ORGANIZATION_ADMIN,
    ORGANIZATION_MANAGER,
    ORGANIZATION_STAFF,
    *SPECIALIST_ROLES
}


def require_roles(*allowed_roles):
    def decorator(view):
        @wraps(view)
        @jwt_required()
        def wrapped(*args, **kwargs):
            claims = get_jwt()
            role = claims.get("role")
            
            # Allow SuperAdmin whenever Admin is permitted
            if role in ["SuperAdmin", "Admin"] and ("Admin" in allowed_roles or "SuperAdmin" in allowed_roles):
                return view(*args, **kwargs)

            # Direct match
            if role in allowed_roles:
                return view(*args, **kwargs)

            # If Staff or general organization role is allowed, allow any specialist role or org member
            if "Staff" in allowed_roles or any(r in ORGANIZATION_ROLES for r in allowed_roles):
                if role in SPECIALIST_ROLES or (claims.get("organization_id") and role != "Customer"):
                    return view(*args, **kwargs)

            return jsonify({"msg": "Unauthorized"}), 403

        return wrapped

    return decorator


def get_organization_id(claims=None):
    claims = claims or get_jwt()
    organization_id = claims.get("organization_id")
    if organization_id is None:
        return None
    try:
        return int(organization_id)
    except (TypeError, ValueError):
        return None
