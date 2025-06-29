#!/usr/bin/env python3
"""
Test hierarchical data loading to verify SQLAlchemy session handling
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db_manager

def test_hierarchy_loading():
    """Test loading subjects with full hierarchy"""
    print("Testing hierarchical data loading...")
    
    db_manager = get_db_manager()
    
    try:
        # Test regular subjects loading
        print("\n1. Testing regular subjects loading...")
        subjects = db_manager.get_subjects()
        print(f"Found {len(subjects)} subjects")
        
        for subject in subjects:
            print(f"  - {subject.name}")
            try:
                for topic in subject.topics:
                    print(f"    - {topic.name}")
                    # This should work now due to eager loading in get_subjects()
            except Exception as e:
                print(f"    ERROR accessing topics: {e}")
        
        # Test full hierarchy loading
        print("\n2. Testing full hierarchy loading...")
        subjects_full = db_manager.get_subjects_with_full_hierarchy()
        print(f"Found {len(subjects_full)} subjects with full hierarchy")
        
        for subject in subjects_full:
            print(f"  📚 {subject.name}")
            try:
                for topic in subject.topics:
                    print(f"    📖 {topic.name}")
                    for class_ in topic.classes:
                        print(f"      🎯 {class_.name}")
                        for level in class_.levels:
                            print(f"        ⭐ {level.name} ({len(level.quizzes)} quizzes)")
                            for quiz in level.quizzes:
                                print(f"          🧩 {quiz.title}")
            except Exception as e:
                print(f"    ERROR in hierarchy: {e}")
        
        print("\n✅ Hierarchy loading test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during hierarchy loading test: {e}")
        return False

if __name__ == "__main__":
    test_hierarchy_loading()
