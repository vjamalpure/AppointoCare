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


if __name__ == "__main__":
    print("=" * 60)
    print("Database Initialization Script")
    print("=" * 60)
    
    create_database_if_not_exists()
    
    print("=" * 60)
    print("Database initialization completed successfully")
    print("=" * 60)
