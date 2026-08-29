"""
Local database initialization script for development.
Use this when running the project without Docker.

Usage:
    python init_db_local.py
"""

import os
import sys
import subprocess
from urllib.parse import urlparse
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql, OperationalError

# Load environment variables from .env file
load_dotenv()


def parse_database_url():
    """Parse DATABASE_URL environment variable."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL environment variable is not set")
        print("Please set it in your .env file or as an environment variable")
        print("\nExample:")
        print("  DATABASE_URL=postgresql://postgres:password@localhost:5432/appointocare")
        sys.exit(1)

    parsed = urlparse(database_url)
    
    return {
        "host": parsed.hostname or "localhost",
        "port": parsed.port or 5432,
        "name": parsed.path.lstrip("/"),
        "user": parsed.username or "postgres",
        "password": parsed.password or "",
    }


def create_database_if_not_exists():
    """Check if database exists and create it if needed."""
    config = parse_database_url()
    
    if not config["name"]:
        print("ERROR: Database name not specified in DATABASE_URL")
        sys.exit(1)
    
    print(f"\n📦 Checking database: {config['name']} on {config['host']}:{config['port']}")
    
    try:
        # Connect to default 'postgres' database
        conn = psycopg2.connect(
            host=config["host"],
            port=config["port"],
            user=config["user"],
            password=config["password"],
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(
            sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s"),
            [config["name"]]
        )
        
        if cursor.fetchone():
            print(f"   ✓ Database '{config['name']}' exists")
        else:
            print(f"   Creating database '{config['name']}'...")
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(config["name"])
            ))
            print(f"   ✓ Database '{config['name']}' created")
        
        cursor.close()
        conn.close()
        return True
        
    except (OperationalError, Exception) as error:
        print(f"   ✗ Database error: {error}")
        print("\n   Make sure PostgreSQL is running:")
        print("   - Windows: psql -U postgres -c 'SELECT version();'")
        print("   - macOS/Linux: psql postgres -c 'SELECT version();'")
        return False


def run_migrations():
    """Run Flask database migrations."""
    print("\n📚 Running database migrations...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "flask", "--app", "run.py", "db", "upgrade"],
            check=True,
            capture_output=True,
            text=True
        )
        print("   ✓ Migrations completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ✗ Migration failed: {e.stderr}")
        return False


def seed_demo_data():
    """Seed demo data into the database."""
    seed = os.getenv("SEED_DEMO_DATA", "true").lower() == "true"
    
    if not seed:
        print("\n⏭️  Demo data seeding disabled (SEED_DEMO_DATA=false)")
        return True
    
    print("\n👥 Seeding demo data...")
    try:
        result = subprocess.run(
            [sys.executable, "create_users.py"],
            check=True,
            capture_output=True,
            text=True
        )
        print("   ✓ Demo data seeded")
        print("\n   Demo Credentials:")
        print("   ├─ Super Admin: superadmin / Admin@12345")
        print("   ├─ Org Admin:   org1 / Org@12345 (Org: ORG1)")
        print("   └─ Staff:       staff1 / Staff@12345 (Org: ORG1)")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ✗ Seeding failed: {e.stderr}")
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("AppointoCare - Local Database Initialization")
    print("="*60)
    
    success = True
    
    # Step 1: Create database if needed
    if not create_database_if_not_exists():
        success = False
    
    # Step 2: Run migrations
    if success and not run_migrations():
        success = False
    
    # Step 3: Seed demo data (optional)
    if success and not seed_demo_data():
        success = False
    
    print("\n" + "="*60)
    if success:
        print("✓ Database initialization completed successfully!")
        print("\nYou can now:")
        print("  1. Start backend: python run.py")
        print("  2. In another terminal, start Celery: celery -A celery_worker.celery worker --loglevel=info")
        print("  3. In another terminal, start frontend: cd ../appointocare-frontend && npm start")
    else:
        print("✗ Database initialization failed!")
        sys.exit(1)
    print("="*60 + "\n")
