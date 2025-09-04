from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

DATABASE_URL = "sqlite:///./yt_repurposer.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    status = Column(String)
    youtube_video_id = Column(String, nullable=False)
    title = Column(String, nullable=True)
    transcript = Column(Text, nullable=True)
    video_url = Column(String, nullable=True) # Added video_url
    repurposed_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Enhanced transcript metadata columns
    transcript_language = Column(String(10), nullable=True)  # Language code (e.g., 'en', 'es')
    transcript_type = Column(String(20), nullable=True)  # 'manual' or 'auto_generated'
    is_translated = Column(Boolean, default=False)
    source_language = Column(String(10), nullable=True)  # Original language if translated
    translation_confidence = Column(Float, nullable=True)  # Translation confidence score
    transcript_priority = Column(String(20), nullable=True)  # Priority level used
    processing_notes = Column(Text, nullable=True)  # JSON string of processing notes

class TranscriptCache(Base):
    """Cache table for storing transcript data to avoid repeated API calls"""
    __tablename__ = "transcript_cache"

    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(String(50), nullable=False, index=True)
    language_code = Column(String(10), nullable=False)
    transcript_type = Column(String(20), nullable=False)  # 'manual' or 'auto_generated'
    transcript_text = Column(Text, nullable=False)
    is_translated = Column(Boolean, default=False)
    source_language = Column(String(10), nullable=True)
    cached_at = Column(DateTime, default=datetime.utcnow)
    
    # Composite unique constraint to prevent duplicates
    __table_args__ = (
        # UniqueConstraint('video_id', 'language_code', 'transcript_type', name='unique_transcript_cache'),
    )

def init_db():
    Base.metadata.create_all(bind=engine)