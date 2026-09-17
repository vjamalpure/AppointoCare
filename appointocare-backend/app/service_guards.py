from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from app.models import db, WhatsAppConfig, PaymentConfig, Organization, ServiceStatus, AuditLog


def _resolve_tenant_id():
    """
    Extracts tenant/organization ID from JWT claims, URL path parameters,
    or incoming JSON body.
    """
    tenant_id = None
    try:
        verify_jwt_in_request(optional=True)
        claims = get_jwt()
        if claims:
            tenant_id = claims.get("organization_id") or claims.get("tenant_id") or claims.get("sub")
            if tenant_id and str(tenant_id).isdigit():
                return int(tenant_id)
    except Exception:
        pass

    # Check route path parameters
    if request.view_args:
        for key in ["tenant_id", "org_id", "organization_id", "id"]:
            if key in request.view_args:
                try:
                    return int(request.view_args[key])
                except (ValueError, TypeError):
                    pass

    # Check JSON payload or query params
    if request.is_json and request.json:
        val = request.json.get("tenant_id") or request.json.get("organization_id")
        if val and str(val).isdigit():
            return int(val)

    if request.args:
        val = request.args.get("tenant_id") or request.args.get("organization_id")
        if val and str(val).isdigit():
            return int(val)

    return 1  # Default fallback if unauthenticated public webhook


def check_whatsapp_active(f):
    """
    Route Guard: Verifies that the tenant's WhatsApp Business API service flag is 'ACTIVE'.
    Instantly halts execution with HTTP 403 if the service is SUSPENDED or INACTIVE.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        tenant_id = _resolve_tenant_id()
        if not tenant_id:
            return jsonify({"error": "TENANT_REQUIRED", "message": "Tenant identification is required"}), 400

        config = WhatsAppConfig.query.filter_by(tenant_id=tenant_id).first()
        
        # If no config row exists yet, check root organization fallback or initialize default
        if not config:
            org = Organization.query.get(tenant_id)
            if org and getattr(org, "whatsapp_enabled", True):
                # Auto-initialize active config for seeded organizations
                config = WhatsAppConfig(
                    tenant_id=tenant_id,
                    waba_id=f"waba_{tenant_id}_{org.code.lower() if org else 'org'}",
                    phone_number_id=f"phone_{tenant_id}_9900",
                    service_status=ServiceStatus.ACTIVE,
                    meta_credit_line_status="SHARED_MASTER"
                )
                db.session.add(config)
                db.session.commit()
            else:
                return jsonify({
                    "error": "WHATSAPP_CONFIG_NOT_FOUND",
                    "message": f"WhatsApp Business service is not configured for tenant ID {tenant_id}.",
                    "tenant_id": tenant_id,
                    "service_status": ServiceStatus.INACTIVE
                }), 403

        if config.service_status != ServiceStatus.ACTIVE:
            return jsonify({
                "error": "WHATSAPP_SERVICE_SUSPENDED",
                "message": f"WhatsApp Business API execution blocked. Service is currently '{config.service_status}'.",
                "tenant_id": tenant_id,
                "service": "whatsapp",
                "service_status": config.service_status,
                "suspension_reason": config.suspension_reason or "Account suspended by platform Superadmin."
            }), 403

        return f(*args, **kwargs)
    return decorated_function


def check_razorpay_active(f):
    """
    Route Guard: Verifies that the tenant's Razorpay Payment Gateway service flag is 'ACTIVE'.
    Blocks order creation and returns HTTP 403 if SUSPENDED or INACTIVE.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        tenant_id = _resolve_tenant_id()
        if not tenant_id:
            return jsonify({"error": "TENANT_REQUIRED", "message": "Tenant identification is required"}), 400

        config = PaymentConfig.query.filter_by(tenant_id=tenant_id).first()
        
        # If no config row exists yet, check organization
        if not config:
            org = Organization.query.get(tenant_id)
            if org:
                # Auto-initialize active sub-account configuration
                config = PaymentConfig(
                    tenant_id=tenant_id,
                    razorpay_account_id=f"acc_rzp_{org.code.lower() if org else 'org'}",
                    merchant_name=org.name,
                    service_status=ServiceStatus.ACTIVE,
                    platform_commission_rate=0.05
                )
                db.session.add(config)
                db.session.commit()
            else:
                return jsonify({
                    "error": "PAYMENT_CONFIG_NOT_FOUND",
                    "message": f"Razorpay payment routing is not configured for tenant ID {tenant_id}.",
                    "tenant_id": tenant_id,
                    "service_status": ServiceStatus.INACTIVE
                }), 403

        if config.service_status != ServiceStatus.ACTIVE:
            return jsonify({
                "error": "PAYMENT_GATEWAY_SUSPENDED",
                "message": f"Razorpay payment processing blocked. Service is currently '{config.service_status}'.",
                "tenant_id": tenant_id,
                "service": "razorpay",
                "service_status": config.service_status,
                "suspension_reason": config.suspension_reason or "Payment gateway suspended by platform Superadmin."
            }), 403

        return f(*args, **kwargs)
    return decorated_function
