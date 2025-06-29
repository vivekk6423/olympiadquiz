"""
Quiz utilities and functions
"""
import streamlit as st
import time
import json
from datetime import datetime
from database import get_db_manager

def get_performance_level(percentage):
    """Get performance level based on percentage"""
    if percentage >= 90:
        return "Excellent! 🌟"
    elif percentage >= 80:
        return "Very Good! 👍"
    elif percentage >= 70:
        return "Good! 👌"
    elif percentage >= 60:
        return "Fair 📚"
    else:
        return "Needs Improvement 💪"

def format_time(seconds):
    """Format time in MM:SS format"""
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes:02d}:{remaining_seconds:02d}"

def display_quiz_navigation():
    """Display quiz navigation breadcrumbs"""
    if 'navigation_path' in st.session_state:
        path = st.session_state.navigation_path
        breadcrumb = " → ".join(path)
        st.markdown(f"**Navigation:** {breadcrumb}")

def show_subjects():
    """Display all subjects"""
    # Safety check - don't run if in admin mode
    if is_admin_mode():
        st.error("Admin users should use the Admin Dashboard for quiz management.")
        if st.button("Go to Admin Dashboard"):
            st.session_state.page = "admin"
            st.rerun()
        return
    
    db_manager = get_db_manager()
    subjects = db_manager.get_subjects()
    
    st.title("📚 Choose Your Subject")
    display_quiz_navigation()
    
    if not subjects:
        st.warning("No subjects available. Please contact the administrator.")
        return
    
    cols = st.columns(min(3, len(subjects)))
    
    for idx, subject in enumerate(subjects):
        with cols[idx % 3]:
            if st.button(
                subject.name,
                key=f"subject_{subject.id}",
                help=f"Explore {subject.name} topics",
                use_container_width=True
            ):
                st.session_state.navigation_path = [subject.name]
                st.session_state.current_subject_id = subject.id
                st.session_state.page = "topics"
                st.rerun()

def show_topics(subject_id):
    """Display topics for a subject"""
    # Safety check - don't run if in admin mode
    if is_admin_mode():
        st.error("Admin users should use the Admin Dashboard for quiz management.")
        if st.button("Go to Admin Dashboard"):
            st.session_state.page = "admin"
            st.rerun()
        return
    
    db_manager = get_db_manager()
    subject = db_manager.get_subject_by_id(subject_id)
    
    if not subject:
        st.error("Subject not found")
        return
    
    st.title(f"📖 {subject.name} Topics")
    display_quiz_navigation()
    
    if not subject.topics:
        st.warning("No topics available for this subject.")
        if st.button("← Back to Subjects"):
            st.session_state.page = "subjects"
            st.rerun()
        return
    
    cols = st.columns(min(3, len(subject.topics)))
    
    for idx, topic in enumerate(subject.topics):
        with cols[idx % 3]:
            if st.button(
                topic.name,
                key=f"topic_{topic.id}",
                help=f"Explore {topic.name} classes",
                use_container_width=True
            ):
                st.session_state.navigation_path = [subject.name, topic.name]
                st.session_state.current_topic_id = topic.id
                st.session_state.page = "classes"
                st.rerun()
    
    st.markdown("---")
    if st.button("← Back to Subjects"):
        st.session_state.page = "subjects"
        st.rerun()

def show_classes(topic_id):
    """Display classes for a topic"""
    db_manager = get_db_manager()
    topic = db_manager.get_topic_by_id(topic_id)
    
    if not topic:
        st.error("Topic not found")
        return
    
    st.title(f"🎯 {topic.name} Classes")
    display_quiz_navigation()
    
    if not topic.classes:
        st.warning("No classes available for this topic.")
        if st.button("← Back to Topics"):
            st.session_state.page = "topics"
            st.rerun()
        return
    
    cols = st.columns(min(3, len(topic.classes)))
    
    for idx, class_ in enumerate(topic.classes):
        with cols[idx % 3]:
            if st.button(
                class_.name,
                key=f"class_{class_.id}",
                help=f"Select difficulty level for {class_.name}",
                use_container_width=True
            ):
                st.session_state.navigation_path = [topic.subject.name, topic.name, class_.name]
                st.session_state.current_class_id = class_.id
                st.session_state.page = "levels"
                st.rerun()
    
    st.markdown("---")
    if st.button("← Back to Topics"):
        st.session_state.page = "topics"
        st.rerun()

def show_levels(class_id):
    """Display levels for a class"""
    db_manager = get_db_manager()
    class_ = db_manager.get_class_by_id(class_id)
    
    if not class_:
        st.error("Class not found")
        return
    
    st.title(f"⭐ {class_.name} Levels")
    display_quiz_navigation()
    
    if not class_.levels:
        st.warning("No levels available for this class.")
        if st.button("← Back to Classes"):
            st.session_state.page = "classes"
            st.rerun()
        return
    
    cols = st.columns(min(3, len(class_.levels)))
    
    for idx, level in enumerate(class_.levels):
        with cols[idx % 3]:
            if st.button(
                level.name,
                key=f"level_{level.id}",
                help=f"View quizzes in {level.name}",
                use_container_width=True
            ):
                st.session_state.navigation_path = [class_.topic.subject.name, class_.topic.name, class_.name, level.name]
                st.session_state.current_level_id = level.id
                st.session_state.page = "quizzes"
                st.rerun()
    
    st.markdown("---")
    if st.button("← Back to Classes"):
        st.session_state.page = "classes"
        st.rerun()

def show_quizzes(level_id):
    """Display quizzes for a level"""
    from auth import get_current_user_id, require_admin
    
    db_manager = get_db_manager()
    level = db_manager.get_level_by_id(level_id)
    
    if not level:
        st.error("Level not found")
        return
    
    st.title(f"🧩 Available Quizzes in {level.name}")
    display_quiz_navigation()
    
    # Get visible quizzes
    quizzes = db_manager.get_visible_quizzes_by_level(level_id, require_admin())
    
    if not quizzes:
        st.warning("No quizzes available for this level.")
        if st.button("← Back to Levels"):
            st.session_state.page = "levels"
            st.rerun()
        return
    
    for quiz in quizzes:
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader(quiz.title)
                if quiz.description:
                    st.write(quiz.description)
                
                # Quiz info
                info_cols = st.columns(3)
                with info_cols[0]:
                    st.metric("⏱️ Time Limit", f"{quiz.time_limit} min")
                with info_cols[1]:
                    st.metric("❓ Questions", len(quiz.questions))
                with info_cols[2]:
                    # Check user's attempts
                    user_id = get_current_user_id()
                    attempts = db_manager.get_user_quiz_attempts(user_id, quiz.id)
                    st.metric("📊 Attempts", len(attempts))
                
                # Show last attempt score if available
                if attempts:
                    last_attempt = attempts[0]
                    percentage = (last_attempt.score / last_attempt.total_questions) * 100
                    st.info(f"🎯 Last Score: {last_attempt.score}/{last_attempt.total_questions} ({percentage:.1f}%)")
            
            with col2:
                if st.button(
                    "Start Quiz" if not attempts else "Retake Quiz",
                    key=f"start_quiz_{quiz.id}",
                    type="primary",
                    use_container_width=True
                ):
                    st.session_state.current_quiz_id = quiz.id
                    st.session_state.page = "take_quiz"
                    st.rerun()
                
                if attempts:
                    if st.button(
                        "View Results",
                        key=f"view_results_{quiz.id}",
                        use_container_width=True
                    ):
                        st.session_state.current_quiz_id = quiz.id
                        st.session_state.page = "quiz_results"
                        st.rerun()
            
            st.markdown("---")
    
    if st.button("← Back to Levels"):
        st.session_state.page = "levels"
        st.rerun()

def take_quiz(quiz_id):
    """Display quiz taking interface"""
    from auth import get_current_user_id
    
    db_manager = get_db_manager()
    quiz = db_manager.get_quiz_by_id(quiz_id)
    
    if not quiz:
        st.error("Quiz not found")
        return
    
    # Initialize quiz session state
    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = False
        st.session_state.current_question = 0
        st.session_state.user_answers = {}
        st.session_state.start_time = None
        st.session_state.quiz_questions = quiz.questions
    
    # Quiz header
    st.title(f"📝 {quiz.title}")
    if quiz.description:
        st.write(quiz.description)
    
    # Start quiz button
    if not st.session_state.quiz_started:
        st.markdown("### Ready to start?")
        st.info(f"⏱️ Time Limit: {quiz.time_limit} minutes | ❓ Questions: {len(quiz.questions)}")
        
        if st.button("🚀 Start Quiz", type="primary", use_container_width=True):
            st.session_state.quiz_started = True
            st.session_state.start_time = time.time()
            st.rerun()
        
        if st.button("← Back to Quizzes"):
            st.session_state.page = "quizzes"
            st.rerun()
        return
    
    # Quiz interface
    questions = st.session_state.quiz_questions
    current_q_idx = st.session_state.current_question
    
    if current_q_idx >= len(questions):
        # Quiz completed
        submit_quiz_results(quiz)
        return
    
    # Timer and progress
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        elapsed_time = int(time.time() - st.session_state.start_time)
        remaining_time = max(0, (quiz.time_limit * 60) - elapsed_time)
        st.metric("⏱️ Time Remaining", format_time(remaining_time))
    
    with col2:
        progress = (current_q_idx + 1) / len(questions)
        st.metric("📊 Progress", f"{current_q_idx + 1}/{len(questions)}")
        st.progress(progress)
    
    with col3:
        answered = len(st.session_state.user_answers)
        st.metric("✅ Answered", f"{answered}/{len(questions)}")
    
    # Check if time is up
    if remaining_time <= 0:
        st.error("⏰ Time's up! Submitting your quiz...")
        submit_quiz_results(quiz)
        return
    
    # Current question
    current_question = questions[current_q_idx]
    
    st.markdown("---")
    st.markdown(f"### Question {current_q_idx + 1}")
    st.write(current_question.question)
    
    # Answer options
    answers = sorted(current_question.answers, key=lambda x: x.id)
    options = [answer.text for answer in answers]
    
    # Get current answer
    current_answer = st.session_state.user_answers.get(current_q_idx)
    
    # Radio buttons for answers
    selected_answer = st.radio(
        "Choose your answer:",
        options,
        index=current_answer if current_answer is not None else None,
        key=f"question_{current_q_idx}"
    )
    
    # Store answer
    if selected_answer:
        st.session_state.user_answers[current_q_idx] = options.index(selected_answer)
    
    # Navigation buttons
    st.markdown("---")
    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)
    
    with nav_col1:
        if current_q_idx > 0:
            if st.button("⬅️ Previous"):
                st.session_state.current_question -= 1
                st.rerun()
    
    with nav_col2:
        if current_q_idx < len(questions) - 1:
            if st.button("Next ➡️"):
                st.session_state.current_question += 1
                st.rerun()
    
    with nav_col3:
        if st.button("📋 Question List"):
            show_question_list(questions)
    
    with nav_col4:
        if len(st.session_state.user_answers) == len(questions):
            if st.button("✅ Submit Quiz", type="primary"):
                submit_quiz_results(quiz)
        else:
            unanswered = len(questions) - len(st.session_state.user_answers)
            st.button(f"❌ {unanswered} Unanswered", disabled=True)

def show_question_list(questions):
    """Show list of all questions for navigation"""
    st.markdown("### Question Navigation")
    
    cols = st.columns(5)
    for i, question in enumerate(questions):
        with cols[i % 5]:
            answered = i in st.session_state.user_answers
            button_text = f"Q{i+1} {'✅' if answered else '❌'}"
            
            if st.button(button_text, key=f"nav_q_{i}"):
                st.session_state.current_question = i
                st.rerun()

def submit_quiz_results(quiz):
    """Submit quiz and show results"""
    from auth import get_current_user_id
    
    # Calculate results
    user_answers = st.session_state.user_answers
    questions = st.session_state.quiz_questions
    
    score = 0
    results = []
    
    for i, question in enumerate(questions):
        answers = sorted(question.answers, key=lambda x: x.id)
        correct_index = next((idx for idx, a in enumerate(answers) if a.is_correct), 0)
        user_answer = user_answers.get(i, -1)
        
        is_correct = user_answer == correct_index
        if is_correct:
            score += 1
        
        results.append({
            'question_id': question.id,
            'question': question.question,
            'user_answer': user_answer,
            'correct_answer': correct_index,
            'is_correct': is_correct,
            'explanation': question.explanation or ''
        })
    
    # Calculate time taken
    time_taken = int(time.time() - st.session_state.start_time)
    percentage = (score / len(questions)) * 100
    
    # Save to database
    db_manager = get_db_manager()
    user_id = get_current_user_id()
    
    attempt = db_manager.submit_quiz_attempt(
        user_id=user_id,
        quiz_id=quiz.id,
        score=score,
        total_questions=len(questions),
        time_taken=time_taken,
        results=results
    )
    
    # Clear quiz session state
    for key in ['quiz_started', 'current_question', 'user_answers', 'start_time', 'quiz_questions']:
        if key in st.session_state:
            del st.session_state[key]
    
    # Show results
    st.success("🎉 Quiz Completed!")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📊 Score", f"{score}/{len(questions)}")
    with col2:
        st.metric("📈 Percentage", f"{percentage:.1f}%")
    with col3:
        st.metric("⏱️ Time Taken", format_time(time_taken))
    
    # Performance level
    performance = get_performance_level(percentage)
    st.markdown(f"### {performance}")
    
    # Action buttons
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 View Detailed Results", type="primary"):
            st.session_state.page = "quiz_results"
            st.rerun()
    
    with col2:
        if st.button("← Back to Quizzes"):
            st.session_state.page = "quizzes"
            st.rerun()

def show_quiz_results(quiz_id):
    """Show detailed quiz results"""
    from auth import get_current_user_id
    
    db_manager = get_db_manager()
    quiz = db_manager.get_quiz_by_id(quiz_id)
    user_id = get_current_user_id()
    attempts = db_manager.get_user_quiz_attempts(user_id, quiz_id)
    
    if not quiz or not attempts:
        st.error("Quiz or results not found")
        return
    
    st.title(f"📊 Results: {quiz.title}")
    
    # Attempts overview
    st.subheader("📈 Your Attempts")
    
    for idx, attempt in enumerate(attempts):
        percentage = (attempt.score / attempt.total_questions) * 100
        performance = get_performance_level(percentage)
        
        with st.expander(f"Attempt {idx + 1} - {attempt.date.strftime('%Y-%m-%d %H:%M')} - {percentage:.1f}%"):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Score", f"{attempt.score}/{attempt.total_questions}")
            with col2:
                st.metric("Percentage", f"{percentage:.1f}%")
            with col3:
                st.metric("Time Taken", format_time(attempt.time_taken))
            with col4:
                st.metric("Performance", performance)
    
    # Detailed results for latest attempt
    if attempts:
        latest_attempt = attempts[0]
        results = latest_attempt.get_results()
        
        st.subheader("📝 Detailed Review (Latest Attempt)")
        
        for idx, result in enumerate(results):
            with st.expander(f"Question {idx + 1} - {'✅ Correct' if result['is_correct'] else '❌ Incorrect'}"):
                st.write("**Question:**", result['question'])
                
                # Show options (we need to get them from the database)
                question = next((q for q in quiz.questions if q.id == result['question_id']), None)
                if question:
                    answers = sorted(question.answers, key=lambda x: x.id)
                    options = [answer.text for answer in answers]
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        user_ans = result['user_answer']
                        st.write("**Your Answer:**", 
                                options[user_ans] if 0 <= user_ans < len(options) else "Not answered")
                    
                    with col2:
                        correct_ans = result['correct_answer']
                        st.write("**Correct Answer:**", options[correct_ans])
                    
                    if result['explanation']:
                        st.write("**Explanation:**", result['explanation'])
    
    # Back button
    if st.button("← Back to Quizzes"):
        st.session_state.page = "quizzes"
        st.rerun()

def is_admin_mode():
    """Check if we're currently in admin mode"""
    return st.session_state.get('page') == 'admin' or st.session_state.get('admin_page') is not None
