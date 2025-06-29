"""
Database models for the Kids Quiz App
Updated to work with existing olympiadquiz schema
"""
from datetime import datetime
import json
import hashlib
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

class Subject(Base):
    __tablename__ = 'subject'
    __table_args__ = {'schema': 'olympiadquiz'}
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    topics = relationship('Topic', back_populates='subject', cascade='all, delete-orphan')

class Topic(Base):
    __tablename__ = 'topic'
    __table_args__ = {'schema': 'olympiadquiz'}
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    subject_id = Column(Integer, ForeignKey('olympiadquiz.subject.id'), nullable=False)
    subject = relationship('Subject', back_populates='topics')
    classes = relationship('Class', back_populates='topic', cascade='all, delete-orphan')

class Class(Base):
    __tablename__ = 'class'
    __table_args__ = {'schema': 'olympiadquiz'}
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    topic_id = Column(Integer, ForeignKey('olympiadquiz.topic.id'), nullable=False)
    topic = relationship('Topic', back_populates='classes')
    levels = relationship('Level', back_populates='class_', cascade='all, delete-orphan')

class Level(Base):
    __tablename__ = 'level'
    __table_args__ = {'schema': 'olympiadquiz'}
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    class_id = Column(Integer, ForeignKey('olympiadquiz.class.id'), nullable=False)
    class_ = relationship('Class', back_populates='levels')
    quizzes = relationship('Quiz', back_populates='level', cascade='all, delete-orphan')

class Quiz(Base):
    __tablename__ = 'quiz'
    __table_args__ = {'schema': 'olympiadquiz'}
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    level_id = Column(Integer, ForeignKey('olympiadquiz.level.id'), nullable=True)
    time_limit = Column(Integer, default=30)  # Time limit in minutes
    is_visible = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    level = relationship('Level', back_populates='quizzes')
    questions = relationship('Question', back_populates='quiz', cascade='all, delete-orphan')
    attempts = relationship('QuizAttempt', back_populates='quiz', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'time_limit': self.time_limit,
            'questions': [q.to_dict() for q in self.questions]
        }

class Question(Base):
    __tablename__ = 'question'
    __table_args__ = {'schema': 'olympiadquiz'}
    
    id = Column(Integer, primary_key=True)
    question = Column(Text, nullable=False)
    quiz_id = Column(Integer, ForeignKey('olympiadquiz.quiz.id', ondelete='CASCADE'), nullable=False)
    explanation = Column(Text)
    
    quiz = relationship('Quiz', back_populates='questions')
    answers = relationship('Answer', back_populates='question', cascade='all, delete-orphan')
    
    def to_dict(self):
        answers = sorted(self.answers, key=lambda x: x.id)
        return {
            'id': self.id,
            'question': self.question,
            'explanation': self.explanation,
            'options': [answer.text for answer in answers],
            'correct_index': next((i for i, answer in enumerate(answers) if answer.is_correct), 0)
        }

class Answer(Base):
    __tablename__ = 'answer'
    __table_args__ = {'schema': 'olympiadquiz'}
    
    id = Column(Integer, primary_key=True)
    text = Column(String(255), nullable=False)
    is_correct = Column(Boolean, default=False)
    question_id = Column(Integer, ForeignKey('olympiadquiz.question.id', ondelete='CASCADE'), nullable=False)
    
    question = relationship('Question', back_populates='answers')

class User(Base):
    __tablename__ = 'user'
    __table_args__ = {'schema': 'olympiadquiz'}
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password_hash = Column(String(120))
    is_admin = Column(Boolean, default=False)
    
    quiz_attempts = relationship('QuizAttempt', back_populates='user', cascade='all, delete-orphan')
    
    def set_password(self, password):
        # Use SHA-256 hash which is shorter and fits in 120 chars
        self.password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    
    def check_password(self, password):
        return self.password_hash == hashlib.sha256(password.encode('utf-8')).hexdigest()

class QuizAttempt(Base):
    __tablename__ = 'quiz_attempt'
    __table_args__ = {'schema': 'olympiadquiz'}
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('olympiadquiz.user.id'), nullable=False)
    quiz_id = Column(Integer, ForeignKey('olympiadquiz.quiz.id', ondelete='CASCADE'), nullable=False)
    score = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    time_taken = Column(Integer)  # Time taken in seconds
    date = Column(DateTime, nullable=False, default=datetime.utcnow)
    results = Column(Text, nullable=False)  # JSON string of results
    
    user = relationship('User', back_populates='quiz_attempts')
    quiz = relationship('Quiz', back_populates='attempts')
    
    def get_results(self):
        return json.loads(self.results) if self.results else []
    
    def set_results(self, results):
        self.results = json.dumps(results)
