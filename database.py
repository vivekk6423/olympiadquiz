"""
Database connection and utilities
"""
import os
from sqlalchemy import create_engine, text as sa_text
from sqlalchemy.orm import sessionmaker
from models import Base, User, Subject, Topic, Class, Level, Quiz, Question, Answer, QuizAttempt
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.init_database()
    
    def init_database(self):
        """Initialize database connection"""
        # Get database URL from environment or use default
        database_url = os.getenv('DATABASE_URL', 
                                'postgresql://postgres:your_password@db.drwpuytfkavmwlsihsrz.supabase.co:5432/postgres')
        
        try:
            # Add schema search path to use olympiadquiz schema
            self.engine = create_engine(
                database_url, 
                echo=False,
                connect_args={"options": "-csearch_path=olympiadquiz,public"}
            )
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            # Test the connection
            with self.engine.connect() as conn:
                result = conn.execute(sa_text("SELECT 1"))
                print("Database connected successfully!")
            
        except Exception as e:
            st.error(f"Database connection failed: {e}")
            print(f"Database connection failed: {e}")
    
    def get_session(self):
        """Get database session"""
        return self.SessionLocal()
    
    def create_admin_user(self, username="admin", password="admin123"):
        """Create admin user if not exists"""
        session = self.get_session()
        try:
            admin = session.query(User).filter_by(username=username, is_admin=True).first()
            if not admin:
                admin = User(username=username, is_admin=True)
                admin.set_password(password)
                session.add(admin)
                session.commit()
                print(f"Admin user created: {username}")
            if admin:
                _ = admin.username  # Ensure user data is loaded
            return admin
        except Exception as e:
            session.rollback()
            print(f"Error creating admin user: {e}")
        finally:
            session.close()
    
    def authenticate_user(self, username, password):
        """Authenticate user"""
        session = self.get_session()
        try:
            user = session.query(User).filter_by(username=username).first()
            if user and user.check_password(password):
                _ = user.username  # Ensure user data is loaded
                return user
            return None
        finally:
            session.close()
    
    def create_user(self, username, password):
        """Create new user"""
        session = self.get_session()
        try:
            # Check if user already exists
            existing_user = session.query(User).filter_by(username=username).first()
            if existing_user:
                return None, "Username already exists"
            
            user = User(username=username)
            user.set_password(password)
            session.add(user)
            session.commit()
            _ = user.username  # Ensure user data is loaded
            return user, "User created successfully"
        except Exception as e:
            session.rollback()
            return None, f"Error creating user: {e}"
        finally:
            session.close()
    
    def get_subjects(self):
        """Get all subjects with topics eager loaded"""
        session = self.get_session()
        try:
            from sqlalchemy.orm import joinedload
            subjects = session.query(Subject).options(
                joinedload(Subject.topics)
            ).all()
            # Make sure all lazy relationships are loaded within session
            for subject in subjects:
                for topic in subject.topics:
                    _ = topic.name  # Access to ensure loading
            return subjects
        finally:
            session.close()
    
    def get_subject_by_id(self, subject_id):
        """Get subject by ID with topics"""
        session = self.get_session()
        try:
            from sqlalchemy.orm import joinedload
            subject = session.query(Subject).options(
                joinedload(Subject.topics)
            ).filter_by(id=subject_id).first()
            if subject:
                for topic in subject.topics:
                    _ = topic.name  # Access to ensure loading
            return subject
        finally:
            session.close()
    
    def get_topic_by_id(self, topic_id):
        """Get topic by ID with classes"""
        session = self.get_session()
        try:
            from sqlalchemy.orm import joinedload
            topic = session.query(Topic).options(
                joinedload(Topic.classes),
                joinedload(Topic.subject)
            ).filter_by(id=topic_id).first()
            if topic:
                _ = topic.name
                for class_ in topic.classes:
                    _ = class_.name
                _ = topic.subject.name
            return topic
        finally:
            session.close()
    
    def get_class_by_id(self, class_id):
        """Get class by ID with levels"""
        session = self.get_session()
        try:
            from sqlalchemy.orm import joinedload
            class_ = session.query(Class).options(
                joinedload(Class.levels),
                joinedload(Class.topic).joinedload(Topic.subject)
            ).filter_by(id=class_id).first()
            if class_:
                _ = class_.name
                for level in class_.levels:
                    _ = level.name
                _ = class_.topic.name
                _ = class_.topic.subject.name
            return class_
        finally:
            session.close()
    
    def get_level_by_id(self, level_id):
        """Get level by ID with quizzes"""
        session = self.get_session()
        try:
            from sqlalchemy.orm import joinedload
            level = session.query(Level).options(
                joinedload(Level.quizzes),
                joinedload(Level.class_).joinedload(Class.topic).joinedload(Topic.subject)
            ).filter_by(id=level_id).first()
            if level:
                _ = level.name
                for quiz in level.quizzes:
                    _ = quiz.title
                _ = level.class_.name
                _ = level.class_.topic.name
                _ = level.class_.topic.subject.name
            return level
        finally:
            session.close()
    
    def get_quiz_by_id(self, quiz_id):
        """Get quiz by ID with questions and answers"""
        session = self.get_session()
        try:
            from sqlalchemy.orm import joinedload
            quiz = session.query(Quiz).options(
                joinedload(Quiz.questions).joinedload(Question.answers),
                joinedload(Quiz.level).joinedload(Level.class_).joinedload(Class.topic).joinedload(Topic.subject)
            ).filter_by(id=quiz_id).first()
            if quiz:
                _ = quiz.title
                _ = len(quiz.questions)
                for question in quiz.questions:
                    _ = question.question
                    _ = len(question.answers)
                    for answer in question.answers:
                        _ = answer.text
                
                if quiz.level:
                    _ = quiz.level.name
                    if quiz.level.class_:
                        _ = quiz.level.class_.name
                        if quiz.level.class_.topic:
                            _ = quiz.level.class_.topic.name
                            if quiz.level.class_.topic.subject:
                                _ = quiz.level.class_.topic.subject.name
            return quiz
        finally:
            session.close()
    
    def get_visible_quizzes_by_level(self, level_id, is_admin=False):
        """Get visible quizzes for a level"""
        session = self.get_session()
        try:
            from sqlalchemy.orm import joinedload
            query = session.query(Quiz).options(
                joinedload(Quiz.questions).joinedload(Question.answers)
            ).filter_by(level_id=level_id)
            if not is_admin:
                query = query.filter_by(is_visible=True)
            quizzes = query.all()
            
            # Access all relationships to ensure they're loaded
            for quiz in quizzes:
                _ = quiz.title  # Basic access
                _ = len(quiz.questions)  # This forces loading
                for question in quiz.questions:
                    _ = question.question  # Basic access
                    _ = len(question.answers)  # This forces loading
                    for answer in question.answers:
                        _ = answer.text  # Basic access
            
            return quizzes
        finally:
            session.close()
    
    def submit_quiz_attempt(self, user_id, quiz_id, score, total_questions, time_taken, results):
        """Submit quiz attempt"""
        session = self.get_session()
        try:
            attempt = QuizAttempt(
                user_id=user_id,
                quiz_id=quiz_id,
                score=score,
                total_questions=total_questions,
                time_taken=time_taken
            )
            attempt.set_results(results)
            session.add(attempt)
            session.commit()
            return attempt
        except Exception as e:
            session.rollback()
            print(f"Error submitting quiz attempt: {e}")
            return None
        finally:
            session.close()
    
    def get_user_quiz_attempts(self, user_id, quiz_id):
        """Get user's quiz attempts"""
        session = self.get_session()
        try:
            from sqlalchemy.orm import joinedload
            attempts = session.query(QuizAttempt).options(
                joinedload(QuizAttempt.user),
                joinedload(QuizAttempt.quiz)
            ).filter_by(
                user_id=user_id, 
                quiz_id=quiz_id
            ).order_by(QuizAttempt.date.desc()).all()
            
            # Access relationships to ensure they're loaded
            for attempt in attempts:
                _ = attempt.user.username
                _ = attempt.quiz.title
            
            return attempts
        finally:
            session.close()
    
    def get_all_quiz_attempts(self):
        """Get all quiz attempts (admin only)"""
        session = self.get_session()
        try:
            from sqlalchemy.orm import joinedload
            attempts = session.query(QuizAttempt).options(
                joinedload(QuizAttempt.user),
                joinedload(QuizAttempt.quiz)
            ).order_by(QuizAttempt.date.desc()).all()
            
            # Access relationships to ensure they're loaded
            for attempt in attempts:
                _ = attempt.user.username
                _ = attempt.quiz.title
            
            return attempts
        finally:
            session.close()
    
    def get_all_quizzes(self):
        """Get all quizzes"""
        session = self.get_session()
        try:
            from sqlalchemy.orm import joinedload
            quizzes = session.query(Quiz).options(
                joinedload(Quiz.questions).joinedload(Question.answers),
                joinedload(Quiz.level).joinedload(Level.class_).joinedload(Class.topic).joinedload(Topic.subject)
            ).all()
            
            # Access all relationships to ensure they're loaded
            for quiz in quizzes:
                _ = quiz.title  # Basic access
                _ = len(quiz.questions)  # This forces loading
                for question in quiz.questions:
                    _ = question.question  # Basic access
                    _ = len(question.answers)  # This forces loading
                    for answer in question.answers:
                        _ = answer.text  # Basic access
                
                # Access level hierarchy if it exists
                if quiz.level:
                    _ = quiz.level.name
                    if quiz.level.class_:
                        _ = quiz.level.class_.name
                        if quiz.level.class_.topic:
                            _ = quiz.level.class_.topic.name
                            if quiz.level.class_.topic.subject:
                                _ = quiz.level.class_.topic.subject.name
            
            return quizzes
        finally:
            session.close()
    
    def toggle_quiz_visibility(self, quiz_id):
        """Toggle quiz visibility"""
        session = self.get_session()
        try:
            quiz = session.query(Quiz).filter_by(id=quiz_id).first()
            if quiz:
                quiz.is_visible = not quiz.is_visible
                session.commit()
                return quiz.is_visible
            return None
        except Exception as e:
            session.rollback()
            print(f"Error toggling quiz visibility: {e}")
            return None
        finally:
            session.close()
    
    def get_all_users(self):
        """Get all users with their statistics"""
        from sqlalchemy.orm import joinedload
        from sqlalchemy import func
        
        session = self.get_session()
        try:
            # Get all users with eager loading of quiz attempts
            users = session.query(User).options(
                joinedload(User.quiz_attempts).joinedload(QuizAttempt.quiz)
            ).all()
            
            # Access all relationships to ensure they're loaded
            for user in users:
                _ = user.username  # Basic access
                _ = len(user.quiz_attempts)  # Force loading
                for attempt in user.quiz_attempts:
                    _ = attempt.quiz.title  # Force loading relations
            
            return users
        finally:
            session.close()
    
    def get_user_by_id(self, user_id):
        """Get user by ID with quiz attempts eager loaded"""
        from sqlalchemy.orm import joinedload
        
        session = self.get_session()
        try:
            user = session.query(User).options(
                joinedload(User.quiz_attempts).joinedload(QuizAttempt.quiz)
            ).filter_by(id=user_id).first()
            
            if user:
                _ = user.username  # Basic access
                _ = len(user.quiz_attempts)  # Force loading
                for attempt in user.quiz_attempts:
                    _ = attempt.quiz.title  # Force loading relations
            
            return user
        finally:
            session.close()
    
    def update_user(self, user_id, username=None, is_admin=None):
        """Update user properties"""
        session = self.get_session()
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                return False, "User not found"
            
            if username is not None and username != user.username:
                # Check if username is already taken
                existing = session.query(User).filter_by(username=username).first()
                if existing and existing.id != user_id:
                    return False, "Username already exists"
                user.username = username
            
            if is_admin is not None:
                user.is_admin = is_admin
            
            session.commit()
            return True, "User updated successfully"
        except Exception as e:
            session.rollback()
            return False, f"Error updating user: {e}"
        finally:
            session.close()
    
    def reset_password(self, user_id, new_password):
        """Reset user password"""
        session = self.get_session()
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                return False, "User not found"
            
            user.set_password(new_password)
            session.commit()
            return True, "Password reset successfully"
        except Exception as e:
            session.rollback()
            return False, f"Error resetting password: {e}"
        finally:
            session.close()
    
    def delete_user(self, user_id):
        """Delete user account"""
        session = self.get_session()
        try:
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                return False, "User not found"
            
            # Check if it's the last admin
            if user.is_admin:
                admin_count = session.query(User).filter_by(is_admin=True).count()
                if admin_count <= 1:
                    return False, "Cannot delete the last admin user"
            
            session.delete(user)
            session.commit()
            return True, "User deleted successfully"
        except Exception as e:
            session.rollback()
            return False, f"Error deleting user: {e}"
        finally:
            session.close()
    
    def get_user_statistics(self):
        """Get aggregated user statistics"""
        from sqlalchemy import func
        
        session = self.get_session()
        try:
            # Count users
            total_users = session.query(func.count(User.id)).scalar()
            admin_users = session.query(func.count(User.id)).filter(User.is_admin == True).scalar()
            regular_users = total_users - admin_users
            
            # Quiz attempt statistics
            total_attempts = session.query(func.count(QuizAttempt.id)).scalar() or 0
            avg_score = session.query(func.avg(QuizAttempt.score * 100.0 / QuizAttempt.total_questions)).scalar() or 0
            avg_time = session.query(func.avg(QuizAttempt.time_taken)).scalar() or 0
            
            # Most active users (top 5)
            active_users_query = session.query(
                User.id, User.username, 
                func.count(QuizAttempt.id).label('attempt_count')
            ).outerjoin(QuizAttempt).group_by(User.id).order_by(func.count(QuizAttempt.id).desc()).limit(5)
            
            active_users = []
            for user_id, username, attempt_count in active_users_query:
                active_users.append({
                    'id': user_id,
                    'username': username,
                    'attempt_count': attempt_count
                })
            
            return {
                'total_users': total_users,
                'admin_users': admin_users,
                'regular_users': regular_users,
                'total_attempts': total_attempts,
                'avg_score': round(avg_score, 1) if avg_score else 0,
                'avg_time': round(avg_time / 60, 1) if avg_time else 0,  # Convert to minutes
                'active_users': active_users
            }
        finally:
            session.close()
    
    def get_subjects_with_full_hierarchy(self):
        """Get all subjects with complete hierarchy (topics -> classes -> levels -> quizzes) eager loaded"""
        session = self.get_session()
        try:
            from sqlalchemy.orm import joinedload
            subjects = session.query(Subject).options(
                joinedload(Subject.topics).joinedload(Topic.classes).joinedload(Class.levels).joinedload(Level.quizzes)
            ).all()
            
            # Force loading of all nested relationships
            for subject in subjects:
                _ = subject.name
                for topic in subject.topics:
                    _ = topic.name
                    for class_ in topic.classes:
                        _ = class_.name
                        for level in class_.levels:
                            _ = level.name
                            for quiz in level.quizzes:
                                _ = quiz.title
            
            return subjects
        finally:
            session.close()

# Global database manager instance
@st.cache_resource
def get_db_manager():
    """Get database manager instance"""
    return DatabaseManager()
