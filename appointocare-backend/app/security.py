from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt, jwt_required


SUPER_ADMIN = "Admin"
ORGANIZATION_ADMIN = "Organization"
ORGANIZATION_MANAGER = "Manager"
ORGANIZATION_STAFF = "Staff"
CUSTOMER = "Customer"
ORGANIZATION_ROLES = {
    ORGANIZATION_ADMIN,
    ORGANIZATION_MANAGER,
    ORGANIZATION_STAFF,
}


def require_roles(*allowed_roles):
    def decorator(view):
        @wraps(view)
        @jwt_required()
        def wrapped(*args, **kwargs):
            if get_jwt().get("role") not in allowed_roles:
                return jsonify({"msg": "Unauthorized"}), 403
            return view(*args, **kwargs)

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
