#!/usr/bin/env python3
"""
Test database connection and check for existing users
"""
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_database_connection():
    """Test database connection and check for existing users"""
    database_url = os.getenv('DATABASE_URL')
    print(f"Using database URL: {database_url[:50]}...")
    
    try:
        # Create engine with schema search path
        engine = create_engine(
            database_url, 
            echo=True,
            connect_args={"options": "-csearch_path=olympiadquiz,public"}
        )
        
        # Test basic connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✓ Database connection successful!")
            
            # Check if olympiadquiz schema exists
            result = conn.execute(text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = 'olympiadquiz'"))
            schema_exists = result.fetchone()
            if schema_exists:
                print("✓ olympiadquiz schema exists")
            else:
                print("✗ olympiadquiz schema does not exist")
                return False
            
            # Check if user table exists
            result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'olympiadquiz' AND table_name = 'user'"))
            table_exists = result.fetchone()
            if table_exists:
                print("✓ user table exists in olympiadquiz schema")
            else:
                print("✗ user table does not exist in olympiadquiz schema")
                return False
            
            # Check existing users
            result = conn.execute(text("SELECT id, username, is_admin FROM olympiadquiz.user LIMIT 10"))
            users = result.fetchall()
            print(f"Found {len(users)} users:")
            for user in users:
                print(f"  - ID: {user[0]}, Username: {user[1]}, Admin: {user[2]}")
            
            # Check password hash for admin user (if exists)
            result = conn.execute(text("SELECT id, username, password_hash, is_admin FROM olympiadquiz.user WHERE username = 'admin' LIMIT 1"))
            admin_user = result.fetchone()
            if admin_user:
                print(f"✓ Admin user found: ID={admin_user[0]}, Username={admin_user[1]}, Has password hash: {bool(admin_user[2])}")
            else:
                print("✗ No admin user found")
            
            return True
            
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    success = test_database_connection()
    sys.exit(0 if success else 1)
