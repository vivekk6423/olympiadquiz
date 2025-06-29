"""
Kids Quiz App - Streamlit Version
A comprehensive quiz application with user authentication and admin features
"""
import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our modules
from auth import require_auth, require_admin, show_login_form, logout_user, init_session_state, get_current_user
from quiz_utils import (
    show_subjects, show_topics, show_classes, show_levels, 
    show_quizzes, take_quiz, show_quiz_results
)
from admin_utils import show_admin_dashboard
from database import get_db_manager

# Configure the page
st.set_page_config(
    page_title="Kids Quiz App",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

def init_app():
    """Initialize the application"""
    # Initialize session state
    init_session_state()
    
    # Initialize database and create admin user
    db_manager = get_db_manager()
    if db_manager.engine:
        db_manager.create_admin_user()
    
    # Initialize page state
    if 'page' not in st.session_state:
        st.session_state.page = "subjects"

def show_sidebar():
    """Show sidebar navigation"""
    with st.sidebar:
        st.title("🎓 Kids Quiz App")
        
        if st.session_state.authenticated:
            user = get_current_user()
            if user:
                st.success(f"Welcome, {user.username}!")
                if user.is_admin:
                    st.info("🔧 Admin User")
            
            # Admin gets different navigation
            if require_admin():
                st.markdown("### Admin Navigation")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("� Admin", use_container_width=True):
                        st.session_state.page = "admin"
                        # Clear any student navigation state
                        clear_student_navigation_state()
                        st.rerun()
                
                with col2:
                    if st.button("👨‍🎓 Student View", use_container_width=True):
                        st.session_state.page = "subjects"
                        # Clear admin navigation state
                        clear_admin_navigation_state()
                        st.rerun()
            else:
                # Regular navigation for students
                st.markdown("### Navigation")
                
                if st.button("� Browse Subjects", use_container_width=True):
                    st.session_state.page = "subjects"
                    # Clear navigation path
                    if 'navigation_path' in st.session_state:
                        del st.session_state.navigation_path
                    st.rerun()
            
            # Logout button
            st.markdown("---")
            if st.button("🚪 Logout", use_container_width=True):
                logout_user()
                st.rerun()
        
        else:
            st.info("Please log in to access the quiz system.")

def clear_student_navigation_state():
    """Clear student navigation state variables"""
    keys_to_clear = [
        'navigation_path', 'current_subject_id', 'current_topic_id', 
        'current_class_id', 'current_level_id', 'current_quiz_id',
        'quiz_questions', 'current_question_index', 'user_answers',
        'quiz_start_time', 'quiz_results'
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

def clear_admin_navigation_state():
    """Clear admin navigation state variables"""
    keys_to_clear = [
        'admin_page', 'editing_quiz_id', 'deleting_quiz_id', 
        'show_delete_confirm'
    ]
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]

def main():
    """Main application function"""
    # Initialize the app
    init_app()
    
    # Check authentication
    if not require_auth():
        show_login_form()
        return
    
    # Show sidebar
    show_sidebar()
    
    # Main content area
    page = st.session_state.get('page', 'subjects')
    
    try:
        if page == "subjects":
            show_subjects()
        
        elif page == "topics":
            subject_id = st.session_state.get('current_subject_id')
            if subject_id:
                show_topics(subject_id)
            else:
                st.error("No subject selected")
                st.session_state.page = "subjects"
                st.rerun()
        
        elif page == "classes":
            topic_id = st.session_state.get('current_topic_id')
            if topic_id:
                show_classes(topic_id)
            else:
                st.error("No topic selected")
                st.session_state.page = "subjects"
                st.rerun()
        
        elif page == "levels":
            class_id = st.session_state.get('current_class_id')
            if class_id:
                show_levels(class_id)
            else:
                st.error("No class selected")
                st.session_state.page = "subjects"
                st.rerun()
        
        elif page == "quizzes":
            level_id = st.session_state.get('current_level_id')
            if level_id:
                show_quizzes(level_id)
            else:
                st.error("No level selected")
                st.session_state.page = "subjects"
                st.rerun()
        
        elif page == "take_quiz":
            quiz_id = st.session_state.get('current_quiz_id')
            if quiz_id:
                take_quiz(quiz_id)
            else:
                st.error("No quiz selected")
                st.session_state.page = "subjects"
                st.rerun()
        
        elif page == "quiz_results":
            quiz_id = st.session_state.get('current_quiz_id')
            if quiz_id:
                show_quiz_results(quiz_id)
            else:
                st.error("No quiz selected")
                st.session_state.page = "subjects"
                st.rerun()
        
        elif page == "admin":
            if require_admin():
                show_admin_dashboard()
            else:
                st.error("Access denied. Admin privileges required.")
                st.session_state.page = "subjects"
                st.rerun()
        
        else:
            st.error("Page not found")
            st.session_state.page = "subjects"
            st.rerun()
    
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.session_state.page = "subjects"
        if st.button("🏠 Return to Home"):
            st.rerun()

if __name__ == "__main__":
    main()
