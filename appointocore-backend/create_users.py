# create_users.py
from app import create_app
from app.models import db, Admin, Organization
from app.utils.hash_helper import hash_password
from datetime import datetime, timedelta
import os

app = create_app()
app.app_context().push()

# ---------------------------
# Create Admin User
# ---------------------------
admin_username = os.getenv("ADMIN_USERNAME", "superadmin")
admin_password = os.getenv("ADMIN_PASSWORD")
org_username = os.getenv("ORG_USERNAME", "org1")
org_password = os.getenv("ORG_PASSWORD")

if not admin_password or not org_password:
    raise RuntimeError("ADMIN_PASSWORD and ORG_PASSWORD must be set")

existing_admin = Admin.query.filter_by(username=admin_username).first()
if not existing_admin:
    admin = Admin(
        username=admin_username,
        password=hash_password(admin_password),
        role="SuperAdmin",
        created_at=datetime.utcnow()
    )
    db.session.add(admin)
    print(f"Admin user '{admin_username}' created with password '{admin_password}'")
else:
    print(f"Admin user '{admin_username}' already exists")

# ---------------------------
# Create Organization User
# ---------------------------
existing_org = Organization.query.filter_by(username=org_username).first()
if not existing_org:
    org = Organization(
        name="Org 1",
        code="ORG1",
        sector="Hospital",
        username=org_username,
        password=hash_password(org_password),
        subscription_status="Active",
        subscription_plan="Basic",
        subscription_start=datetime.utcnow(),
        subscription_end=datetime.utcnow() + timedelta(days=30),
        next_billing_date=datetime.utcnow() + timedelta(days=30),
        created_at=datetime.utcnow()
    )
    db.session.add(org)
    print(f"Organization user '{org_username}' created with password '{org_password}'")
else:
    print(f"Organization user '{org_username}' already exists")

# Commit all changes
db.session.commit()
print("Users creation script completed successfully!")
