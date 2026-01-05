# db/models.py

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Enum, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=True)
    session_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    uploaded_files = relationship("UploadedFile", back_populates="user")
    questions = relationship("Question", back_populates="user")

class UploadedFile(Base):
    __tablename__ = 'uploaded_files'
    id = Column(Integer, primary_key=True)
    filename = Column(String)
    preview = Column(Text)
    checksum = Column(String)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship("User", back_populates="uploaded_files")
    questions = relationship("Question", back_populates="file")

class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    question = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user_id = Column(Integer, ForeignKey('users.id'))
    file_id = Column(Integer, ForeignKey('uploaded_files.id'))

    user = relationship("User", back_populates="questions")
    file = relationship("UploadedFile", back_populates="questions")
    code_executions = relationship("CodeExecution", back_populates="question")
    consulting_messages = relationship("ConsultingMessage", back_populates="question")

class CodeExecution(Base):
    __tablename__ = 'code_executions'
    id = Column(Integer, primary_key=True)
    code = Column(Text, nullable=False)
    result = Column(Text)
    status = Column(Enum('success', 'error', name='execution_status'))
    error_message = Column(Text)
    execution_time = Column(Float)
    model_used = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    question_id = Column(Integer, ForeignKey('questions.id'))

    question = relationship("Question", back_populates="code_executions")

class ConsultingMessage(Base):
    __tablename__ = 'consulting_messages'
    id = Column(Integer, primary_key=True)
    message = Column(Text, nullable=False)
    role = Column(String)  # user, assistant, system...
    model_used = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    question_id = Column(Integer, ForeignKey('questions.id'))

    question = relationship("Question", back_populates="consulting_messages")
