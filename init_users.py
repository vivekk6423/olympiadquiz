#!/usr/bin/env python3
"""
Initialize the database with test users
"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def create_test_users():
    """Create test users including admin"""
    database_url = os.getenv('DATABASE_URL')
    
    try:
        # Create engine with schema search path
        engine = create_engine(
            database_url, 
            echo=False,
            connect_args={"options": "-csearch_path=olympiadquiz,public"}
        )
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()
        
        try:
            # Create admin user
            admin_user = session.query(User).filter_by(username='admin').first()
            if not admin_user:
                admin_user = User(username='admin', is_admin=True)
                admin_user.set_password('admin123')
                session.add(admin_user)
                print("✓ Created admin user (username: admin, password: admin123)")
            else:
                print("✓ Admin user already exists")
            
            # Create a test student user
            student_user = session.query(User).filter_by(username='student').first()
            if not student_user:
                student_user = User(username='student', is_admin=False)
                student_user.set_password('student123')
                session.add(student_user)
                print("✓ Created student user (username: student, password: student123)")
            else:
                print("✓ Student user already exists")
            
            # Create another test user
            test_user = session.query(User).filter_by(username='testuser').first()
            if not test_user:
                test_user = User(username='testuser', is_admin=False)
                test_user.set_password('test123')
                session.add(test_user)
                print("✓ Created test user (username: testuser, password: test123)")
            else:
                print("✓ Test user already exists")
            
            session.commit()
            print("\n✓ All test users created successfully!")
            
            # Verify users were created
            all_users = session.query(User).all()
            print(f"\nTotal users in database: {len(all_users)}")
            for user in all_users:
                print(f"  - {user.username} (Admin: {user.is_admin})")
            
            return True
            
        except Exception as e:
            session.rollback()
            print(f"✗ Error creating users: {e}")
            return False
        finally:
            session.close()
            
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    success = create_test_users()
    sys.exit(0 if success else 1)
