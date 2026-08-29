# sample_data.py
from app import create_app
from app.models import db, Organization, Appointment, AppointmentTransaction, OrganizationTransaction, Admin
from app.utils.hash_helper import hash_password
from datetime import datetime, timedelta
import random
import os

admin_password = os.getenv("ADMIN_PASSWORD")
org_password = os.getenv("ORG_PASSWORD")

if not admin_password or not org_password:
    raise RuntimeError("ADMIN_PASSWORD and ORG_PASSWORD must be set")

app = create_app()
app.app_context().push()

# Clear existing data
db.drop_all()
db.create_all()

# ----------------------------
# Create Admin
# ----------------------------
admin = Admin(
    username="superadmin",
    password=hash_password(admin_password),
    role="SuperAdmin"
)
db.session.add(admin)
db.session.commit()

# ----------------------------
# Create Organizations
# ----------------------------
sectors = ["Hospital", "Finance", "Retail"]
plans = ["Basic", "Premium", "Enterprise"]

organizations = []
for i in range(1, 6):
    org = Organization(
        name=f"Org {i}",
        code=f"ORG{i}",
        sector=random.choice(sectors),
        username=f"org{i}",
        password=hash_password(org_password),
        subscription_status=random.choice(["Active", "Paused", "Stopped"]),
        subscription_plan=random.choice(plans),
        subscription_start=datetime.utcnow() - timedelta(days=30),
        subscription_end=datetime.utcnow() + timedelta(days=30),
        next_billing_date=datetime.utcnow() + timedelta(days=30)
    )
    db.session.add(org)
    organizations.append(org)

db.session.commit()

# ----------------------------
# Create Appointments & Transactions
# ----------------------------
payment_methods = ["UPI", "Cash", "Card"]

for org in organizations:
    for j in range(1, 6):
        appt_date = datetime.utcnow() + timedelta(days=random.randint(1, 15))
        appointment = Appointment(
            customer_name=f"Customer {j} of {org.name}",
            customer_phone=f"90000000{j}",
            appointment_date=appt_date,
            status=random.choice(["Booked", "Completed", "Cancelled"]),
            payment_status=random.choice(["Paid", "Unpaid"]),
            organization_id=org.id
        )
        db.session.add(appointment)
        db.session.flush()  # get appointment.id

        # Appointment transaction
        transaction = AppointmentTransaction(
            appointment_id=appointment.id,
            organization_id=org.id,
            amount=random.randint(100, 1000),
            transaction_type=random.choice(["Payment", "Refund"]),
            payment_method=random.choice(payment_methods),
            processed_by_type="Organization",
            processed_by_id=org.id,
            status="Success"
        )
        db.session.add(transaction)

# ----------------------------
# Create Organization Transactions (Subscription payments)
# ----------------------------
for org in organizations:
    org_txn = OrganizationTransaction(
        organization_id=org.id,
        amount=random.randint(500, 2000),
        transaction_type="Subscription",
        payment_method=random.choice(payment_methods),
        invoice_id=f"INV-{org.code}-{random.randint(1000,9999)}",
        period_start=org.subscription_start,
        period_end=org.subscription_end,
        status="Success",
        processed_by_type="Admin",
        processed_by_id=admin.id
    )
    db.session.add(org_txn)

# Commit all
db.session.commit()

print("Sample data created successfully!")
