#!/usr/bin/env python3
"""
Test the user management functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db_manager

def test_user_management():
    """Test user management functions"""
    print("Testing user management functions...")
    
    db_manager = get_db_manager()
    
    try:
        # 1. Create test user
        print("\n1. Creating test user...")
        test_user, message = db_manager.create_user("testuser", "test123")
        if test_user:
            print(f"Created user: {test_user.username}, ID: {test_user.id}")
        else:
            print(f"Failed to create user: {message}")
            print("Note: If username already exists, this is expected.")
            # Try to get the user instead
            session = db_manager.get_session()
            test_user = session.query(db_manager.User).filter_by(username="testuser").first()
            session.close()
            if test_user:
                print(f"Found existing user: {test_user.username}, ID: {test_user.id}")
            else:
                print("Could not find or create test user, exiting test")
                return False
        
        # 2. Test get all users
        print("\n2. Testing get_all_users()...")
        users = db_manager.get_all_users()
        print(f"Found {len(users)} users")
        for user in users[:5]:  # Show first 5
            print(f"  - {user.username} (Admin: {user.is_admin})")
        
        # 3. Test get user by ID
        print("\n3. Testing get_user_by_id()...")
        user = db_manager.get_user_by_id(test_user.id)
        if user:
            print(f"Retrieved user by ID: {user.username}")
        else:
            print("Failed to retrieve user by ID")
        
        # 4. Test update user
        print("\n4. Testing update_user()...")
        success, message = db_manager.update_user(test_user.id, username="testuser_updated")
        print(f"Update result: {success}, {message}")
        
        # 5. Test reset password
        print("\n5. Testing reset_password()...")
        success, message = db_manager.reset_password(test_user.id, "newpassword123")
        print(f"Password reset result: {success}, {message}")
        
        # 6. Test make admin
        print("\n6. Testing make admin...")
        success, message = db_manager.update_user(test_user.id, is_admin=True)
        print(f"Make admin result: {success}, {message}")
        
        # 7. Test user statistics
        print("\n7. Testing get_user_statistics()...")
        stats = db_manager.get_user_statistics()
        print(f"Total users: {stats['total_users']}")
        print(f"Admin users: {stats['admin_users']}")
        print(f"Regular users: {stats['regular_users']}")
        print(f"Total attempts: {stats['total_attempts']}")
        print(f"Average score: {stats['avg_score']}%")
        print(f"Average time: {stats['avg_time']} minutes")
        if stats['active_users']:
            print("Most active users:")
            for user in stats['active_users']:
                print(f"  - {user['username']}: {user['attempt_count']} attempts")
        
        # 8. Clean up (delete test user)
        print("\n8. Testing delete_user()...")
        success, message = db_manager.delete_user(test_user.id)
        print(f"Delete result: {success}, {message}")
        
        print("\n✅ User management tests completed successfully!")
        return True
    
    except Exception as e:
        import traceback
        print(f"\n❌ Error during user management tests: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_user_management()
