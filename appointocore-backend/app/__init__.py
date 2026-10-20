import os
from flask import Flask
from .models import db
from .config import Config
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS
from sqlalchemy import text


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Production Secret Hygiene Guard (SEC-02)
    app_env = os.getenv("APP_ENV", app.config.get("APP_ENV", "development"))
    secret = os.getenv("SECRET_KEY", app.config.get("SECRET_KEY", ""))
    jwt_secret = os.getenv("JWT_SECRET_KEY", app.config.get("JWT_SECRET_KEY", ""))

    if app_env == "production":
        insecure_keys = {"supersecretkey", "jwtsecretkey", "secret", "changeme", "dev", "appointocare-secret-jwt-key-2026", "appointocore-secret-jwt-key-2026"}
        if not secret or secret in insecure_keys or len(secret) < 32:
            raise RuntimeError("FATAL: Insecure or default SECRET_KEY in production environment. A strong key (>= 32 chars) is required.")
        if not jwt_secret or jwt_secret in insecure_keys or len(jwt_secret) < 32:
            raise RuntimeError("FATAL: Insecure or default JWT_SECRET_KEY in production environment. A strong key (>= 32 chars) is required.")

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)

    CORS(app, resources={r"/*": {"origins": app.config["CORS_ORIGINS"]}})

    @app.get("/health")
    def health():
        return {"status": "ok", "service": "appointocore-api", "app": "AppointoCore"}, 200

    @app.get("/ready")
    def ready():
        try:
            db.session.execute(text("SELECT 1"))
        except Exception:
            db.session.rollback()
            return {"status": "not_ready", "database": "unavailable"}, 503
        return {"status": "ready", "database": "available"}, 200

    # Import and register blueprints
    from .routes.auth import auth_bp
    from .routes.organization import organization_bp
    from .routes.appointments import appointment_bp
    from .routes.transactions import transaction_bp
    from .routes.admin import admin_bp
    from .routes.customers import customer_bp
    from .routes.services import service_bp
    from .routes.whatsapp import whatsapp_bp
    from .routes.platform import platform_bp
    from .routes.providers import provider_bp
    from .routes.payments import payments_bp
    from .routes.audit_logs import audit_bp
    from .routes.organization_v1 import org_v1_bp, ai_bp
    from .routes.industry_suite import industry_suite_bp
    from .routes.notifications import notifications_bp
    from .routes.workflows import workflows_bp, custom_fields_bp
    from .routes.customer_portal import customer_portal_bp
    from .routes.analytics import analytics_bp
    from .routes.automation import automation_bp
    from .routes.tasks import tasks_bp
    from .routes.pipelines import pipelines_bp
    from .routes.documents import documents_bp
    from .routes.healthcare import healthcare_bp

    # Auth & Admin & Core
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(admin_bp, url_prefix="/api/v1/admin", name="admin_api_v1")
    app.register_blueprint(organization_bp, url_prefix="/organization")
    app.register_blueprint(appointment_bp, url_prefix="/appointments")
    app.register_blueprint(appointment_bp, url_prefix="/api/v1/appointments", name="appointments_api_v1")
    app.register_blueprint(transaction_bp, url_prefix="/transactions")
    app.register_blueprint(transaction_bp, url_prefix="/api/v1/transactions", name="transaction_api_v1")

    # Multi-Industry Services Catalog (dual-prefix)
    app.register_blueprint(service_bp, url_prefix="/service")
    app.register_blueprint(service_bp, url_prefix="/api/v1/services", name="service_api_v1")

    # Customer CRM (dual-prefix)
    app.register_blueprint(customer_bp, url_prefix="/customer")
    app.register_blueprint(customer_bp, url_prefix="/api/v1/customers", name="customer_api_v1")

    # WhatsApp Meta Cloud API (dual-prefix)
    app.register_blueprint(whatsapp_bp, url_prefix="/whatsapp")
    app.register_blueprint(whatsapp_bp, url_prefix="/api/v1/whatsapp", name="whatsapp_api_v1")

    # Platform, Providers, Payments, Audit Logs, Staff & AI
    app.register_blueprint(platform_bp, url_prefix="/api/v1/platform")
    app.register_blueprint(provider_bp, url_prefix="/api/v1/providers")
    app.register_blueprint(payments_bp, url_prefix="/payments")
    app.register_blueprint(payments_bp, url_prefix="/api/v1/payments", name="payments_api_v1")
    app.register_blueprint(audit_bp, url_prefix="/api/v1/audit-logs")
    app.register_blueprint(org_v1_bp, url_prefix="/api/v1/organization")
    app.register_blueprint(ai_bp, url_prefix="/api/v1/ai")
    app.register_blueprint(industry_suite_bp, url_prefix="/api/v1/industry-suite")
    app.register_blueprint(notifications_bp, url_prefix="/api/v1/notifications")

    # Iteration 4: Workflows, Custom Fields, Client Portal, Analytics & Automation
    app.register_blueprint(workflows_bp, url_prefix="/api/v1/workflows")
    app.register_blueprint(custom_fields_bp, url_prefix="/api/v1/custom-fields")
    app.register_blueprint(customer_portal_bp, url_prefix="/api/v1/portal")
    app.register_blueprint(customer_portal_bp, url_prefix="/api/v1/customer-portal", name="customer_portal_api_v1")
    app.register_blueprint(analytics_bp, url_prefix="/api/v1/analytics")
    app.register_blueprint(automation_bp, url_prefix="/api/v1/automations")
    app.register_blueprint(automation_bp, url_prefix="/api/v1/automation", name="automation_singular_api_v1")

    # Iteration 5: Tasks, Pipelines, Documents & Healthcare Clinical Engine
    app.register_blueprint(tasks_bp, url_prefix="/api/v1/tasks")
    app.register_blueprint(pipelines_bp, url_prefix="/api/v1/pipelines")
    app.register_blueprint(documents_bp, url_prefix="/api/v1/documents")
    app.register_blueprint(healthcare_bp, url_prefix="/api/v1/healthcare")

    return app

