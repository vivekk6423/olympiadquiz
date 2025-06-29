"""
Authentication utilities for Streamlit
"""
import streamlit as st
from database import get_db_manager

def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'is_admin' not in st.session_state:
        st.session_state.is_admin = False

def login_user(username, password):
    """Login user and set session state"""
    db_manager = get_db_manager()
    user = db_manager.authenticate_user(username, password)
    
    if user:
        st.session_state.authenticated = True
        st.session_state.user = user
        st.session_state.user_id = user.id
        st.session_state.username = user.username
        st.session_state.is_admin = user.is_admin
        return True, "Login successful!"
    else:
        return False, "Invalid username or password"

def register_user(username, password):
    """Register new user"""
    db_manager = get_db_manager()
    user, message = db_manager.create_user(username, password)
    
    if user:
        return True, message
    else:
        return False, message

def logout_user():
    """Logout user and clear session state"""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.is_admin = False

def require_auth():
    """Decorator-like function to require authentication"""
    init_session_state()
    return st.session_state.authenticated

def require_admin():
    """Check if user is admin"""
    return st.session_state.get('is_admin', False)

def get_current_user():
    """Get current user from session state"""
    return st.session_state.get('user')

def get_current_user_id():
    """Get current user ID from session state"""
    return st.session_state.get('user_id')

def show_login_form():
    """Show login/register form"""
    init_session_state()
    
    st.title("🎓 Kids Quiz App")
    st.markdown("Welcome to the Interactive Quiz Learning Platform!")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit_login = st.form_submit_button("Login")
            
            if submit_login:
                if username and password:
                    success, message = login_user(username, password)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please enter both username and password")
    
    with tab2:
        st.subheader("Register")
        with st.form("register_form"):
            new_username = st.text_input("Choose Username")
            new_password = st.text_input("Choose Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            submit_register = st.form_submit_button("Register")
            
            if submit_register:
                if new_username and new_password and confirm_password:
                    if new_password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(new_password) < 4:
                        st.error("Password must be at least 4 characters long")
                    else:
                        success, message = register_user(new_username, new_password)
                        if success:
                            st.success(message)
                            st.info("You can now login with your credentials")
                        else:
                            st.error(message)
                else:
                    st.error("Please fill in all fields")
    
    # Demo admin credentials info
    st.markdown("---")
    st.info("🔑 **Demo Admin Access**: username: `admin`, password: `admin123`")
    st.info("📝 **Demo Student**: Create your own account or use any username/password")
