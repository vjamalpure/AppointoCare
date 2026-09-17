"""
Database initialization script.
Checks if database exists, creates it if needed, then runs migrations.
This is automatically called during container startup.
"""

import os
import sys
from urllib.parse import urlparse
import psycopg2
from psycopg2 import sql


def create_database_if_not_exists():
    """
    Connect to PostgreSQL and create the database if it doesn't exist.
    Extracts database name from DATABASE_URL environment variable.
    """
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable is not set")
        sys.exit(1)

    # Parse the DATABASE_URL
    parsed = urlparse(database_url)
    
    db_host = parsed.hostname or "localhost"
    db_port = parsed.port or 5432
    db_name = parsed.path.lstrip("/")
    db_user = parsed.username or "postgres"
    db_password = parsed.password or ""
    
    if not db_name:
        print("ERROR: Database name not specified in DATABASE_URL")
        sys.exit(1)
    
    print(f"Checking if database '{db_name}' exists on {db_host}:{db_port}...")
    
    try:
        # Connect to the default 'postgres' database to check/create our database
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"),
            [db_name]
        )
        
        if cursor.fetchone():
            print(f"✓ Database '{db_name}' already exists")
        else:
            print(f"Creating database '{db_name}'...")
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(db_name)
            ))
            print(f"✓ Database '{db_name}' created successfully")
        
        cursor.close()
        conn.close()
        
    except (Exception, psycopg2.DatabaseError) as error:
        print(f"ERROR: Failed to create/check database: {error}")
        sys.exit(1)


def ensure_schema_synced():
    """
    Connects to the application database and verifies that all expected tables
    and columns from the SQLAlchemy models exist.
    Uses 'ALTER TABLE ... ADD COLUMN IF NOT EXISTS' for seamless, safe schema healing.
    """
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        return

    print("Checking and syncing database table schemas...")
    try:
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cursor = conn.cursor()

        schema_statements = [
            # Ensure global_settings table
            """
            CREATE TABLE IF NOT EXISTS global_settings (
                key VARCHAR(120) PRIMARY KEY,
                value TEXT NOT NULL,
                description VARCHAR(255),
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            # Ensure industry_records table
            """
            CREATE TABLE IF NOT EXISTS industry_records (
                id SERIAL PRIMARY KEY,
                organization_id INTEGER NOT NULL REFERENCES organizations(id),
                appointment_id INTEGER REFERENCES appointments(id),
                customer_id INTEGER,
                sector VARCHAR(50) NOT NULL,
                record_type VARCHAR(80) NOT NULL,
                title VARCHAR(200) NOT NULL,
                data JSON NOT NULL DEFAULT '{}',
                status VARCHAR(50) DEFAULT 'Active',
                created_by_user VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            );
            """,
            # message_logs columns
            "ALTER TABLE message_logs ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;",
            "ALTER TABLE message_logs ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP;",
            "ALTER TABLE message_logs ADD COLUMN IF NOT EXISTS direction VARCHAR(20) DEFAULT 'Outbound';",
            "ALTER TABLE message_logs ADD COLUMN IF NOT EXISTS provider_message_id VARCHAR(200);",
            "UPDATE message_logs SET created_at = COALESCE(sent_at, CURRENT_TIMESTAMP) WHERE created_at IS NULL;",
            # organizations columns
            "ALTER TABLE organizations ADD COLUMN IF NOT EXISTS email VARCHAR(120);",
            "ALTER TABLE organizations ADD COLUMN IF NOT EXISTS phone VARCHAR(30);",
            "ALTER TABLE organizations ADD COLUMN IF NOT EXISTS address VARCHAR(255);",
            "ALTER TABLE organizations ADD COLUMN IF NOT EXISTS logo_url VARCHAR(255);",
            "ALTER TABLE organizations ADD COLUMN IF NOT EXISTS whatsapp_enabled BOOLEAN DEFAULT TRUE;",
            "ALTER TABLE organizations ADD COLUMN IF NOT EXISTS whatsapp_monthly_limit INTEGER DEFAULT 1000;",
            "ALTER TABLE organizations ADD COLUMN IF NOT EXISTS whatsapp_messages_used INTEGER DEFAULT 0;",
            "ALTER TABLE organizations ADD COLUMN IF NOT EXISTS booking_flow_enabled BOOLEAN DEFAULT TRUE;",
            "ALTER TABLE organizations ADD COLUMN IF NOT EXISTS auto_welcome_enabled BOOLEAN DEFAULT TRUE;",
            "ALTER TABLE organizations ADD COLUMN IF NOT EXISTS reminders_enabled BOOLEAN DEFAULT TRUE;",
            "ALTER TABLE organizations ADD COLUMN IF NOT EXISTS campaigns_enabled BOOLEAN DEFAULT TRUE;",
            # appointments columns
            "ALTER TABLE appointments ADD COLUMN IF NOT EXISTS service_name VARCHAR(150);",
            "ALTER TABLE appointments ADD COLUMN IF NOT EXISTS staff_name VARCHAR(150);",
            "ALTER TABLE appointments ADD COLUMN IF NOT EXISTS customer_id INTEGER;",
            "ALTER TABLE appointments ADD COLUMN IF NOT EXISTS notes TEXT;",
            # services columns
            "ALTER TABLE services ADD COLUMN IF NOT EXISTS sector VARCHAR(50);",
            "UPDATE services SET sector = organizations.sector FROM organizations WHERE services.organization_id = organizations.id AND services.sector IS NULL;",
            # admins columns
            "ALTER TABLE admins ADD COLUMN IF NOT EXISTS name VARCHAR(150);",
            "ALTER TABLE admins ADD COLUMN IF NOT EXISTS email VARCHAR(120);",
            # users columns
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS name VARCHAR(150);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS email VARCHAR(120);",
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR(30);"
        ]

        for stmt in schema_statements:
            try:
                cursor.execute(stmt)
            except Exception as stmt_err:
                print(f"Notice during schema sync: {stmt_err}")

        cursor.close()
        conn.close()
        print("✓ All database schemas verified and synced successfully")

    except Exception as e:
        print(f"Warning: Could not sync schema in init_db: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("Database Initialization Script")
    print("=" * 60)
    
    create_database_if_not_exists()
    ensure_schema_synced()
    
    print("=" * 60)
    print("Database initialization completed successfully")
    print("=" * 60)

