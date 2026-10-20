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

    versions = db.relationship("DocumentVersion", backref="document", lazy=True, cascade="all, delete-orphan")


# -----------------------------------------------------------------------------
# Iteration 5: Enterprise Task Management, Pipelines & Shared Capabilities
# -----------------------------------------------------------------------------
class TaskItem(db.Model):
    __tablename__ = "task_items"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    priority = db.Column(db.String(30), default="Medium")  # Urgent, High, Medium, Low
    status = db.Column(db.String(30), default="Pending")    # Pending, In_Progress, Completed, Overdue, Cancelled
    assigned_to_user_id = db.Column(db.Integer, nullable=True)
    assigned_to_name = db.Column(db.String(100), nullable=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id", ondelete="SET NULL"), nullable=True, index=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    reminder_at = db.Column(db.DateTime, nullable=True)
    escalation_level = db.Column(db.Integer, default=0)
    completed_at = db.Column(db.DateTime, nullable=True)
    tags = db.Column(db.String(150), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    __table_args__ = (
        db.Index("idx_task_org_status", "organization_id", "status"),
    )


class BusinessPipeline(db.Model):
    __tablename__ = "business_pipelines"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    sector = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    stages = db.Column(db.JSON, default=list)  # [{id: "lead", name: "New Lead", order: 1, probability: 20}]
    deals = db.Column(db.JSON, default=list)   # [{id: "deal-1", title: "Acme Deal", stage_id: "lead", value: 15000}]
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    __table_args__ = (
        db.Index("idx_pipeline_org_sector", "organization_id", "sector"),
    )


class DocumentVersion(db.Model):
    __tablename__ = "document_versions"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_document_id = db.Column(db.Integer, db.ForeignKey("customer_documents.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = db.Column(db.Integer, nullable=False, default=1)
    file_name = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, default=0)
    storage_url_or_content = db.Column(db.Text, nullable=True)
    access_level = db.Column(db.String(50), default="Customer_Facing")  # Public, Customer_Facing, Internal_Staff, Practitioner_Only
    expiry_date = db.Column(db.DateTime, nullable=True)
    uploaded_by = db.Column(db.String(100), default="Staff")
    download_count = db.Column(db.Integer, default=0)
    change_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ApprovalRecord(db.Model):
    __tablename__ = "approval_records"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    entity_type = db.Column(db.String(60), nullable=False)  # treatment_plan, estimate, quote, engagement_letter, timesheet
    entity_id = db.Column(db.Integer, nullable=False)
    signee_name = db.Column(db.String(150), nullable=False)
    signee_email = db.Column(db.String(150), nullable=True)
    signee_role = db.Column(db.String(50), default="Customer")  # Customer, Doctor, Manager, Client
    status = db.Column(db.String(30), default="Approved")       # Pending, Approved, Rejected
    signature_hash = db.Column(db.String(255), nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    signed_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# -----------------------------------------------------------------------------
# Iteration 5: Healthcare Clinical Architecture & ABDM Standards Foundations
# -----------------------------------------------------------------------------
class ClinicalEncounter(db.Model):
    __tablename__ = "clinical_encounters"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True, index=True)
    practitioner_id = db.Column(db.Integer, nullable=True)
    practitioner_name = db.Column(db.String(150), nullable=False)
    practitioner_reg_no = db.Column(db.String(100), nullable=True)
    encounter_date = db.Column(db.DateTime, default=datetime.utcnow)
    encounter_type = db.Column(db.String(50), default="Outpatient")  # Outpatient, Teleconsult, Emergency, Follow_Up
    chief_complaints = db.Column(db.Text, nullable=True)
    vitals = db.Column(db.JSON, default=dict)  # bp_systolic, bp_diastolic, pulse, temp, spo2, weight, height, bmi
    allergies = db.Column(db.JSON, default=list)  # [{allergen: "Penicillin", severity: "High"}]
    medication_history = db.Column(db.JSON, default=list)
    clinical_notes = db.Column(db.Text, nullable=True)  # Structured SOAP notes
    diagnosis = db.Column(db.JSON, default=list)  # [{code: "ICD-10", description: "Essential Hypertension"}]
    treatment_plan = db.Column(db.Text, nullable=True)
    prescription_data = db.Column(db.JSON, default=dict)  # {rx_number, medications: [...], advice: "..."}
    follow_up_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(30), default="In_Progress")  # Draft, In_Progress, Signed_Off
    revision_number = db.Column(db.Integer, default=1)
    signed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    __table_args__ = (
        db.Index("idx_encounter_patient_org", "patient_id", "organization_id"),
    )


class AppointmentWaitlist(db.Model):
    __tablename__ = "appointment_waitlists"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_name = db.Column(db.String(150), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey("services.id", ondelete="SET NULL"), nullable=True)
    service_name = db.Column(db.String(150), nullable=True)
    preferred_practitioner = db.Column(db.String(150), nullable=True)
    preferred_date_start = db.Column(db.DateTime, nullable=True)
    preferred_date_end = db.Column(db.DateTime, nullable=True)
    urgency = db.Column(db.String(30), default="Routine")  # Routine, Urgent, Critical
    status = db.Column(db.String(30), default="Waiting")    # Waiting, Offered, Booked, Expired, Cancelled
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    __table_args__ = (
        db.Index("idx_waitlist_org_status", "organization_id", "status"),
    )


class ResourceRoomSchedule(db.Model):
    __tablename__ = "resource_room_schedules"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    branch_id = db.Column(db.Integer, nullable=True)
    resource_name = db.Column(db.String(150), nullable=False)  # e.g. "Consultation Room 102", "OT Suite 1"
    resource_type = db.Column(db.String(50), default="Room")   # Room, Chair, OT, Machine, Cabin
    assigned_practitioner = db.Column(db.String(150), nullable=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id", ondelete="SET NULL"), nullable=True)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(30), default="Reserved")  # Reserved, Occupied, Cleaned, Maintenance
    notes = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.Index("idx_resource_org_time", "organization_id", "start_time", "end_time"),
    )


class DiagnosticLabOrder(db.Model):
    __tablename__ = "diagnostic_lab_orders"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    encounter_id = db.Column(db.Integer, db.ForeignKey("clinical_encounters.id", ondelete="SET NULL"), nullable=True)
    order_number = db.Column(db.String(80), nullable=False)
    test_name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(50), default="Pathology")  # Pathology, Radiology, Biochemistry, Hematology
    ordering_doctor = db.Column(db.String(150), nullable=True)
    status = db.Column(db.String(40), default="Ordered")  # Ordered, Sample_Collected, Result_Uploaded, Reviewed_By_Doctor
    results_data = db.Column(db.JSON, default=dict)
    attachment_url = db.Column(db.String(255), nullable=True)
    doctor_review_notes = db.Column(db.Text, nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    critical_flag = db.Column(db.Boolean, default=False)
    escalated_to_clinician = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    __table_args__ = (
        db.Index("idx_lab_order_org_status", "organization_id", "status"),
    )


class ABDMConsentArtifact(db.Model):
    __tablename__ = "abdm_consent_artifacts"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    consent_request_id = db.Column(db.String(100), nullable=False, unique=True)
    hiu_id = db.Column(db.String(100), nullable=True)
    hip_id = db.Column(db.String(100), nullable=True)
    purpose_code = db.Column(db.String(50), default="CAREMGT")  # CAREMGT, BTG, PUBHLTH
    status = db.Column(db.String(30), default="GRANTED")       # REQUESTED, GRANTED, REVOKED, EXPIRED
    granted_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    fhir_bundle_id = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class MedicationRefillRequest(db.Model):
    __tablename__ = "medication_refill_requests"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False, index=True)
    encounter_id = db.Column(db.Integer, db.ForeignKey("clinical_encounters.id", ondelete="SET NULL"), nullable=True)
    medication_name = db.Column(db.String(150), nullable=False)
    dosage = db.Column(db.String(100), nullable=True)
    quantity_requested = db.Column(db.Integer, default=30)
    refills_remaining = db.Column(db.Integer, default=2)
    status = db.Column(db.String(40), default="Pending_Approval")  # Pending_Approval, Approved, Dispensed, Denied
    approving_doctor = db.Column(db.String(150), nullable=True)
    pharmacy_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)


class RetailInventoryItem(db.Model):
    __tablename__ = "retail_inventory_items"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    sku = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(80), default="Retail")
    quantity_on_hand = db.Column(db.Integer, default=0)
    reorder_level = db.Column(db.Integer, default=5)
    unit_cost = db.Column(db.Float, default=0.0)
    unit_price = db.Column(db.Float, default=0.0)
    barcode = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(40), default="In_Stock")  # In_Stock, Low_Stock, Out_Of_Stock
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)


class CancellationRecoveryOffer(db.Model):
    __tablename__ = "cancellation_recovery_offers"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    cancelled_appointment_id = db.Column(db.Integer, nullable=True)
    waitlist_id = db.Column(db.Integer, db.ForeignKey("appointment_waitlists.id", ondelete="SET NULL"), nullable=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    customer_name = db.Column(db.String(150), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    offered_slot = db.Column(db.DateTime, nullable=False)
    service_name = db.Column(db.String(150), default="Service Appointment")
    expires_at = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(40), default="Offered")  # Offered, Accepted, Expired, Declined
    recovered_revenue = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class HouseholdRelationship(db.Model):
    __tablename__ = "household_relationships"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    household_name = db.Column(db.String(150), nullable=False)
    head_customer_id = db.Column(db.Integer, db.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    member_customer_id = db.Column(db.Integer, db.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    relationship_type = db.Column(db.String(50), default="Spouse")  # Spouse, Dependent, Child, Parent, Partner
    consolidated_aum = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class RiskSuitabilityProfile(db.Model):
    __tablename__ = "risk_suitability_profiles"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    risk_tolerance_category = db.Column(db.String(50), default="Moderate")  # Conservative, Moderate, Growth, Aggressive
    risk_score = db.Column(db.Integer, default=50)  # 0 - 100
    investment_horizon_years = db.Column(db.Integer, default=5)
    liquidity_needs = db.Column(db.String(50), default="Medium")
    documented_objective = db.Column(db.String(255), default="Long-term capital appreciation with moderate income")
    advisor_name = db.Column(db.String(150), nullable=True)
    status = db.Column(db.String(40), default="Approved")  # Draft, Pending_Client_Signature, Approved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)


class InsurancePolicyRecord(db.Model):
    __tablename__ = "insurance_policy_records"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    policy_number = db.Column(db.String(100), nullable=False)
    carrier_name = db.Column(db.String(150), nullable=False)
    plan_type = db.Column(db.String(80), default="Comprehensive Health")  # Health, Motor, Life, Commercial, Term
    sum_insured = db.Column(db.Float, default=500000.0)
    annual_premium = db.Column(db.Float, nullable=False)
    commission_rate_pct = db.Column(db.Float, default=15.0)
    effective_date = db.Column(db.DateTime, nullable=False)
    expiry_date = db.Column(db.DateTime, nullable=False)
    renewal_status = db.Column(db.String(40), default="Upcoming")  # Upcoming, Re-quoted, Renewed, Lapsed
    retention_risk_score = db.Column(db.Integer, default=20)  # 0 - 100
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)


class PolicyEndorsement(db.Model):
    __tablename__ = "policy_endorsements"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    policy_id = db.Column(db.Integer, db.ForeignKey("insurance_policy_records.id", ondelete="CASCADE"), nullable=False)
    endorsement_type = db.Column(db.String(80), default="Nominee Change")  # Address Change, Nominee Change, Sum Insured Elevation, Member Addition
    change_summary = db.Column(db.String(255), nullable=False)
    premium_delta = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(40), default="Approved")  # Submitted, Carrier_Review, Approved, Rejected
    effective_date = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class BespokeOrder(db.Model):
    __tablename__ = "bespoke_orders"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    order_number = db.Column(db.String(80), nullable=False)
    garment_type = db.Column(db.String(100), default="Bespoke Tuxedo")
    fabric_choice = db.Column(db.String(150), default="Super 150s Merino Wool (Navy)")
    measurements_profile = db.Column(db.JSON, default=dict)
    design_sketch_url = db.Column(db.String(255), nullable=True)
    fitting_date = db.Column(db.DateTime, nullable=True)
    production_stage = db.Column(db.String(50), default="Pattern_Cutting")  # Pattern_Cutting, In_Tailoring, First_Fitting, Alterations, Ready_For_Pickup, Delivered
    total_price = db.Column(db.Float, default=45000.0)
    deposit_paid = db.Column(db.Float, default=20000.0)
    balance_due = db.Column(db.Float, default=25000.0)
    pickup_ready = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)


class ClientWishlist(db.Model):
    __tablename__ = "client_wishlists"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    item_name = db.Column(db.String(150), nullable=False)
    sku = db.Column(db.String(80), nullable=True)
    size_preference = db.Column(db.String(50), default="40R")
    estimated_price = db.Column(db.Float, default=0.0)
    stylist_notes = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(40), default="Saved")  # Saved, Reserved, Purchased
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class UniversityProgram(db.Model):
    __tablename__ = "university_programs"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    institution_name = db.Column(db.String(150), nullable=False)
    program_title = db.Column(db.String(150), nullable=False)
    country = db.Column(db.String(80), default="United Kingdom")
    intake_semester = db.Column(db.String(50), default="Fall 2027")
    annual_tuition = db.Column(db.Float, default=24000.0)
    currency = db.Column(db.String(10), default="GBP")
    min_gpa = db.Column(db.Float, default=3.0)
    min_ielts = db.Column(db.Float, default=6.5)
    global_ranking = db.Column(db.Integer, default=120)
    status = db.Column(db.String(40), default="Active")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class StudentReadinessScore(db.Model):
    __tablename__ = "student_readiness_scores"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    readiness_score = db.Column(db.Integer, default=75)  # 0 - 100
    gpa = db.Column(db.Float, default=3.4)
    english_score = db.Column(db.String(40), default="IELTS 7.0")
    sop_status = db.Column(db.String(40), default="Drafted")  # Missing, Drafted, Reviewed, Approved
    lor_count = db.Column(db.Integer, default=2)
    missing_documents = db.Column(db.JSON, default=list)
    counselor_name = db.Column(db.String(150), default="Lead Counselor")
    readiness_tier = db.Column(db.String(40), default="High")  # Low, Moderate, High, Ready_To_Lodge
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)


class LegalMatter(db.Model):
    __tablename__ = "legal_matters"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id = db.Column(db.Integer, db.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    matter_number = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    practice_area = db.Column(db.String(100), default="Commercial Litigation")
    adverse_party = db.Column(db.String(150), nullable=True)
    conflict_cleared = db.Column(db.Boolean, default=True)
    limitation_date = db.Column(db.DateTime, nullable=True)
    retainer_balance = db.Column(db.Float, default=75000.0)
    trust_account_balance = db.Column(db.Float, default=50000.0)
    billable_hours_recorded = db.Column(db.Float, default=12.5)
    hourly_rate = db.Column(db.Float, default=12500.0)
    status = db.Column(db.String(40), default="Active")  # In_Conflict_Check, Active, Suspended, Closed
    lead_advocate = db.Column(db.String(150), default="Senior Advocate")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)


class AdverseConflictReview(db.Model):
    __tablename__ = "adverse_conflict_reviews"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    matter_id = db.Column(db.Integer, db.ForeignKey("legal_matters.id", ondelete="CASCADE"), nullable=False)
    search_term = db.Column(db.String(150), nullable=False)
    matched_entity = db.Column(db.String(150), nullable=True)
    similarity_score = db.Column(db.Float, default=0.0)
    clearance_decision = db.Column(db.String(40), default="Cleared")  # Potential_Conflict, Cleared, Disqualified
    ethical_notes = db.Column(db.Text, nullable=True)
    reviewed_by_partner = db.Column(db.String(150), default="Managing Partner")
    reviewed_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PropertyReservation(db.Model):
    __tablename__ = "property_reservations"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    buyer_id = db.Column(db.Integer, db.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    property_name = db.Column(db.String(150), nullable=False)
    unit_number = db.Column(db.String(50), default="Tower A - 1402")
    list_price = db.Column(db.Float, default=18500000.0)
    offer_price = db.Column(db.Float, default=17800000.0)
    earnest_deposit = db.Column(db.Float, default=500000.0)
    status = db.Column(db.String(40), default="Reserved")  # Site_Visited, Offer_Made, Reserved, Agreement_Signed, Closed
    agent_name = db.Column(db.String(150), default="Senior Broker")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)


class ArchitectureProject(db.Model):
    __tablename__ = "architecture_projects"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    client_id = db.Column(db.Integer, db.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    project_title = db.Column(db.String(150), nullable=False)
    total_budget = db.Column(db.Float, default=12500000.0)
    actual_cost_to_date = db.Column(db.Float, default=4200000.0)
    drawings_revision_count = db.Column(db.Integer, default=4)
    open_rfis_count = db.Column(db.Integer, default=2)
    variation_orders_amount = db.Column(db.Float, default=450000.0)
    project_stage = db.Column(db.String(50), default="Design_Development")  # Schematic, Design_Development, Permitting, Construction_Admin, Handover
    lead_architect = db.Column(db.String(150), default="Principal Architect")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)


class ProjectProfitability(db.Model):
    __tablename__ = "project_profitability"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    project_code = db.Column(db.String(80), nullable=False)
    project_name = db.Column(db.String(150), nullable=False)
    planned_budget = db.Column(db.Float, default=2500000.0)
    actual_cost_burn = db.Column(db.Float, default=1650000.0)
    billable_invoiced = db.Column(db.Float, default=2100000.0)
    target_margin_pct = db.Column(db.Float, default=35.0)
    current_margin_pct = db.Column(db.Float, default=21.4)
    risk_level = db.Column(db.String(30), default="Caution")  # Healthy, Caution, Critical_Overrun
    estimate_to_complete = db.Column(db.Float, default=600000.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)


class ResourceCapacity(db.Model):
    __tablename__ = "resource_capacities"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    consultant_name = db.Column(db.String(150), nullable=False)
    role_title = db.Column(db.String(100), default="Senior Consultant")
    skill_tags = db.Column(db.JSON, default=list)
    weekly_capacity_hours = db.Column(db.Float, default=40.0)
    billable_assigned_hours = db.Column(db.Float, default=34.0)
    utilization_percentage = db.Column(db.Float, default=85.0)
    bench_availability = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)


class IncidentTicket(db.Model):
    __tablename__ = "incident_tickets"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    ticket_number = db.Column(db.String(80), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    severity = db.Column(db.String(10), default="P2")  # P1, P2, P3, P4
    client_name = db.Column(db.String(150), default="Enterprise Client")
    assigned_engineer = db.Column(db.String(150), default="On-Call Lead")
    status = db.Column(db.String(40), default="Investigating")  # Triggered, Investigating, Mitigated, Resolved
    response_deadline = db.Column(db.DateTime, nullable=False)
    resolution_deadline = db.Column(db.DateTime, nullable=False)
    resolved_at = db.Column(db.DateTime, nullable=True)
    sla_breached = db.Column(db.Boolean, default=False)
    postmortem_notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)


class AutomationExecutionLog(db.Model):
    __tablename__ = "automation_execution_logs"

    id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, index=True)
    rule_id = db.Column(db.Integer, db.ForeignKey("automation_rules.id", ondelete="SET NULL"), nullable=True)
    rule_name = db.Column(db.String(150), nullable=False)
    event_trigger = db.Column(db.String(100), nullable=False)
    action_type = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(40), default="Success")  # Success, Failed, Pending_Approval, Retrying
    details = db.Column(db.JSON, default=dict)
    executed_at = db.Column(db.DateTime, default=datetime.utcnow)





