"""Database setup and session management"""
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import Optional
import json

from app.config import settings

Base = declarative_base()


class ConversationSession(Base):
    """Database model for conversation sessions"""
    __tablename__ = "conversations"
    
    session_id = Column(String, primary_key=True, index=True)
    messages = Column(JSON, default=list)
    triage_level = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    red_flag_detected = Column(String, nullable=True)


# Create database engine
engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def save_conversation(db: Session, session_id: str, messages: list, triage_level: Optional[str] = None, 
                     summary: Optional[str] = None, red_flag: Optional[str] = None):
    """Save or update conversation session"""
    session = db.query(ConversationSession).filter(ConversationSession.session_id == session_id).first()
    
    if session:
        session.messages = messages
        session.triage_level = triage_level
        session.summary = summary
        session.red_flag_detected = red_flag
        session.updated_at = datetime.now()
    else:
        session = ConversationSession(
            session_id=session_id,
            messages=messages,
            triage_level=triage_level,
            summary=summary,
            red_flag_detected=red_flag
        )
        db.add(session)
    
    db.commit()
    return session


def get_conversation(db: Session, session_id: str) -> Optional[ConversationSession]:
    """Get conversation session by ID"""
    return db.query(ConversationSession).filter(ConversationSession.session_id == session_id).first()

