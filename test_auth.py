#!/usr/bin/env python3
"""
Test authentication functionality
"""
import os
from database import DatabaseManager
from dotenv import load_dotenv

load_dotenv()

def test_authentication():
    """Test user authentication"""
    db_manager = DatabaseManager()
    
    # Test cases
    test_cases = [
        ("admin", "admin123", True, "Admin user"),
        ("student", "student123", False, "Student user"),
        ("testuser", "test123", False, "Test user"),
        ("admin", "wrongpassword", None, "Admin with wrong password"),
        ("nonexistent", "password", None, "Non-existent user"),
    ]
    
    print("Testing authentication...")
    for username, password, expected_result, description in test_cases:
        user = db_manager.authenticate_user(username, password)
        
        if expected_result is None:
            if user is None:
                print(f"✓ {description}: Correctly failed authentication")
            else:
                print(f"✗ {description}: Should have failed but got user {user.username}")
        else:
            if user and user.username == username and user.is_admin == expected_result:
                print(f"✓ {description}: Successfully authenticated (Admin: {user.is_admin})")
            else:
                print(f"✗ {description}: Authentication failed")
                
    print("\nAuthentication test completed!")

if __name__ == "__main__":
    test_authentication()
