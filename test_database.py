#!/usr/bin/env python3
"""
Simple test to check database and relationships
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from database import DatabaseManager
    print("✓ Database module imported successfully")
    
    db = DatabaseManager()
    print("✓ DatabaseManager created successfully")
    
    # Test basic connection
    print("Testing basic queries...")
    
    # Get subjects
    subjects = db.get_subjects()
    print(f"✓ Found {len(subjects)} subjects")
    
    # Test a specific method that was causing issues
    quizzes = db.get_all_quizzes()
    print(f"✓ Found {len(quizzes)} quizzes")
    
    if len(quizzes) > 0:
        quiz = quizzes[0]
        print(f"✓ First quiz: {quiz.title}")
        print(f"✓ Questions in first quiz: {len(quiz.questions)}")
        
        if len(quiz.questions) > 0:
            question = quiz.questions[0]
            print(f"✓ First question: {question.question[:50]}...")
            print(f"✓ Answers for first question: {len(question.answers)}")
    
    print("✓ All tests passed!")
    
except Exception as e:
    import traceback
    print(f"✗ Error: {e}")
    traceback.print_exc()
