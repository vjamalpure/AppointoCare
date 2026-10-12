from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

db = SQLAlchemy()


class Organization(db.Model):
    __tablename__ = "organizations"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    sector = db.Column(db.String(50), nullable=False)  # hospital, finance, retail
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)

    # Contact & Profile
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    logo_url = db.Column(db.String(255), nullable=True)

    # WhatsApp & Feature Toggles
    whatsapp_enabled = db.Column(db.Boolean, default=True)
    whatsapp_monthly_limit = db.Column(db.Integer, default=1000)
    whatsapp_messages_used = db.Column(db.Integer, default=0)
    booking_flow_enabled = db.Column(db.Boolean, default=True)
    auto_welcome_enabled = db.Column(db.Boolean, default=True)
    reminders_enabled = db.Column(db.Boolean, default=True)
    campaigns_enabled = db.Column(db.Boolean, default=True)

    # Subscription details
    subscription_status = db.Column(db.String(50), default="Active")  # Active, Paused, Stopped
    subscription_plan = db.Column(db.String(100), default="Basic")  # Basic, Premium, Enterprise
    subscription_start = db.Column(db.DateTime, default=datetime.utcnow)
    subscription_end = db.Column(db.DateTime, default=lambda: datetime.utcnow() + timedelta(days=30))
    next_billing_date = db.Column(db.DateTime, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Relationships
    appointments = db.relationship("Appointment", backref="organization", lazy=True)
    org_transactions = db.relationship("OrganizationTransaction", backref="organization", lazy=True)
    whatsapp_config = db.relationship("WhatsAppConfig", backref="organization", uselist=False, lazy=True, cascade="all, delete-orphan")
    payment_config = db.relationship("PaymentConfig", backref="organization", uselist=False, lazy=True, cascade="all, delete-orphan")


class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(150), nullable=False)
    customer_phone = db.Column(db.String(15), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default="Booked")  # Booked, Cancelled, Completed
    payment_status = db.Column(db.String(50), default="Pending")  # Paid, Unpaid

    # Metadata & Relations
    service_name = db.Column(db.String(150), nullable=True)
    staff_name = db.Column(db.String(150), nullable=True)
    customer_id = db.Column(db.Integer, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # Relationship for payments related to this appointment
    appointment_transactions = db.relationship("AppointmentTransaction", backref="appointment", lazy=True)


class AppointmentTransaction(db.Model):
    """
    Stores payment or refund transactions linked to a specific appointment.
    """
    __tablename__ = "appointment_transactions"

    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id"), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id"), nullable=False)

    # Transaction details
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(50))  # Payment, Refund
    payment_method = db.Column(db.String(50))  # UPI, Cash, Card, NetBanking, Wallet
    transaction_reference = db.Column(db.String(100), unique=True, nullable=True)
    status = db.Column(db.String(50), default="Success")  # Success, Failed, Pending

    # Who processed this transaction (Admin or Organization Staff)
    processed_by_type = db.Column(db.String(50))  # 'Admin', 'Organization'
    processed_by_id = db.Column(db.Integer, nullable=True)  # references Admin.id or Organization.id

    remarks = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)


class OrganizationTransaction(db.Model):
    """
    Stores all transactions made by an organization for subscriptions or credits.
    """
    __tablename__ = "organization_transactions"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id"), nullable=False)

    # Transaction details
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(50))  # Subscription, Credit, Refund
    payment_method = db.Column(db.String(50))  # UPI, Cash, Card, NetBanking, Wallet
    invoice_id = db.Column(db.String(100), unique=True, nullable=True)
    period_start = db.Column(db.DateTime, nullable=True)
    period_end = db.Column(db.DateTime, nullable=True)
    remarks = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), default="Success")  # Success, Failed, Pending

    # Who processed the payment (Admin or Organization)
    processed_by_type = db.Column(db.String(50))  # 'Admin', 'Organization'
    processed_by_id = db.Column(db.Integer, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)


class Admin(db.Model):
    __tablename__ = "admins"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default="SuperAdmin")  # SuperAdmin, Manager

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)


# --- User (Organization Staff) ---
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id"), nullable=False)
    name = db.Column(db.String(150), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default="Staff")  # Staff, Manager, Receptionist, etc.
    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)


# --- Patient (Appointment Client) ---
class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id"), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    dob = db.Column(db.Date, nullable=True)
    address = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)


# --- MessageLog (WhatsApp/SMS/Email) ---
class MessageLog(db.Model):
    __tablename__ = "message_logs"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id"), nullable=False)
    recipient_number = db.Column(db.String(20), nullable=False)
    message_type = db.Column(db.String(50), nullable=False)  # WhatsApp, SMS, Email
    message_content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(50), default="Sent")  # Sent, Failed, Delivered
    direction = db.Column(db.String(20), default="Outbound")
    provider_message_id = db.Column(db.String(200), nullable=True)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    related_appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id"), nullable=True)
    remarks = db.Column(db.String(255), nullable=True)


# --- Subscription (Plan Management) ---
class Subscription(db.Model):
    __tablename__ = "subscriptions"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id"), nullable=False)
    plan_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), default="Active")  # Active, Paused, Cancelled
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime, nullable=True)
    next_billing_date = db.Column(db.DateTime, nullable=True)
    amount = db.Column(db.Float, nullable=False)
    remarks = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)


class Service(db.Model):
    __tablename__ = "services"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id"), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(100), nullable=True)
    price = db.Column(db.Float, nullable=False, default=0.0)
    duration_minutes = db.Column(db.Integer, nullable=False, default=30)
    active = db.Column(db.Boolean, default=True)
    sector = db.Column(db.String(50), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)


class Customer(db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id"), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    dob = db.Column(db.Date, nullable=True)
    address = db.Column(db.String(255), nullable=True)
    tags = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    source = db.Column(db.String(100), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id"), nullable=True)
    user_id = db.Column(db.Integer, nullable=True)
    user_role = db.Column(db.String(50), nullable=True)
    action = db.Column(db.String(150), nullable=False)
    entity = db.Column(db.String(100), nullable=True)
    entity_id = db.Column(db.Integer, nullable=True)
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(100), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SubscriptionPlan(db.Model):
    __tablename__ = "subscription_plans"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False, default=0.0)
    billing_cycle = db.Column(db.String(20), nullable=False, default="monthly")
    feature_limits = db.Column(db.JSON, nullable=False, default=dict)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)


class Campaign(db.Model):
    __tablename__ = "campaigns"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id"), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    channel = db.Column(db.String(30), nullable=False, default="WhatsApp")
    message = db.Column(db.Text, nullable=False)
    audience_filter = db.Column(db.JSON, nullable=False, default=dict)
    status = db.Column(db.String(30), nullable=False, default="Draft")
    scheduled_at = db.Column(db.DateTime, nullable=True)
    sent_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id"), nullable=False)
    recipient_type = db.Column(db.String(30), nullable=False, default="organization")
    recipient_id = db.Column(db.Integer, nullable=True)
    channel = db.Column(db.String(30), nullable=False, default="in_app")
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), nullable=False, default="unread")
    read_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Branch(db.Model):
    __tablename__ = "branches"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id"), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    timezone = db.Column(db.String(50), nullable=False, default="UTC")
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)


class SectorTemplate(db.Model):
    __tablename__ = "sector_templates"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    services = db.Column(db.JSON, nullable=False, default=list)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PaymentOrder(db.Model):
    __tablename__ = "payment_orders"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id"), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id"), nullable=True)
    provider = db.Column(db.String(40), nullable=False)
    provider_order_id = db.Column(db.String(150), unique=True, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), nullable=False, default="INR")
    status = db.Column(db.String(30), nullable=False, default="created")
    provider_metadata = db.Column("metadata", db.JSON, nullable=False, default=dict)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)


class ProviderEvent(db.Model):
    __tablename__ = "provider_events"

    id = db.Column(db.Integer, primary_key=True)
    provider = db.Column(db.String(40), nullable=False)
    event_id = db.Column(db.String(200), nullable=False)
    event_type = db.Column(db.String(100), nullable=False)
    payload = db.Column(db.JSON, nullable=False, default=dict)
    status = db.Column(db.String(30), nullable=False, default="received")
    error_message = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime, nullable=True)
    __table_args__ = (db.UniqueConstraint("provider", "event_id", name="uq_provider_event"),)


class IndustryRecord(db.Model):
    __tablename__ = "industry_records"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id"), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id"), nullable=True)
    customer_id = db.Column(db.Integer, nullable=True)
    sector = db.Column(db.String(50), nullable=False)
    record_type = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    data = db.Column(db.JSON, nullable=False, default=dict)
    status = db.Column(db.String(50), default="Active")
    created_by_user = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)


class GlobalSetting(db.Model):
    __tablename__ = "global_settings"

    key = db.Column(db.String(120), primary_key=True)
    value = db.Column(db.Text, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class FinancialLedgerEntry(db.Model):
    __tablename__ = "financial_ledger_entries"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id"), nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=True, index=True)
    record_id = db.Column(db.Integer, db.ForeignKey("industry_records.id"), nullable=True, index=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id"), nullable=True)
    entry_type = db.Column(db.String(50), nullable=False)  # CREDIT_ISSUANCE, CREDIT_REDEMPTION, CREDIT_REVERSAL, RETAINER_DEPOSIT, RETAINER_TIME_LOGGED
    units_delta = db.Column(db.Float, nullable=False)
    balance_after = db.Column(db.Float, nullable=False)
    currency_or_unit = db.Column(db.String(20), default="sessions")  # sessions, hours, INR, USD
    monetary_equivalent = db.Column(db.Float, nullable=True, default=0.0)
    reference_id = db.Column(db.String(100), nullable=True)
    description = db.Column(db.Text, nullable=True)
    created_by_user = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.Index("idx_fin_ledger_org_record", "organization_id", "record_id"),
    )


# -----------------------------------------------------------------------------
# Multi-Tenant Service Integrations: Meta WhatsApp & Razorpay Route
# -----------------------------------------------------------------------------
class ServiceStatus:
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    INACTIVE = "INACTIVE"
    CHOICES = [ACTIVE, SUSPENDED, INACTIVE]


class WhatsAppConfig(db.Model):
    __tablename__ = "whatsapp_configs"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)

    # Meta WABA & Phone Credentials (Onboarded via Embedded Signup)
    waba_id = db.Column(db.String(100), nullable=True, index=True)
    phone_number_id = db.Column(db.String(100), nullable=True, index=True)
    business_account_id = db.Column(db.String(100), nullable=True)
    display_phone_number = db.Column(db.String(50), nullable=True)
    verified_name = db.Column(db.String(200), nullable=True)
    quality_rating = db.Column(db.String(50), default="GREEN")

    # Tokens & Secrets (Stored Encrypted)
    access_token_encrypted = db.Column(db.Text, nullable=True)
    token_expires_at = db.Column(db.DateTime, nullable=True)
    webhook_verify_token = db.Column(db.String(255), nullable=True)

    # Service Controls & Billing Line
    service_status = db.Column(db.String(20), nullable=False, default=ServiceStatus.INACTIVE, index=True)  # ACTIVE, SUSPENDED, INACTIVE
    suspension_reason = db.Column(db.String(255), nullable=True)
    meta_credit_line_status = db.Column(db.String(50), default="SHARED_MASTER")  # Master Centralized Line
    monthly_limit = db.Column(db.Integer, default=1000)
    messages_sent_this_month = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)


class PaymentConfig(db.Model):
    __tablename__ = "payment_configs"

    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)

    # Razorpay Route Connected Sub-Account
    razorpay_account_id = db.Column(db.String(100), nullable=True, index=True)  # acc_xxxx
    merchant_name = db.Column(db.String(200), nullable=True)
    merchant_email = db.Column(db.String(150), nullable=True)
    onboarding_status = db.Column(db.String(50), default="PENDING")  # PENDING, LINKED, VERIFIED

    # Service Controls & Split Platform Commission
    service_status = db.Column(db.String(20), nullable=False, default=ServiceStatus.INACTIVE, index=True)  # ACTIVE, SUSPENDED, INACTIVE
    suspension_reason = db.Column(db.String(255), nullable=True)
    platform_commission_rate = db.Column(db.Float, nullable=False, default=0.05)  # 5% commission retained
    currency = db.Column(db.String(10), default="INR")
    auto_capture = db.Column(db.Boolean, default=True)

    # OAuth Partner Tokens
    oauth_access_token_encrypted = db.Column(db.Text, nullable=True)
    oauth_refresh_token_encrypted = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)


# Alias Tenant to Organization for clean multi-tenant domain nomenclature
Tenant = Organization


# -----------------------------------------------------------------------------
# Enterprise Workflow, Custom Fields, Automation & Self-Service Portal Models
# -----------------------------------------------------------------------------
class CustomFieldDefinition(db.Model):
    __tablename__ = "custom_field_definitions"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    sector = db.Column(db.String(50), nullable=False)
    entity_type = db.Column(db.String(50), default="record")  # record, customer, appointment
    field_key = db.Column(db.String(80), nullable=False)
    field_label = db.Column(db.String(150), nullable=False)
    field_type = db.Column(db.String(30), default="text")  # text, number, date, select, boolean, file
    is_required = db.Column(db.Boolean, default=False)
    options = db.Column(db.JSON, default=list)  # for select dropdowns
    default_value = db.Column(db.String(255), nullable=True)
    validation_rules = db.Column(db.JSON, default=dict)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    __table_args__ = (
        db.Index("idx_custom_field_org_sector", "organization_id", "sector", "entity_type"),
    )


class WorkflowDefinition(db.Model):
    __tablename__ = "workflow_definitions"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    sector = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    entity_type = db.Column(db.String(50), default="record")
    initial_status = db.Column(db.String(50), default="Draft")
    statuses = db.Column(db.JSON, default=list)  # [{id: "draft", label: "Draft", color: "gray", sla_hours: 24}]
    transitions = db.Column(db.JSON, default=list)  # [{from: "draft", to: "review", label: "Submit", required_role: "Staff", required_fields: []}]
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    __table_args__ = (
        db.Index("idx_workflow_org_sector", "organization_id", "sector"),
    )


class WorkflowTransitionHistory(db.Model):
    __tablename__ = "workflow_transition_histories"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    record_id = db.Column(db.Integer, db.ForeignKey("industry_records.id", ondelete="CASCADE"), nullable=False, index=True)
    from_status = db.Column(db.String(50), nullable=False)
    to_status = db.Column(db.String(50), nullable=False)
    triggered_by_user = db.Column(db.String(100), nullable=True)
    user_role = db.Column(db.String(50), nullable=True)
    comment = db.Column(db.Text, nullable=True)
    transition_metadata = db.Column(db.JSON, default=dict)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.Index("idx_wf_history_rec_org", "record_id", "organization_id"),
    )


class AutomationRule(db.Model):
    __tablename__ = "automation_rules"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)
    event_trigger = db.Column(db.String(80), nullable=False)  # record.transition, appointment.booked, invoice.overdue, sla.breach
    conditions = db.Column(db.JSON, default=dict)
    action_type = db.Column(db.String(50), nullable=False)  # in_app_notification, whatsapp_alert, status_escalation, email_reminder
    action_payload = db.Column(db.JSON, default=dict)
    is_active = db.Column(db.Boolean, default=True)
    last_triggered_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class CustomerPortalSession(db.Model):
    __tablename__ = "customer_portal_sessions"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    session_token = db.Column(db.String(128), unique=True, nullable=False, index=True)
    auth_code = db.Column(db.String(10), nullable=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    communication_preferences = db.Column(db.JSON, default=lambda: {"whatsapp": True, "email": True, "sms": False})
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class CustomerDocument(db.Model):
    __tablename__ = "customer_documents"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    record_id = db.Column(db.Integer, db.ForeignKey("industry_records.id", ondelete="SET NULL"), nullable=True, index=True)
    title = db.Column(db.String(150), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), default="application/pdf")
    file_size = db.Column(db.Integer, default=0)
    storage_url_or_content = db.Column(db.Text, nullable=True)
    uploaded_by = db.Column(db.String(50), default="Customer")  # Customer, Staff
    status = db.Column(db.String(50), default="Verified")  # Pending_Review, Verified, Rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)




