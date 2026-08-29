# create_users.py
from app import create_app
from app.models import (
    db,
    Admin,
    Organization,
    User,
    Customer,
    Service,
    SubscriptionPlan,
    SectorTemplate,
)
from app.utils.hash_helper import hash_password
from datetime import datetime, timedelta
import os

app = create_app()
app.app_context().push()

# ---------------------------
# Create Admin User
# ---------------------------
admin_username = os.getenv("ADMIN_USERNAME", "superadmin")
admin_password = os.getenv("ADMIN_PASSWORD", "Admin@12345")
org_username = os.getenv("ORG_USERNAME", "org1")
org_password = os.getenv("ORG_PASSWORD", "Org@12345")
staff_username = os.getenv("STAFF_USERNAME", "staff1")
staff_password = os.getenv("STAFF_PASSWORD", "Staff@12345")

if os.getenv("APP_ENV") == "production" and os.getenv("SEED_DEMO_DATA", "false").lower() == "true":
    raise RuntimeError("Demo data seeding is disabled in production")

existing_admin = Admin.query.filter_by(username=admin_username).first()
if not existing_admin:
    admin = Admin(
        username=admin_username,
        password=hash_password(admin_password),
        role="SuperAdmin",
        created_at=datetime.utcnow()
    )
    db.session.add(admin)
    print(f"Admin user '{admin_username}' created")
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
    db.session.flush()
    print(f"Organization user '{org_username}' created")
else:
    print(f"Organization user '{org_username}' already exists")

org = Organization.query.filter_by(username=org_username).first()

staff = User.query.filter_by(organization_id=org.id, username=staff_username).first()
if not staff:
    db.session.add(User(
        organization_id=org.id,
        username=staff_username,
        password=hash_password(staff_password),
        role="Staff",
        is_active=True,
    ))
    print(f"Staff user '{staff_username}' created")
else:
    print(f"Staff user '{staff_username}' already exists")

customer = Customer.query.filter_by(organization_id=org.id, phone="9000000001").first()
if not customer:
    db.session.add(Customer(
        organization_id=org.id,
        name="Demo Customer",
        phone="9000000001",
        email="customer@example.com",
        source="demo",
    ))
    print("Demo customer created")

service = Service.query.filter_by(organization_id=org.id, name="General Consultation").first()
if not service:
    db.session.add(Service(
        organization_id=org.id,
        name="General Consultation",
        description="Sample service for local development",
        category="General",
        price=500.0,
        duration_minutes=30,
        active=True,
    ))
    print("Demo service created")

for plan_name, price, limits in [
    ("Starter", 999.0, {"users": 5, "appointments_per_month": 500}),
    ("Professional", 2499.0, {"users": 25, "appointments_per_month": 2500}),
    ("Enterprise", 9999.0, {"users": -1, "appointments_per_month": -1}),
]:
    if not SubscriptionPlan.query.filter_by(name=plan_name).first():
        db.session.add(SubscriptionPlan(
            name=plan_name,
            description=f"{plan_name} development plan",
            price=price,
            billing_cycle="monthly",
            feature_limits=limits,
            is_active=True,
        ))

for template_name, services in {
    "Hospital": ["Doctor Consultation", "Diagnostic Review"],
    "Finance": ["Loan Consultation", "Financial Planning"],
    "Retail": ["Store Visit", "Product Consultation"],
    "Education": ["Counselling Session", "Course Consultation"],
    "Insurance": ["Policy Consultation", "Claims Assistance"],
    "Salon": ["Hair Styling", "Wellness Consultation"],
    "Consultancy": ["Discovery Call", "Advisory Session"],
}.items():
    if not SectorTemplate.query.filter_by(name=template_name).first():
        db.session.add(SectorTemplate(
            name=template_name,
            description=f"Configurable {template_name.lower()} services",
            services=services,
            is_active=True,
        ))

db.session.commit()
print("Demo data initialization completed successfully")
