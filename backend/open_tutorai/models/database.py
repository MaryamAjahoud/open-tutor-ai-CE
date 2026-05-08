"""
Database module for OpenTutorAI

This module defines the database tables specific to OpenTutorAI while using
the same database connection as OpenWebUI to maintain compatibility.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, func, ARRAY
from sqlalchemy.orm import relationship
from open_webui.internal.db import Base, get_db, JSONField

PREFIX = "opentutorai_"

class Support(Base):
    """
    Table for storing student support requests.
    Each support request is linked to a chat in the Open WebUI chat table.
    """
    __tablename__ = f"{PREFIX}support"
    
    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    title = Column(String, nullable=False)
    short_description = Column(String, nullable=True)
    subject = Column(String, nullable=False)
    custom_subject = Column(String, nullable=True)
    course_id = Column(String, nullable=True)
    learning_objective = Column(Text, nullable=True)
    learning_type = Column(String, nullable=True)
    level = Column(String, nullable=False)
    content_language = Column(String, nullable=True, default="English")
    estimated_duration = Column(String, nullable=True)
    access_type = Column(String, nullable=True, default="Private")
    keywords = Column(String, nullable=True)
    start_date = Column(String, nullable=True)
    end_date = Column(String, nullable=True)
    avatar_id = Column(String, nullable=True)
    status = Column(String, nullable=False, default="open")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())
    meta_data = Column(JSONField, nullable=True)
    
    chat_id = Column(String, ForeignKey("chat.id", ondelete="CASCADE"), index=True, nullable=True)
    
    def __repr__(self):
        return f"<Support(id={self.id}, user_id={self.user_id}, title={self.title})>"

class SupportFile(Base):
    """
    Table for storing files attached to support requests.
    """
    __tablename__ = f"{PREFIX}support_file"
    
    id = Column(String, primary_key=True, index=True)
    support_id = Column(String, ForeignKey(f"{PREFIX}support.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    support = relationship("Support", backref="files")
    
    def __repr__(self):
        return f"<SupportFile(id={self.id}, support_id={self.support_id}, filename={self.filename})>"

def init_database():
    """
    Initialize the database tables for OpenTutorAI.
    Call this function when your app starts to ensure all tables exist.
    
    This is safe to call even if tables already exist, as SQLAlchemy's
    create_all() only creates tables that don't exist yet.
    """
    from open_webui.internal.db import engine
    
    Base.metadata.create_all(bind=engine, checkfirst=True)
    print("OpenTutorAI database tables initialized successfully")
    
    return engine


class Assignment(Base):
    """Table for storing teacher assignments."""
    __tablename__ = f"{PREFIX}assignment"

    id = Column(String, primary_key=True, index=True)
    teacher_id = Column(String, index=True, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    course = Column(String, nullable=True)
    course_id = Column(String, nullable=True)
    course_color = Column(String, nullable=True, default="from-indigo-500 to-indigo-600")
    due_date = Column(String, nullable=False)
    due_time = Column(String, nullable=False, default="23:59")
    points = Column(Integer, nullable=False, default=100)
    status = Column(String, nullable=False, default="active")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())

    def __repr__(self):
        return f"<Assignment(id={self.id}, title={self.title})>"


class Submission(Base):
    """Table for storing student submissions."""
    __tablename__ = f"{PREFIX}submission"

    id = Column(String, primary_key=True, index=True)
    assignment_id = Column(String, ForeignKey(f"{PREFIX}assignment.id", ondelete="CASCADE"), nullable=False, index=True)
    student_id = Column(String, nullable=False, index=True)
    student_name = Column(String, nullable=True)
    student_email = Column(String, nullable=True)
    content = Column(Text, nullable=True)
    file_ids = Column(JSONField, nullable=True)
    status = Column(String, nullable=False, default="submitted")
    grade = Column(String, nullable=True)
    feedback = Column(Text, nullable=True)
    submitted_at = Column(DateTime, nullable=False, server_default=func.now())
    graded_at = Column(DateTime, nullable=True)

    assignment = relationship("Assignment", backref="submissions")

    def __repr__(self):
        return f"<Submission(id={self.id}, assignment_id={self.assignment_id}, student_id={self.student_id})>"
