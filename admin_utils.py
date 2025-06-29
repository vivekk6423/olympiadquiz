"""
Admin utilities and functions
"""
import streamlit as st
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from models import Quiz, Question, Answer, Subject, Topic, Class, Level, User, QuizAttempt
from database import get_db_manager

def show_admin_dashboard():
    """Show admin dashboard"""
    st.title("🔧 Admin Dashboard")
    
    # Ensure we're in admin mode - clear any student navigation state
    if st.session_state.get('page') != 'admin':
        st.session_state.page = 'admin'
    
    # Clear student navigation state to prevent conflicts
    student_nav_keys = ['current_subject_id', 'current_topic_id', 'current_class_id', 
                       'current_level_id', 'current_quiz_id', 'navigation_path']
    for key in student_nav_keys:
        if key in st.session_state:
            del st.session_state[key]
    
    # Check if we're in quiz editing mode
    if st.session_state.get('admin_page') == 'edit_quiz':
        show_quiz_editor()
        return
    
    # Quick stats
    db_manager = get_db_manager()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        subjects = db_manager.get_subjects()
        st.metric("📚 Subjects", len(subjects))
    
    with col2:
        quizzes = db_manager.get_all_quizzes()
        st.metric("🧩 Quizzes", len(quizzes))
    
    with col3:
        attempts = db_manager.get_all_quiz_attempts()
        st.metric("📊 Total Attempts", len(attempts))
    
    with col4:
        # Count total questions
        total_questions = sum(len(quiz.questions) for quiz in quizzes)
        st.metric("❓ Total Questions", total_questions)
    
    st.markdown("---")
    
    # Handle delete confirmation
    if st.session_state.get('show_delete_confirm'):
        show_delete_confirmation(db_manager)
    
    # Admin menu
    menu_option = st.selectbox(
        "Choose Admin Function:",
        ["Dashboard Overview", "Manage Quizzes", "View All Attempts", "Upload Quiz Data", "User Management"]
    )
    
    if menu_option == "Dashboard Overview":
        show_dashboard_overview()
    elif menu_option == "Manage Quizzes":
        show_quiz_management()
    elif menu_option == "View All Attempts":
        show_all_attempts()
    elif menu_option == "Upload Quiz Data":
        show_quiz_upload()
    elif menu_option == "User Management":
        show_user_management()

def show_dashboard_overview():
    """Show dashboard overview"""
    st.subheader("📈 System Overview")
    
    db_manager = get_db_manager()
    subjects = db_manager.get_subjects_with_full_hierarchy()
    
    if not subjects:
        st.warning("No data found in the system. Use the 'Upload Quiz Data' feature to add content.")
        return
    
    # Subject hierarchy
    for subject in subjects:
        with st.expander(f"📚 {subject.name}"):
            for topic in subject.topics:
                st.write(f"  📖 {topic.name}")
                for class_ in topic.classes:
                    st.write(f"    🎯 {class_.name}")
                    for level in class_.levels:
                        quiz_count = len(level.quizzes)
                        st.write(f"      ⭐ {level.name} ({quiz_count} quizzes)")

def show_quiz_management():
    """Show quiz management interface"""
    st.subheader("🧩 Quiz Management")
    
    db_manager = get_db_manager()
    
    # Add tabs for different views
    tab1, tab2 = st.tabs(["📊 Tree View", "📋 List View"])
    
    with tab1:
        show_quiz_tree_view(db_manager)
    
    with tab2:
        show_quiz_list_view(db_manager)

def show_quiz_tree_view(db_manager):
    """Show hierarchical tree view of quizzes for admin management"""
    subjects = db_manager.get_subjects_with_full_hierarchy()
    
    if not subjects:
        st.warning("No quizzes found in the system.")
        return
    
    # Subject hierarchy with admin controls
    for subject in subjects:
        with st.expander(f"📚 {subject.name} ({count_subject_quizzes(subject)} quizzes)", expanded=False):
            for topic in subject.topics:
                st.write(f"📖 **{topic.name}** ({count_topic_quizzes(topic)} quizzes)")
                
                for class_ in topic.classes:
                    st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;🎯 **{class_.name}** ({count_class_quizzes(class_)} quizzes)")
                    
                    for level in class_.levels:
                        quiz_count = len(level.quizzes)
                        st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;⭐ **{level.name}** ({quiz_count} quizzes)")
                        
                        if quiz_count > 0:
                            # Show quizzes in this level with admin actions
                            for quiz in level.quizzes:
                                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                                
                                with col1:
                                    visibility_icon = "👁️" if quiz.is_visible else "🙈"
                                    st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{visibility_icon} {quiz.title}")
                                
                                with col2:
                                    if st.button("✏️", key=f"edit_{quiz.id}", help="Edit Quiz"):
                                        st.session_state.editing_quiz_id = quiz.id
                                        st.session_state.admin_page = "edit_quiz"
                                        st.rerun()
                                
                                with col3:
                                    if st.button("👁️" if not quiz.is_visible else "🙈", 
                                               key=f"toggle_{quiz.id}",
                                               help="Toggle Visibility"):
                                        new_visibility = db_manager.toggle_quiz_visibility(quiz.id)
                                        if new_visibility is not None:
                                            st.success(f"Quiz {'shown' if new_visibility else 'hidden'}")
                                            st.rerun()
                                
                                with col4:
                                    if st.button("🗑️", key=f"delete_{quiz.id}", help="Delete Quiz"):
                                        st.session_state.deleting_quiz_id = quiz.id
                                        st.session_state.show_delete_confirm = True

def show_quiz_list_view(db_manager):
    """Show flat list view of all quizzes"""
    quizzes = db_manager.get_all_quizzes()
    
    if not quizzes:
        st.warning("No quizzes found in the system.")
        return
    
    # Quiz filters
    col1, col2 = st.columns(2)
    with col1:
        show_hidden = st.checkbox("Show Hidden Quizzes")
    with col2:
        search_term = st.text_input("Search Quizzes", placeholder="Search by title...")
    
    # Filter quizzes
    filtered_quizzes = quizzes
    if not show_hidden:
        filtered_quizzes = [q for q in filtered_quizzes if q.is_visible]
    
    if search_term:
        filtered_quizzes = [q for q in filtered_quizzes if search_term.lower() in q.title.lower()]
    
    # Display quizzes in table format
    if filtered_quizzes:
        quiz_data = []
        for quiz in filtered_quizzes:
            level_name = quiz.level.name if quiz.level else "No Level"
            class_name = quiz.level.class_.name if quiz.level and quiz.level.class_ else "No Class"
            topic_name = quiz.level.class_.topic.name if quiz.level and quiz.level.class_ and quiz.level.class_.topic else "No Topic"
            subject_name = quiz.level.class_.topic.subject.name if quiz.level and quiz.level.class_ and quiz.level.class_.topic and quiz.level.class_.topic.subject else "No Subject"
            
            quiz_data.append({
                "Title": quiz.title,
                "Subject": subject_name,
                "Topic": topic_name,
                "Class": class_name,
                "Level": level_name,
                "Questions": len(quiz.questions),
                "Time (min)": quiz.time_limit,
                "Visible": "✅" if quiz.is_visible else "❌",
                "Actions": quiz.id
            })
        
        # Display as dataframe for better formatting
        df = pd.DataFrame(quiz_data)
        
        # Display table
        for idx, row in df.iterrows():
            quiz_id = row["Actions"]
            quiz = next(q for q in filtered_quizzes if q.id == quiz_id)
            
            col1, col2, col3, col4 = st.columns([4, 1, 1, 1])
            
            with col1:
                st.write(f"**{row['Title']}**")
                st.write(f"📍 {row['Subject']} → {row['Topic']} → {row['Class']} → {row['Level']}")
                st.write(f"⏱️ {row['Time (min)']} min | ❓ {row['Questions']} questions | {row['Visible']}")
            
            with col2:
                if st.button("✏️ Edit", key=f"edit_list_{quiz_id}"):
                    st.session_state.editing_quiz_id = quiz_id
                    st.session_state.admin_page = "edit_quiz"
                    st.rerun()
            
            with col3:
                if st.button("👁️ Toggle", key=f"toggle_list_{quiz_id}"):
                    new_visibility = db_manager.toggle_quiz_visibility(quiz_id)
                    if new_visibility is not None:
                        st.success(f"Quiz {'shown' if new_visibility else 'hidden'}")
                        st.rerun()
            
            with col4:
                if st.button("�️ Delete", key=f"delete_list_{quiz_id}"):
                    st.session_state.deleting_quiz_id = quiz_id
                    st.session_state.show_delete_confirm = True
            
            st.markdown("---")

def count_subject_quizzes(subject):
    """Count total quizzes in a subject"""
    total = 0
    for topic in subject.topics:
        total += count_topic_quizzes(topic)
    return total

def count_topic_quizzes(topic):
    """Count total quizzes in a topic"""
    total = 0
    for class_ in topic.classes:
        total += count_class_quizzes(class_)
    return total

def count_class_quizzes(class_):
    """Count total quizzes in a class"""
    total = 0
    for level in class_.levels:
        total += len(level.quizzes)
    return total

def show_quiz_details(quiz):
    """Show detailed quiz information"""
    st.subheader(f"📝 Quiz Details: {quiz.title}")
    
    # Basic info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Questions", len(quiz.questions))
    with col2:
        st.metric("Time Limit", f"{quiz.time_limit} min")
    with col3:
        visibility = "Visible" if quiz.is_visible else "Hidden"
        st.metric("Status", visibility)
    
    # Questions
    st.subheader("❓ Questions")
    for idx, question in enumerate(quiz.questions):
        with st.expander(f"Question {idx + 1}"):
            st.write("**Question:**", question.question)
            
            answers = sorted(question.answers, key=lambda x: x.id)
            st.write("**Options:**")
            for i, answer in enumerate(answers):
                icon = "✅" if answer.is_correct else "❌"
                st.write(f"{i + 1}. {icon} {answer.text}")
            
            if question.explanation:
                st.write("**Explanation:**", question.explanation)

def show_all_attempts():
    """Show all quiz attempts"""
    st.subheader("📊 All Quiz Attempts")
    
    db_manager = get_db_manager()
    attempts = db_manager.get_all_quiz_attempts()
    
    if not attempts:
        st.warning("No quiz attempts found.")
        return
    
    # Convert to display format
    attempt_data = []
    for attempt in attempts:
        percentage = (attempt.score / attempt.total_questions) * 100
        attempt_data.append({
            "User": attempt.user.username,
            "Quiz": attempt.quiz.title,
            "Score": f"{attempt.score}/{attempt.total_questions}",
            "Percentage": f"{percentage:.1f}%",
            "Time Taken": f"{attempt.time_taken // 60}m {attempt.time_taken % 60}s",
            "Date": attempt.date.strftime("%Y-%m-%d %H:%M"),
            "Admin": "Yes" if attempt.user.is_admin else "No"
        })
    
    # Display as dataframe
    if attempt_data:
        st.dataframe(attempt_data, use_container_width=True)
        
        # Download option
        csv = '\n'.join([','.join(row.values()) for row in attempt_data])
        st.download_button(
            "📥 Download CSV",
            csv,
            "quiz_attempts.csv",
            "text/csv"
        )

def show_quiz_upload():
    """Show quiz upload interface"""
    st.subheader("📤 Upload Quiz Data")
    
    st.markdown("""
    Upload quiz data in JSON format. The JSON should follow this structure:
    """)
    
    # Example JSON structure
    example_json = {
        "subject": {
            "name": "Mathematics",
            "topics": [
                {
                    "name": "Algebra",
                    "classes": [
                        {
                            "name": "Class 8",
                            "levels": [
                                {
                                    "name": "Basic Algebra",
                                    "quizzes": [
                                        {
                                            "title": "Linear Equations",
                                            "description": "Basic linear equations",
                                            "time_limit": 30,
                                            "questions": [
                                                {
                                                    "question": "What is 2x + 3 = 7?",
                                                    "options": ["x = 1", "x = 2", "x = 3", "x = 4"],
                                                    "answer": 1,
                                                    "explanation": "2x = 7 - 3 = 4, so x = 2"
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                }
            ]
        }
    }
    
    st.code(json.dumps(example_json, indent=2), language="json")
    
    # File upload
    uploaded_file = st.file_uploader("Choose JSON file", type=['json'])
    
    if uploaded_file is not None:
        try:
            quiz_data = json.load(uploaded_file)
            
            if st.button("📤 Upload Quiz Data", type="primary"):
                success = process_quiz_upload(quiz_data)
                if success:
                    st.success("✅ Quiz data uploaded successfully!")
                else:
                    st.error("❌ Failed to upload quiz data")
        
        except json.JSONDecodeError:
            st.error("❌ Invalid JSON file")
        except Exception as e:
            st.error(f"❌ Error reading file: {e}")

def process_quiz_upload(quiz_data):
    """Process uploaded quiz data"""
    try:
        db_manager = get_db_manager()
        session = db_manager.get_session()
        
        # Get or create subject
        subject_data = quiz_data['subject']
        subject = session.query(Subject).filter_by(name=subject_data['name']).first()
        if not subject:
            subject = Subject(name=subject_data['name'])
            session.add(subject)
            session.flush()
        
        # Process topics
        for topic_data in subject_data.get('topics', []):
            topic = session.query(Topic).filter_by(name=topic_data['name'], subject_id=subject.id).first()
            if not topic:
                topic = Topic(name=topic_data['name'], subject_id=subject.id)
                session.add(topic)
                session.flush()
            
            # Process classes
            for class_data in topic_data.get('classes', []):
                class_ = session.query(Class).filter_by(name=class_data['name'], topic_id=topic.id).first()
                if not class_:
                    class_ = Class(name=class_data['name'], topic_id=topic.id)
                    session.add(class_)
                    session.flush()
                
                # Process levels
                for level_data in class_data.get('levels', []):
                    level = session.query(Level).filter_by(name=level_data['name'], class_id=class_.id).first()
                    if not level:
                        level = Level(name=level_data['name'], class_id=class_.id)
                        session.add(level)
                        session.flush()
                    
                    # Process quizzes
                    for quiz_data in level_data.get('quizzes', []):
                        # Check if quiz exists
                        existing_quiz = session.query(Quiz).filter_by(title=quiz_data['title'], level_id=level.id).first()
                        
                        if existing_quiz:
                            # Update existing quiz
                            existing_quiz.description = quiz_data.get('description', '')
                            existing_quiz.time_limit = quiz_data.get('time_limit', 30)
                            
                            # Delete existing questions
                            for question in existing_quiz.questions:
                                session.delete(question)
                            session.flush()
                            quiz = existing_quiz
                        else:
                            # Create new quiz
                            quiz = Quiz(
                                title=quiz_data['title'],
                                description=quiz_data.get('description', ''),
                                time_limit=quiz_data.get('time_limit', 30),
                                level_id=level.id
                            )
                            session.add(quiz)
                            session.flush()
                        
                        # Process questions
                        for question_data in quiz_data.get('questions', []):
                            question = Question(
                                question=question_data['question'],
                                quiz_id=quiz.id,
                                explanation=question_data.get('explanation', '')
                            )
                            session.add(question)
                            session.flush()
                            
                            # Process answers
                            for i, option in enumerate(question_data['options']):
                                answer = Answer(
                                    text=option,
                                    is_correct=(i == question_data['answer']),
                                    question_id=question.id
                                )
                                session.add(answer)
        
        session.commit()
        return True
        
    except Exception as e:
        session.rollback()
        st.error(f"Error processing quiz data: {e}")
        return False
    finally:
        session.close()

def show_user_management():
    """Show user management interface"""
    st.subheader("👥 User Management")
    
    db_manager = get_db_manager()
    
    # User statistics dashboard
    stats = db_manager.get_user_statistics()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Users", stats['total_users'])
    with col2:
        st.metric("Admin Users", stats['admin_users'])
    with col3:
        st.metric("Regular Users", stats['regular_users'])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Quiz Attempts", stats['total_attempts'])
    with col2:
        st.metric("Avg. Score", f"{stats['avg_score']}%")
    with col3:
        st.metric("Avg. Time Spent", f"{stats['avg_time']} min")
    
    # Tabs for different user management features
    tab1, tab2, tab3, tab4 = st.tabs(["👥 User List", "➕ Add User", "🔐 Reset Password", "📊 User Statistics"])
    
    with tab1:
        show_user_list(db_manager)
    
    with tab2:
        show_add_user_form(db_manager)
    
    with tab3:
        show_password_reset_form(db_manager)
    
    with tab4:
        show_user_statistics(db_manager, stats)

def show_quiz_editor():
    """Show quiz editing interface"""
    if 'editing_quiz_id' not in st.session_state:
        st.error("No quiz selected for editing.")
        return
    
    db_manager = get_db_manager()
    quiz = db_manager.get_quiz_by_id(st.session_state.editing_quiz_id)
    
    if not quiz:
        st.error("Quiz not found.")
        return
    
    st.subheader(f"✏️ Editing Quiz: {quiz.title}")
    
    # Back button
    if st.button("← Back to Quiz Management"):
        if 'editing_quiz_id' in st.session_state:
            del st.session_state.editing_quiz_id
        if 'admin_page' in st.session_state:
            del st.session_state.admin_page
        st.rerun()
    
    # Quiz metadata editing
    st.write("### Quiz Information")
    
    with st.form("edit_quiz_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_title = st.text_input("Title", value=quiz.title)
            new_time_limit = st.number_input("Time Limit (minutes)", value=quiz.time_limit, min_value=1, max_value=300)
        
        with col2:
            new_description = st.text_area("Description", value=quiz.description or "", height=100)
            
            # Level selection (simplified for now)
            level_name = quiz.level.name if quiz.level else "No Level"
            st.text_input("Level", value=level_name, disabled=True, help="Level assignment cannot be changed in this interface")
        
        if st.form_submit_button("Save Quiz Information"):
            success = update_quiz_metadata(db_manager, quiz.id, new_title, new_description, new_time_limit)
            if success:
                st.success("Quiz information updated successfully!")
                st.rerun()
            else:
                st.error("Failed to update quiz information.")
    
    st.markdown("---")
    
    # Questions editing
    st.write("### Questions Management")
    
    if quiz.questions:
        for idx, question in enumerate(quiz.questions):
            with st.expander(f"Question {idx + 1}: {question.question[:50]}{'...' if len(question.question) > 50 else ''}", expanded=False):
                show_question_editor(db_manager, question, idx + 1)
    else:
        st.info("No questions found in this quiz.")
    
    # Add new question
    st.write("### Add New Question")
    with st.form("add_question_form"):
        new_question_text = st.text_area("Question Text", height=100)
        new_explanation = st.text_area("Explanation (optional)", height=80)
        
        st.write("**Options:**")
        option1 = st.text_input("Option 1")
        option2 = st.text_input("Option 2")
        option3 = st.text_input("Option 3")
        option4 = st.text_input("Option 4")
        
        correct_option = st.selectbox("Correct Option", 
                                    ["Option 1", "Option 2", "Option 3", "Option 4"])
        
        if st.form_submit_button("Add Question"):
            options = [option1, option2, option3, option4]
            if new_question_text and all(options):
                correct_index = ["Option 1", "Option 2", "Option 3", "Option 4"].index(correct_option)
                success = add_question_to_quiz(db_manager, quiz.id, new_question_text, options, correct_index, new_explanation)
                if success:
                    st.success("Question added successfully!")
                    st.rerun()
                else:
                    st.error("Failed to add question.")
            else:
                st.error("Please fill in all required fields.")

def show_question_editor(db_manager, question, question_number):
    """Show individual question editor"""
    st.write(f"**Question {question_number}:**")
    
    # Display current question
    st.write(question.question)
    
    # Display current options
    st.write("**Options:**")
    answers = sorted(question.answers, key=lambda x: x.id)
    for i, answer in enumerate(answers):
        icon = "✅" if answer.is_correct else "❌"
        st.write(f"{i+1}. {answer.text} {icon}")
    
    if question.explanation:
        st.write(f"**Explanation:** {question.explanation}")
    
    # Edit form
    with st.form(f"edit_question_{question.id}"):
        st.write("**Edit Question:**")
        new_question_text = st.text_area("Question Text", value=question.question, height=100)
        new_explanation = st.text_area("Explanation", value=question.explanation or "", height=80)
        
        st.write("**Edit Options:**")
        new_options = []
        current_correct = None
        
        for i, answer in enumerate(answers):
            new_options.append(st.text_input(f"Option {i+1}", value=answer.text))
            if answer.is_correct:
                current_correct = i
        
        # Add more options if needed
        while len(new_options) < 4:
            new_options.append(st.text_input(f"Option {len(new_options)+1}", value=""))
        
        correct_option = st.selectbox("Correct Option", 
                                    [f"Option {i+1}" for i in range(len([opt for opt in new_options if opt]))],
                                    index=current_correct if current_correct is not None else 0)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Save Changes"):
                # Filter out empty options
                filtered_options = [opt for opt in new_options if opt.strip()]
                if new_question_text and len(filtered_options) >= 2:
                    correct_index = int(correct_option.split()[-1]) - 1
                    success = update_question(db_manager, question.id, new_question_text, filtered_options, correct_index, new_explanation)
                    if success:
                        st.success("Question updated successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to update question.")
                else:
                    st.error("Please provide a question and at least 2 options.")
        
        with col2:
            if st.form_submit_button("Delete Question", type="secondary"):
                success = delete_question(db_manager, question.id)
                if success:
                    st.success("Question deleted successfully!")
                    st.rerun()
                else:
                    st.error("Failed to delete question.")

def update_quiz_metadata(db_manager, quiz_id, title, description, time_limit):
    """Update quiz metadata"""
    session = db_manager.get_session()
    try:
        quiz = session.query(Quiz).filter_by(id=quiz_id).first()
        if quiz:
            quiz.title = title
            quiz.description = description
            quiz.time_limit = time_limit
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        print(f"Error updating quiz metadata: {e}")
        return False
    finally:
        session.close()

def add_question_to_quiz(db_manager, quiz_id, question_text, options, correct_index, explanation=""):
    """Add a new question to a quiz"""
    session = db_manager.get_session()
    try:
        # Create question
        question = Question(
            question=question_text,
            quiz_id=quiz_id,
            explanation=explanation
        )
        session.add(question)
        session.flush()  # Get the question ID
        
        # Create answers
        for i, option_text in enumerate(options):
            answer = Answer(
                text=option_text,
                is_correct=(i == correct_index),
                question_id=question.id
            )
            session.add(answer)
        
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Error adding question: {e}")
        return False
    finally:
        session.close()

def update_question(db_manager, question_id, question_text, options, correct_index, explanation=""):
    """Update an existing question"""
    session = db_manager.get_session()
    try:
        # Get the question
        question = session.query(Question).filter_by(id=question_id).first()
        if not question:
            return False
        
        # Update question text and explanation
        question.question = question_text
        question.explanation = explanation
        
        # Delete old answers
        session.query(Answer).filter_by(question_id=question_id).delete()
        
        # Create new answers
        for i, option_text in enumerate(options):
            answer = Answer(
                text=option_text,
                is_correct=(i == correct_index),
                question_id=question.id
            )
            session.add(answer)
        
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Error updating question: {e}")
        return False
    finally:
        session.close()

def delete_question(db_manager, question_id):
    """Delete a question and its answers"""
    session = db_manager.get_session()
    try:
        # Delete answers first (due to foreign key constraint)
        session.query(Answer).filter_by(question_id=question_id).delete()
        
        # Delete question
        session.query(Question).filter_by(id=question_id).delete()
        
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        print(f"Error deleting question: {e}")
        return False
    finally:
        session.close()

def show_delete_confirmation(db_manager):
    """Show delete confirmation dialog"""
    if 'deleting_quiz_id' not in st.session_state:
        st.session_state.show_delete_confirm = False
        return
    
    quiz_id = st.session_state.deleting_quiz_id
    quiz = db_manager.get_quiz_by_id(quiz_id)
    
    if quiz:
        st.error(f"⚠️ Are you sure you want to delete the quiz '{quiz.title}'? This action cannot be undone.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, Delete", type="primary"):
                if delete_quiz(db_manager, quiz_id):
                    st.success("Quiz deleted successfully!")
                    del st.session_state.deleting_quiz_id
                    st.session_state.show_delete_confirm = False
                    st.rerun()
                else:
                    st.error("Failed to delete quiz.")
        
        with col2:
            if st.button("❌ Cancel"):
                del st.session_state.deleting_quiz_id
                st.session_state.show_delete_confirm = False
                st.rerun()

def delete_quiz(db_manager, quiz_id):
    """Delete a quiz and all its questions/answers"""
    session = db_manager.get_session()
    try:
        # Delete quiz attempts first
        from models import QuizAttempt
        session.query(QuizAttempt).filter_by(quiz_id=quiz_id).delete()
        
        # Get the quiz and delete it (cascade will handle questions and answers)
        quiz = session.query(Quiz).filter_by(id=quiz_id).first()
        if quiz:
            session.delete(quiz)
            session.commit()
            return True
        return False
    except Exception as e:
        session.rollback()
        print(f"Error deleting quiz: {e}")
        return False
    finally:
        session.close()

def show_user_list(db_manager):
    """Show list of users with management controls"""
    st.subheader("All Users")
    
    # Initialize session state for user deletion confirmation
    if 'show_user_delete_confirm' not in st.session_state:
        st.session_state.show_user_delete_confirm = False
    if 'deleting_user_id' not in st.session_state:
        st.session_state.deleting_user_id = None
    
    # Handle delete confirmation
    if st.session_state.show_user_delete_confirm:
        show_user_delete_confirmation(db_manager)
    
    # Get all users
    users = db_manager.get_all_users()
    
    if not users:
        st.info("No users found in the system.")
        return
    
    # Filter options
    col1, col2 = st.columns(2)
    with col1:
        show_admins_only = st.checkbox("Show Admin Users Only")
    with col2:
        search_term = st.text_input("Search users", placeholder="Enter username...")
    
    # Apply filters
    filtered_users = users
    if show_admins_only:
        filtered_users = [u for u in filtered_users if u.is_admin]
    if search_term:
        filtered_users = [u for u in filtered_users if search_term.lower() in u.username.lower()]
    
    # Display users in a table format
    for user in filtered_users:
        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
        
        with col1:
            user_type = "👑 Admin" if user.is_admin else "👤 User"
            attempt_count = len(user.quiz_attempts)
            avg_score = 0
            if attempt_count > 0:
                avg_score = sum(a.score / a.total_questions * 100 for a in user.quiz_attempts) / attempt_count
            
            st.write(f"**{user.username}** ({user_type})")
            st.write(f"Attempts: {attempt_count} | Avg. Score: {avg_score:.1f}%")
        
        with col2:
            admin_state = "Remove Admin" if user.is_admin else "Make Admin"
            if st.button(admin_state, key=f"admin_{user.id}"):
                success, message = db_manager.update_user(user.id, is_admin=not user.is_admin)
                if success:
                    st.success(f"User {user.username} updated successfully!")
                    st.rerun()
                else:
                    st.error(message)
        
        with col3:
            if st.button("🔐 Reset", key=f"reset_{user.id}"):
                # Store user ID in session state and switch to reset password tab
                st.session_state.resetting_user_id = user.id
                st.session_state.resetting_username = user.username
                st.rerun()
        
        with col4:
            if st.button("🗑️ Delete", key=f"delete_{user.id}"):
                st.session_state.deleting_user_id = user.id
                st.session_state.deleting_username = user.username
                st.session_state.show_user_delete_confirm = True
                st.rerun()
        
        st.markdown("---")

def show_user_delete_confirmation(db_manager):
    """Show deletion confirmation dialog"""
    if 'deleting_user_id' not in st.session_state:
        st.session_state.show_user_delete_confirm = False
        return
    
    user_id = st.session_state.deleting_user_id
    username = st.session_state.deleting_username
    
    st.error(f"⚠️ Are you sure you want to delete the user '{username}'? This will delete all quiz attempts and cannot be undone.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Yes, Delete User", type="primary"):
            success, message = db_manager.delete_user(user_id)
            if success:
                st.success(f"User {username} deleted successfully!")
                st.session_state.show_user_delete_confirm = False
                st.session_state.deleting_user_id = None
                st.session_state.deleting_username = None
                st.rerun()
            else:
                st.error(message)
    
    with col2:
        if st.button("❌ Cancel"):
            st.session_state.show_user_delete_confirm = False
            st.session_state.deleting_user_id = None
            st.session_state.deleting_username = None
            st.rerun()

def show_add_user_form(db_manager):
    """Show form to add a new user"""
    st.subheader("Add New User")
    
    with st.form("add_user_form"):
        username = st.text_input("Username", placeholder="Enter username")
        password = st.text_input("Password", placeholder="Enter password", type="password")
        confirm_password = st.text_input("Confirm Password", placeholder="Confirm password", type="password")
        is_admin = st.checkbox("Is Admin User")
        
        if st.form_submit_button("Add User", type="primary"):
            if not username or not password:
                st.error("Username and password are required")
                return
            
            if password != confirm_password:
                st.error("Passwords do not match")
                return
            
            # Create the user
            user, message = db_manager.create_user(username, password)
            if user:
                # If admin checkbox was selected, update user to admin
                if is_admin and not user.is_admin:
                    success, _ = db_manager.update_user(user.id, is_admin=True)
                    if success:
                        st.success(f"Admin user '{username}' created successfully!")
                    else:
                        st.warning(f"User created but could not set admin status: {message}")
                else:
                    st.success(f"User '{username}' created successfully!")
            else:
                st.error(message)

def show_password_reset_form(db_manager):
    """Show form to reset user password"""
    st.subheader("Reset User Password")
    
    # Check if we're resetting a specific user's password
    if hasattr(st.session_state, 'resetting_user_id') and st.session_state.resetting_user_id:
        st.info(f"Resetting password for: {st.session_state.resetting_username}")
        user_id = st.session_state.resetting_user_id
        
        with st.form("reset_specific_password_form"):
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            if st.form_submit_button("Reset Password", type="primary"):
                if not new_password:
                    st.error("Password cannot be empty")
                    return
                
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                    return
                
                # Reset password
                success, message = db_manager.reset_password(user_id, new_password)
                if success:
                    st.success(f"Password reset successfully for {st.session_state.resetting_username}!")
                    # Clear session state
                    st.session_state.resetting_user_id = None
                    st.session_state.resetting_username = None
                else:
                    st.error(message)
        
        if st.button("Cancel Password Reset"):
            st.session_state.resetting_user_id = None
            st.session_state.resetting_username = None
            st.rerun()
    else:
        # Show dropdown to select a user
        users = db_manager.get_all_users()
        if not users:
            st.info("No users found in the system.")
            return
        
        user_options = [(user.id, f"{user.username} {'(Admin)' if user.is_admin else ''}") for user in users]
        selected_user_idx = st.selectbox(
            "Select User", 
            range(len(user_options)),
            format_func=lambda i: user_options[i][1]
        )
        
        selected_user_id = user_options[selected_user_idx][0]
        
        with st.form("reset_password_form"):
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            if st.form_submit_button("Reset Password", type="primary"):
                if not new_password:
                    st.error("Password cannot be empty")
                    return
                
                if new_password != confirm_password:
                    st.error("Passwords do not match")
                    return
                
                # Reset password
                success, message = db_manager.reset_password(selected_user_id, new_password)
                if success:
                    st.success(f"Password reset successfully!")
                else:
                    st.error(message)

def show_user_statistics(db_manager, stats):
    """Show detailed user statistics"""
    st.subheader("User Activity Statistics")
    
    # Top active users chart
    st.write("### Most Active Users")
    if stats['active_users']:
        # Convert to DataFrame for easier charting
        active_df = pd.DataFrame(stats['active_users'])
        
        fig = px.bar(
            active_df, 
            x='username', 
            y='attempt_count', 
            title='Users with Most Quiz Attempts',
            labels={'username': 'User', 'attempt_count': 'Number of Attempts'}
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No quiz attempts recorded yet.")
    
    # User registration over time (if we had registration date)
    st.write("### Quiz Attempts by User")
    
    # Get all users with their quiz attempts
    users = db_manager.get_all_users()
    
    if users:
        # Prepare data for visualization
        user_attempt_data = []
        for user in users:
            if user.quiz_attempts:
                total_attempts = len(user.quiz_attempts)
                avg_score = sum(a.score / a.total_questions * 100 for a in user.quiz_attempts) / total_attempts if total_attempts > 0 else 0
                total_time = sum(a.time_taken / 60 for a in user.quiz_attempts)  # minutes
                
                user_attempt_data.append({
                    'username': user.username,
                    'attempts': total_attempts,
                    'avg_score': round(avg_score, 1),
                    'total_time': round(total_time, 1)
                })
        
        if user_attempt_data:
            user_df = pd.DataFrame(user_attempt_data)
            
            # Sort by attempts
            user_df = user_df.sort_values('attempts', ascending=False)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig1 = px.bar(
                    user_df, 
                    x='username', 
                    y='avg_score',
                    title='Average Quiz Score by User (%)',
                    color='avg_score',
                    color_continuous_scale='RdYlGn',  # Red to Yellow to Green
                    range_color=[0, 100]
                )
                st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                fig2 = px.bar(
                    user_df, 
                    x='username', 
                    y='total_time',
                    title='Total Time Spent on Quizzes (minutes)',
                    color='attempts',
                    labels={'total_time': 'Total Time (min)', 'attempts': 'Quiz Attempts'}
                )
                st.plotly_chart(fig2, use_container_width=True)
            
            # Show the data in table form
            st.write("### User Performance Data")
            st.dataframe(user_df, use_container_width=True)
        else:
            st.info("No quiz attempts recorded yet.")
    else:
        st.info("No users found in the system.")
