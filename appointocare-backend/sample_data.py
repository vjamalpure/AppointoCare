"""
Comprehensive Sample Data Migration Script for AppointoCare Backend
Seeds users of each level (SuperAdmin, Org Admins, Staff/Specialists/Managers),
all 9 industry sectors, branches, services, customers/patients, appointments,
transactions, subscriptions, plans, templates, and message logs.

Can be run standalone:
    python sample_data.py [--reset]
or invoked programmatically via:
    from sample_data import seed_all_sample_data
    seed_all_sample_data()
"""

import os
import sys
from datetime import datetime, timedelta
from app import create_app
from app.models import (
    db,
    Admin,
    Organization,
    User,
    Branch,
    Customer,
    Patient,
    Service,
    Appointment,
    AppointmentTransaction,
    OrganizationTransaction,
    SubscriptionPlan,
    Subscription,
    SectorTemplate,
    MessageLog,
    AuditLog,
    Notification
)
from app.utils.hash_helper import hash_password

DEFAULT_ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin@12345")
DEFAULT_ORG_PASSWORD = os.getenv("ORG_PASSWORD", "Org@12345")
DEFAULT_STAFF_PASSWORD = os.getenv("STAFF_PASSWORD", "Staff@12345")

# All 9 multi-industry organizations
SAMPLE_ORGANIZATIONS = [
    {
        "name": "City Care Health & Dental",
        "code": "ORG1",
        "sector": "Healthcare",
        "username": "org1",
        "plan": "Enterprise",
        "status": "Active",
        "branches": [
            {"name": "Downtown Central Hospital", "address": "100 Medical Center Blvd, Metro City", "phone": "+1 555-0101", "tz": "America/New_York"},
            {"name": "Westside Dental Specialty Center", "address": "450 Westside Ave, Suite 300", "phone": "+1 555-0102", "tz": "America/New_York"},
        ],
        "staff": [
            {"username": "staff1", "role": "Staff"},
            {"username": "doc_sarah", "role": "Doctor"},
            {"username": "dr_chen", "role": "Doctor"},
        ],
        "services": [
            {"name": "General Physician Consultation", "category": "Medical", "price": 120.0, "duration": 30},
            {"name": "Comprehensive Dental Cleaning & Exam", "category": "Dental", "price": 180.0, "duration": 45},
            {"name": "Orthopedic Assessment & Digital X-Ray", "category": "Diagnostics", "price": 260.0, "duration": 60},
            {"name": "Pediatric Routine Wellness Exam", "category": "Pediatrics", "price": 140.0, "duration": 30},
        ],
        "customers": [
            {"name": "Michael Harrison", "phone": "+1 555-1101", "email": "michael.h@example.com", "gender": "Male"},
            {"name": "Sarah Connor", "phone": "+1 555-1102", "email": "s.connor@example.com", "gender": "Female"},
            {"name": "David Miller", "phone": "+1 555-1103", "email": "dmiller@example.com", "gender": "Male"},
        ],
        "appointments": [
            {"customer": "Michael Harrison", "phone": "+1 555-1101", "service": "General Physician Consultation", "days_offset": 0, "status": "Booked", "payment": "Paid", "amount": 120.0},
            {"customer": "Sarah Connor", "phone": "+1 555-1102", "service": "Comprehensive Dental Cleaning & Exam", "days_offset": 1, "status": "Booked", "payment": "Unpaid", "amount": 180.0},
            {"customer": "David Miller", "phone": "+1 555-1103", "service": "Orthopedic Assessment & Digital X-Ray", "days_offset": -1, "status": "Completed", "payment": "Paid", "amount": 260.0},
        ]
    },
    {
        "name": "Apex Aesthetics & Wellness Spa",
        "code": "ORG2",
        "sector": "Salon & Wellness",
        "username": "org2",
        "plan": "Professional",
        "status": "Active",
        "branches": [
            {"name": "Midtown Luxe Spa & Lounge", "address": "780 Fifth Avenue, Floor 4", "phone": "+1 555-0201", "tz": "America/New_York"}
        ],
        "staff": [
            {"username": "olivia_spa", "role": "Therapist"},
            {"username": "chloe_hair", "role": "Stylist"}
        ],
        "services": [
            {"name": "Hydra-Facial & Dermaplaning Session", "category": "Aesthetics", "price": 220.0, "duration": 60},
            {"name": "Balayage Color & Master Precision Cut", "category": "Hair", "price": 310.0, "duration": 90},
            {"name": "Hot Stone Aromatherapy Deep Massage", "category": "Body", "price": 160.0, "duration": 75}
        ],
        "customers": [
            {"name": "Jessica Alba", "phone": "+1 555-2101", "email": "jessica.a@example.com", "gender": "Female"},
            {"name": "Victoria Beckham", "phone": "+1 555-2102", "email": "v.beckham@example.com", "gender": "Female"}
        ],
        "appointments": [
            {"customer": "Jessica Alba", "phone": "+1 555-2101", "service": "Hydra-Facial & Dermaplaning Session", "days_offset": 0, "status": "Booked", "payment": "Paid", "amount": 220.0},
            {"customer": "Victoria Beckham", "phone": "+1 555-2102", "service": "Balayage Color & Master Precision Cut", "days_offset": 2, "status": "Booked", "payment": "Unpaid", "amount": 310.0}
        ]
    },
    {
        "name": "Vanguard Wealth & Asset Advisory",
        "code": "ORG3",
        "sector": "Finance",
        "username": "org3",
        "plan": "Enterprise",
        "status": "Active",
        "branches": [
            {"name": "Wall Street Private Client Group", "address": "14 Wall Street, 22nd Floor", "phone": "+1 555-0301", "tz": "America/New_York"}
        ],
        "staff": [
            {"username": "alex_wealth", "role": "Advisor"},
            {"username": "sarah_tax", "role": "Analyst"}
        ],
        "services": [
            {"name": "High-Net-Worth Portfolio Restructuring", "category": "Advisory", "price": 500.0, "duration": 60},
            {"name": "Cross-Border Tax & Trust Structuring", "category": "Tax", "price": 650.0, "duration": 90},
            {"name": "Retirement & Estate Liquidity Planning", "category": "Estate", "price": 350.0, "duration": 45}
        ],
        "customers": [
            {"name": "Marcus Vance", "phone": "+1 555-3101", "email": "marcus.v@example.com", "gender": "Male"}
        ],
        "appointments": [
            {"customer": "Marcus Vance", "phone": "+1 555-3101", "service": "High-Net-Worth Portfolio Restructuring", "days_offset": 0, "status": "Booked", "payment": "Paid", "amount": 500.0}
        ]
    },
    {
        "name": "Sovereign Life & Risk Insurance",
        "code": "ORG4",
        "sector": "Insurance",
        "username": "org4",
        "plan": "Professional",
        "status": "Active",
        "branches": [
            {"name": "Financial District Branch", "address": "200 Liberty Street, Suite 12", "phone": "+1 555-0401", "tz": "America/New_York"}
        ],
        "staff": [
            {"username": "victoria_insur", "role": "Underwriter"}
        ],
        "services": [
            {"name": "Whole-Life & Term Policy Underwriting", "category": "Life", "price": 0.0, "duration": 45},
            {"name": "Commercial Liability & Cyber Shield Review", "category": "Corporate", "price": 250.0, "duration": 60}
        ],
        "customers": [
            {"name": "Ethan Hunt", "phone": "+1 555-4101", "email": "ethan.h@example.com", "gender": "Male"}
        ],
        "appointments": [
            {"customer": "Ethan Hunt", "phone": "+1 555-4101", "service": "Commercial Liability & Cyber Shield Review", "days_offset": 1, "status": "Booked", "payment": "Paid", "amount": 250.0}
        ]
    },
    {
        "name": "Aura Haute Couture & Styling Lounge",
        "code": "ORG5",
        "sector": "Retail",
        "username": "org5",
        "plan": "Professional",
        "status": "Active",
        "branches": [
            {"name": "Madison Avenue Showroom", "address": "650 Madison Avenue", "phone": "+1 555-0501", "tz": "America/New_York"}
        ],
        "staff": [
            {"username": "jeanluc_style", "role": "Stylist"}
        ],
        "services": [
            {"name": "VIP Runway Wardrobe Consultation", "category": "Styling", "price": 300.0, "duration": 90},
            {"name": "Bespoke Suiting & Tailoring Fitting", "category": "Tailoring", "price": 150.0, "duration": 45}
        ],
        "customers": [
            {"name": "Claire Dupont", "phone": "+1 555-5101", "email": "c.dupont@example.com", "gender": "Female"}
        ],
        "appointments": [
            {"customer": "Claire Dupont", "phone": "+1 555-5101", "service": "VIP Runway Wardrobe Consultation", "days_offset": 0, "status": "Booked", "payment": "Paid", "amount": 300.0}
        ]
    },
    {
        "name": "Beacon Global University Counseling",
        "code": "ORG6",
        "sector": "Education",
        "username": "org6",
        "plan": "Professional",
        "status": "Active",
        "branches": [
            {"name": "Academic Heights Center", "address": "120 College Walk, Suite 500", "phone": "+1 555-0601", "tz": "America/New_York"}
        ],
        "staff": [
            {"username": "elena_counsel", "role": "Counselor"}
        ],
        "services": [
            {"name": "Ivy League Admissions Strategy Call", "category": "Admissions", "price": 400.0, "duration": 60},
            {"name": "SOP & Research Statement Review", "category": "Editorial", "price": 250.0, "duration": 45}
        ],
        "customers": [
            {"name": "Alexander Young", "phone": "+1 555-6101", "email": "ayoung@example.com", "gender": "Male"}
        ],
        "appointments": [
            {"customer": "Alexander Young", "phone": "+1 555-6101", "service": "Ivy League Admissions Strategy Call", "days_offset": 1, "status": "Booked", "payment": "Paid", "amount": 400.0}
        ]
    },
    {
        "name": "Sterling & Blackwood Legal Partners",
        "code": "ORG7",
        "sector": "Consultancy",
        "username": "org7",
        "plan": "Enterprise",
        "status": "Active",
        "branches": [
            {"name": "Park Avenue Chambers", "address": "345 Park Avenue, 30th Floor", "phone": "+1 555-0701", "tz": "America/New_York"}
        ],
        "staff": [
            {"username": "eleanor_legal", "role": "Partner"}
        ],
        "services": [
            {"name": "M&A Due Diligence & Corporate Counsel", "category": "Corporate", "price": 850.0, "duration": 60},
            {"name": "Intellectual Property & Patent Defense", "category": "IP", "price": 700.0, "duration": 60}
        ],
        "customers": [
            {"name": "Jonathan Vance", "phone": "+1 555-7101", "email": "jvance@example.com", "gender": "Male"}
        ],
        "appointments": [
            {"customer": "Jonathan Vance", "phone": "+1 555-7101", "service": "M&A Due Diligence & Corporate Counsel", "days_offset": 0, "status": "Booked", "payment": "Paid", "amount": 850.0}
        ]
    },
    {
        "name": "Sovereign Realty & Architectural Partners",
        "code": "ORG8",
        "sector": "Real Estate",
        "username": "org8",
        "plan": "Professional",
        "status": "Active",
        "branches": [
            {"name": "TriBeCa Penthouse Gallery", "address": "88 Franklin Street", "phone": "+1 555-0801", "tz": "America/New_York"}
        ],
        "staff": [
            {"username": "marcus_realty", "role": "Broker"}
        ],
        "services": [
            {"name": "Luxury Penthouse Private Showing", "category": "Listing", "price": 0.0, "duration": 60},
            {"name": "Architectural Design Feasibility Review", "category": "Architecture", "price": 450.0, "duration": 60}
        ],
        "customers": [
            {"name": "Lady Catherine", "phone": "+1 555-8101", "email": "catherine@example.com", "gender": "Female"}
        ],
        "appointments": [
            {"customer": "Lady Catherine", "phone": "+1 555-8101", "service": "Luxury Penthouse Private Showing", "days_offset": 2, "status": "Booked", "payment": "Paid", "amount": 0.0}
        ]
    },
    {
        "name": "Vanguard Global Enterprise Solutions",
        "code": "ORG9",
        "sector": "Professional Services",
        "username": "org9",
        "plan": "Enterprise",
        "status": "Active",
        "branches": [
            {"name": "One World Trade Center HQ", "address": "285 Fulton St, Suite 75", "phone": "+1 555-0901", "tz": "America/New_York"}
        ],
        "staff": [
            {"username": "elizabeth_exec", "role": "Consultant"}
        ],
        "services": [
            {"name": "Enterprise Cloud Architecture Audit", "category": "IT", "price": 1200.0, "duration": 90},
            {"name": "AI Transformation & Workflow Blueprint", "category": "AI", "price": 1500.0, "duration": 120}
        ],
        "customers": [
            {"name": "William Sterling", "phone": "+1 555-9101", "email": "wsterling@example.com", "gender": "Male"}
        ],
        "appointments": [
            {"customer": "William Sterling", "phone": "+1 555-9101", "service": "Enterprise Cloud Architecture Audit", "days_offset": 1, "status": "Booked", "payment": "Paid", "amount": 1200.0}
        ]
    }
]

SUBSCRIPTION_PLANS = [
    {
        "name": "Starter",
        "description": "Essential appointment scheduling for single-location clinics and studios.",
        "price": 49.0,
        "billing_cycle": "monthly",
        "feature_limits": {"branches": 1, "staff": 3, "appointments_per_month": 300, "whatsapp_integration": True}
    },
    {
        "name": "Professional",
        "description": "Robust suite with multi-branch management, advanced analytics, and custom WhatsApp automation.",
        "price": 149.0,
        "billing_cycle": "monthly",
        "feature_limits": {"branches": 5, "staff": 15, "appointments_per_month": 2500, "whatsapp_integration": True, "api_access": True}
    },
    {
        "name": "Enterprise",
        "description": "Unlimited capacity, dedicated HIPAA-compliant hosting, audit logs, and priority SLA.",
        "price": 499.0,
        "billing_cycle": "monthly",
        "feature_limits": {"branches": -1, "staff": -1, "appointments_per_month": -1, "whatsapp_integration": True, "api_access": True, "custom_domain": True}
    }
]

SECTOR_TEMPLATES = {
    "Hospital & Medical Clinic": ["Doctor Consultation", "Diagnostic Review", "Emergency Triage", "Prescription Refill"],
    "Premium Salon & Aesthetics Spa": ["Hair Styling & Cut", "Hydra-Facial", "Deep Tissue Massage", "Manicure & Pedicure"],
    "Wealth & Financial Advisory": ["Portfolio Audit", "Tax Advisory", "Wealth Management", "Retirement Planning"],
    "Life & General Insurance Agency": ["Policy Consultation", "Underwriting Review", "Claims Assistance", "Corporate Risk Audit"],
    "Luxury Retail & Personal Styling": ["VIP Fitting Session", "Runway Styling", "Bespoke Tailoring", "Personal Shopper"],
    "Academy & University Counseling": ["Admissions Strategy", "SOP Review", "Scholarship Counseling", "Mock Interview"],
    "Strategic Management & Legal Advisory": ["Corporate Counsel", "M&A Due Diligence", "IP Strategy", "Contract Review"],
    "Real Estate & Architecture Advisory": ["Penthouse Showing", "Commercial Site Tour", "Architectural Review", "Valuation Consultation"],
    "Custom Enterprise & Professional Services": ["Cloud Architecture Audit", "Security Assessment", "Digital Transformation", "Executive Briefing"]
}


def seed_all_sample_data(reset=False):
    """
    Idempotent seeding function.
    If reset=True, it clears application data tables safely without dropping alembic_version.
    """
    print("=" * 60)
    print("Starting AppointoCare Comprehensive Sample Data Migration")
    print("=" * 60)

    if reset:
        print("Reset flag detected: Clearing previous domain records...")
        db.session.query(MessageLog).delete()
        db.session.query(AuditLog).delete()
        db.session.query(Notification).delete()
        db.session.query(AppointmentTransaction).delete()
        db.session.query(Appointment).delete()
        db.session.query(Patient).delete()
        db.session.query(Customer).delete()
        db.session.query(Service).delete()
        db.session.query(Branch).delete()
        db.session.query(User).delete()
        db.session.query(Subscription).delete()
        db.session.query(OrganizationTransaction).delete()
        db.session.query(Organization).delete()
        db.session.query(Admin).delete()
        db.session.query(SubscriptionPlan).delete()
        db.session.query(SectorTemplate).delete()
        db.session.commit()
        print("✓ Previous domain records cleared.")

    # 1. SuperAdmin User
    admin_user = os.getenv("ADMIN_USERNAME", "superadmin")
    admin = Admin.query.filter_by(username=admin_user).first()
    if not admin:
        admin = Admin(
            username=admin_user,
            password=hash_password(DEFAULT_ADMIN_PASSWORD),
            role="SuperAdmin",
            created_at=datetime.utcnow()
        )
        db.session.add(admin)
        db.session.commit()
        print(f"✓ SuperAdmin created: {admin_user}")
    else:
        admin.password = hash_password(DEFAULT_ADMIN_PASSWORD)
        db.session.commit()
        print(f"✓ SuperAdmin updated: {admin_user}")

    # 2. Subscription Plans
    for plan_data in SUBSCRIPTION_PLANS:
        plan = SubscriptionPlan.query.filter_by(name=plan_data["name"]).first()
        if not plan:
            plan = SubscriptionPlan(
                name=plan_data["name"],
                description=plan_data["description"],
                price=plan_data["price"],
                billing_cycle=plan_data["billing_cycle"],
                feature_limits=plan_data["feature_limits"],
                is_active=True
            )
            db.session.add(plan)
        else:
            plan.price = plan_data["price"]
            plan.feature_limits = plan_data["feature_limits"]
            plan.description = plan_data["description"]
    db.session.commit()
    print("✓ Subscription Plans synchronized.")

    # 3. Sector Templates
    for template_name, services in SECTOR_TEMPLATES.items():
        template = SectorTemplate.query.filter_by(name=template_name).first()
        if not template:
            template = SectorTemplate(
                name=template_name,
                description=f"Standard preconfigured workflows for {template_name}",
                services=services,
                is_active=True
            )
            db.session.add(template)
        else:
            template.services = services
    db.session.commit()
    print("✓ Sector Templates synchronized.")

    # 4. Organizations, Branches, Staff, Services, Customers, Appointments
    now = datetime.utcnow()
    for org_data in SAMPLE_ORGANIZATIONS:
        org = Organization.query.filter_by(code=org_data["code"]).first()
        if not org:
            org = Organization(
                name=org_data["name"],
                code=org_data["code"],
                sector=org_data["sector"],
                username=org_data["username"],
                password=hash_password(DEFAULT_ORG_PASSWORD),
                subscription_status=org_data["status"],
                subscription_plan=org_data["plan"],
                subscription_start=now - timedelta(days=60),
                subscription_end=now + timedelta(days=300),
                next_billing_date=now + timedelta(days=30)
            )
            db.session.add(org)
            db.session.flush()
            print(f"  + Created Organization: {org.name} ({org.code})")
        else:
            org.name = org_data["name"]
            org.sector = org_data["sector"]
            org.password = hash_password(DEFAULT_ORG_PASSWORD)
            org.subscription_plan = org_data["plan"]
            org.subscription_status = org_data["status"]
            db.session.flush()

        # Organization Transaction (Subscription Invoice)
        existing_tx = OrganizationTransaction.query.filter_by(organization_id=org.id).first()
        if not existing_tx:
            db.session.add(OrganizationTransaction(
                organization_id=org.id,
                amount=149.0 if org_data["plan"] == "Professional" else (499.0 if org_data["plan"] == "Enterprise" else 49.0),
                transaction_type="Subscription",
                payment_method="Card",
                invoice_id=f"INV-{org.code}-{now.strftime('%Y%m')}",
                status="Success",
                processed_by_type="Admin",
                processed_by_id=admin.id,
                remarks=f"Automated annual plan renewal for {org.name}"
            ))

        # Branches
        for branch_info in org_data["branches"]:
            branch = Branch.query.filter_by(organization_id=org.id, name=branch_info["name"]).first()
            if not branch:
                db.session.add(Branch(
                    organization_id=org.id,
                    name=branch_info["name"],
                    address=branch_info["address"],
                    phone=branch_info["phone"],
                    timezone=branch_info.get("tz", "America/New_York"),
                    is_active=True
                ))

        # Staff Users
        for staff_info in org_data["staff"]:
            staff = User.query.filter_by(organization_id=org.id, username=staff_info["username"]).first()
            if not staff:
                db.session.add(User(
                    organization_id=org.id,
                    username=staff_info["username"],
                    password=hash_password(DEFAULT_STAFF_PASSWORD),
                    role=staff_info["role"],
                    is_active=True
                ))
            else:
                staff.password = hash_password(DEFAULT_STAFF_PASSWORD)
                staff.role = staff_info["role"]
                staff.is_active = True

        # Services
        for svc_info in org_data["services"]:
            service = Service.query.filter_by(organization_id=org.id, name=svc_info["name"]).first()
            if not service:
                db.session.add(Service(
                    organization_id=org.id,
                    name=svc_info["name"],
                    category=svc_info["category"],
                    price=svc_info["price"],
                    duration_minutes=svc_info["duration"],
                    description=f"{svc_info['name']} provided by specialized experts at {org.name}.",
                    active=True
                ))

        # Customers & Patients
        for cust_info in org_data["customers"]:
            customer = Customer.query.filter_by(organization_id=org.id, phone=cust_info["phone"]).first()
            if not customer:
                customer = Customer(
                    organization_id=org.id,
                    name=cust_info["name"],
                    phone=cust_info["phone"],
                    email=cust_info["email"],
                    gender=cust_info["gender"],
                    source="Online Booking",
                    notes="Verified verified client"
                )
                db.session.add(customer)

            patient = Patient.query.filter_by(organization_id=org.id, phone=cust_info["phone"]).first()
            if not patient:
                patient = Patient(
                    organization_id=org.id,
                    name=cust_info["name"],
                    phone=cust_info["phone"],
                    email=cust_info["email"],
                    gender=cust_info["gender"]
                )
                db.session.add(patient)

        # Commit so appointments can link foreign keys
        db.session.flush()

        # Appointments
        for appt_info in org_data["appointments"]:
            appt_time = (now + timedelta(days=appt_info["days_offset"])).replace(hour=10, minute=30, second=0, microsecond=0)
            existing_appt = Appointment.query.filter_by(
                organization_id=org.id,
                customer_phone=appt_info["phone"],
                status=appt_info["status"]
            ).first()

            if not existing_appt:
                appt = Appointment(
                    customer_name=appt_info["customer"],
                    customer_phone=appt_info["phone"],
                    appointment_date=appt_time,
                    status=appt_info["status"],
                    payment_status=appt_info["payment"],
                    organization_id=org.id
                )
                db.session.add(appt)
                db.session.flush()

                # Appointment Transaction if paid
                if appt_info["payment"] == "Paid" and appt_info["amount"] > 0:
                    db.session.add(AppointmentTransaction(
                        appointment_id=appt.id,
                        organization_id=org.id,
                        amount=appt_info["amount"],
                        transaction_type="Payment",
                        payment_method="UPI" if org.sector == "Healthcare" else "Card",
                        transaction_reference=f"TXN-{appt.id}-{int(datetime.utcnow().timestamp())}",
                        status="Success",
                        processed_by_type="Organization",
                        processed_by_id=org.id,
                        remarks=f"Payment received for {appt_info['service']}"
                    ))

                # MessageLog
                db.session.add(MessageLog(
                    organization_id=org.id,
                    recipient_number=appt_info["phone"],
                    message_type="WhatsApp",
                    message_content=f"Hello {appt_info['customer']}, your booking for {appt_info['service']} at {org.name} is confirmed for {appt_time.strftime('%b %d, %Y at %I:%M %p')}.",
                    status="Delivered",
                    sent_at=now - timedelta(hours=2),
                    related_appointment_id=appt.id
                ))

        db.session.commit()

    print("=" * 60)
    print("✓ AppointoCare Sample Data Migration Completed Successfully!")
    print("  Organizations : 9 Multi-Industry Entities (ORG1 to ORG9)")
    print("  SuperAdmin    : superadmin / Admin@12345")
    print("  Org Admins    : org1..org9 / Org@12345")
    print("  Staff Users   : staff1, doc_sarah, alex_wealth, etc. / Staff@12345")
    print("=" * 60)


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        reset_requested = "--reset" in sys.argv or os.getenv("RESET_DATA", "false").lower() == "true"
        seed_all_sample_data(reset=reset_requested)
