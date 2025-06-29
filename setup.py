#!/usr/bin/env python3
"""
Setup script for Kids Quiz App
Run this script to initialize the database and load sample data
"""

import os
import sys
import json
from dotenv import load_dotenv

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from database import get_db_manager
from admin_utils import process_quiz_upload

def setup_database():
    """Setup database and create admin user"""
    print("🔧 Setting up database...")
    
    try:
        db_manager = get_db_manager()
        
        if not db_manager.engine:
            print("❌ Database connection failed!")
            print("Please check your DATABASE_URL in .env file")
            return False
        
        print("✅ Database connected successfully!")
        
        # Create admin user
        admin_username = os.getenv('ADMIN_USERNAME', 'admin')
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
        
        admin = db_manager.create_admin_user(admin_username, admin_password)
        if admin:
            print(f"✅ Admin user created: {admin_username}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False

def load_sample_data():
    """Load sample quiz data"""
    print("📤 Loading sample quiz data...")
    
    try:
        # Check if sample data file exists
        sample_file = "sample_quiz_data.json"
        if not os.path.exists(sample_file):
            print(f"❌ Sample data file not found: {sample_file}")
            return False
        
        # Load and process sample data
        with open(sample_file, 'r') as f:
            quiz_data = json.load(f)
        
        success = process_quiz_upload(quiz_data)
        if success:
            print("✅ Sample quiz data loaded successfully!")
            return True
        else:
            print("❌ Failed to load sample quiz data")
            return False
        
    except Exception as e:
        print(f"❌ Error loading sample data: {e}")
        return False

def main():
    """Main setup function"""
    print("🎓 Kids Quiz App Setup")
    print("=" * 40)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please create .env file from .env.example and configure your database settings")
        return
    
    # Setup database
    if not setup_database():
        print("❌ Setup failed! Please check your database configuration.")
        return
    
    # Ask user if they want to load sample data
    load_sample = input("\n📊 Do you want to load sample quiz data? (y/n): ").lower().strip()
    
    if load_sample in ['y', 'yes']:
        load_sample_data()
    
    print("\n🎉 Setup completed!")
    print("\nNext steps:")
    print("1. Run: streamlit run app.py")
    print("2. Login with admin credentials:")
    print(f"   Username: {os.getenv('ADMIN_USERNAME', 'admin')}")
    print(f"   Password: {os.getenv('ADMIN_PASSWORD', 'admin123')}")
    print("3. Create student accounts or upload more quiz data")
    print("\n📖 Visit http://localhost:8501 to access the app")

if __name__ == "__main__":
    main()
