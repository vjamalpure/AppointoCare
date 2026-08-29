from flask import Flask
from .models import db
from .config import Config
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_cors import CORS  # <- Import CORS
from sqlalchemy import text


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)

    CORS(app, resources={r"/*": {"origins": app.config["CORS_ORIGINS"]}})

    @app.get("/health")
    def health():
        return {"status": "ok", "service": "appointocore-api"}, 200

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

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(organization_bp, url_prefix="/organization")
    app.register_blueprint(appointment_bp, url_prefix="/appointments")
    app.register_blueprint(transaction_bp, url_prefix="/transactions")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(customer_bp, url_prefix="/customer")
    app.register_blueprint(service_bp, url_prefix="/service")
    app.register_blueprint(whatsapp_bp, url_prefix="/whatsapp")
    app.register_blueprint(platform_bp, url_prefix="/api/v1/platform")
    app.register_blueprint(provider_bp, url_prefix="/api/v1/providers")

    return app
