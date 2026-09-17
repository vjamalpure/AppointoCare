"""Sync all schema columns and tables across models.

Revision ID: d49f8b1c2e35
Revises: c38e7a5b1d92
"""
from alembic import op
import sqlalchemy as sa


revision = "d49f8b1c2e35"
down_revision = "c38e7a5b1d92"
branch_labels = None
depends_on = None


def upgrade():
    # Ensure global_settings table
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    # 1. global_settings table
    if not inspector.has_table("global_settings"):
        op.create_table(
            "global_settings",
            sa.Column("key", sa.String(length=120), primary_key=True),
            sa.Column("value", sa.Text(), nullable=False),
            sa.Column("description", sa.String(length=255), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
        )

    # 2. industry_records table
    if not inspector.has_table("industry_records"):
        op.create_table(
            "industry_records",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("organization_id", sa.Integer(), nullable=False),
            sa.Column("appointment_id", sa.Integer(), nullable=True),
            sa.Column("customer_id", sa.Integer(), nullable=True),
            sa.Column("sector", sa.String(length=50), nullable=False),
            sa.Column("record_type", sa.String(length=80), nullable=False),
            sa.Column("title", sa.String(length=200), nullable=False),
            sa.Column("data", sa.JSON(), nullable=False),
            sa.Column("status", sa.String(length=50), nullable=True, default="Active"),
            sa.Column("created_by_user", sa.String(length=100), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
            sa.ForeignKeyConstraint(["appointment_id"], ["appointments.id"]),
        )

    # Helper for adding columns safely
    def add_col_if_missing(table_name, col):
        existing_cols = [c["name"] for c in inspector.get_columns(table_name)]
        if col.name not in existing_cols:
            op.add_column(table_name, col)

    # 3. message_logs
    add_col_if_missing("message_logs", sa.Column("created_at", sa.DateTime(), nullable=True))
    add_col_if_missing("message_logs", sa.Column("updated_at", sa.DateTime(), nullable=True))
    add_col_if_missing("message_logs", sa.Column("direction", sa.String(length=20), nullable=True, default="Outbound"))
    add_col_if_missing("message_logs", sa.Column("provider_message_id", sa.String(length=200), nullable=True))

    # 4. organizations
    add_col_if_missing("organizations", sa.Column("email", sa.String(length=120), nullable=True))
    add_col_if_missing("organizations", sa.Column("phone", sa.String(length=30), nullable=True))
    add_col_if_missing("organizations", sa.Column("address", sa.String(length=255), nullable=True))
    add_col_if_missing("organizations", sa.Column("logo_url", sa.String(length=255), nullable=True))
    add_col_if_missing("organizations", sa.Column("whatsapp_enabled", sa.Boolean(), nullable=True, default=True))
    add_col_if_missing("organizations", sa.Column("whatsapp_monthly_limit", sa.Integer(), nullable=True, default=1000))
    add_col_if_missing("organizations", sa.Column("whatsapp_messages_used", sa.Integer(), nullable=True, default=0))
    add_col_if_missing("organizations", sa.Column("booking_flow_enabled", sa.Boolean(), nullable=True, default=True))
    add_col_if_missing("organizations", sa.Column("auto_welcome_enabled", sa.Boolean(), nullable=True, default=True))
    add_col_if_missing("organizations", sa.Column("reminders_enabled", sa.Boolean(), nullable=True, default=True))
    add_col_if_missing("organizations", sa.Column("campaigns_enabled", sa.Boolean(), nullable=True, default=True))

    # 5. appointments
    add_col_if_missing("appointments", sa.Column("service_name", sa.String(length=150), nullable=True))
    add_col_if_missing("appointments", sa.Column("staff_name", sa.String(length=150), nullable=True))
    add_col_if_missing("appointments", sa.Column("customer_id", sa.Integer(), nullable=True))
    add_col_if_missing("appointments", sa.Column("notes", sa.Text(), nullable=True))

    # 6. admins
    add_col_if_missing("admins", sa.Column("name", sa.String(length=150), nullable=True))
    add_col_if_missing("admins", sa.Column("email", sa.String(length=120), nullable=True))

    # 7. users
    add_col_if_missing("users", sa.Column("name", sa.String(length=150), nullable=True))
    add_col_if_missing("users", sa.Column("email", sa.String(length=120), nullable=True))
    add_col_if_missing("users", sa.Column("phone", sa.String(length=30), nullable=True))

    # Backfill message_logs.created_at if null
    op.execute("UPDATE message_logs SET created_at = COALESCE(sent_at, CURRENT_TIMESTAMP) WHERE created_at IS NULL")


def downgrade():
    pass
