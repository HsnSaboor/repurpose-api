from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Float, Index, LargeBinary
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
    
    # Brain indexing fields (v2.0)
    is_indexed = Column(Boolean, default=False)  # Whether indexed in Brain
    indexed_at = Column(DateTime, nullable=True)  # When indexed
    source_type = Column(String(20), nullable=True)  # 'youtube' | 'document' | 'text'
    tags = Column(Text, nullable=True)  # JSON array of tags
    topics = Column(Text, nullable=True)  # JSON array of extracted topics
    summary = Column(Text, nullable=True)  # AI-generated summary
    embedding_id = Column(String(100), nullable=True)  # Reference to vector embedding
    
    __table_args__ = (
        Index('idx_videos_is_indexed', 'is_indexed'),
        Index('idx_videos_source_type', 'source_type'),
    )

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


class BrainSource(Base):
    """Unified knowledge source storage for the Brain system"""
    __tablename__ = "brain_sources"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    source_id = Column(String(100), nullable=False, unique=True, index=True)
    source_type = Column(String(20), nullable=False)  # 'youtube' | 'document' | 'text'
    title = Column(String(500), nullable=True)
    content = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)  # AI-generated summary (200-500 chars)
    topics = Column(Text, nullable=True)  # JSON array: ["topic1", "topic2"]
    tags = Column(Text, nullable=True)  # JSON array: ["tag1", "tag2"]
    source_metadata = Column(Text, nullable=True)  # JSON: source-specific metadata (renamed from 'metadata')
    
    # Indexing for semantic search
    embedding = Column(LargeBinary, nullable=True)  # Vector embedding for semantic search
    embedding_model = Column(String(50), nullable=True)  # Model used for embedding
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_used_at = Column(DateTime, nullable=True)
    use_count = Column(Integer, default=0)

    __table_args__ = (
        Index('idx_brain_sources_type', 'source_type'),
        Index('idx_brain_sources_last_used', 'last_used_at'),
    )


class BrainSession(Base):
    """Tracks content generation sessions using Brain sources"""
    __tablename__ = "brain_sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(100), nullable=False, unique=True, index=True)
    mode = Column(String(20), nullable=False)  # 'vision' | 'full_ai_single' | 'full_ai_multiple' | 'full_ai_auto' | 'hybrid'
    
    # Input
    user_vision = Column(Text, nullable=True)  # User's idea/thought (for vision mode)
    selected_source_ids = Column(Text, nullable=True)  # JSON array of source IDs
    requested_count = Column(Integer, nullable=True)  # For multiple mode
    
    # Hybrid mode fields
    ai_augment_hint = Column(Text, nullable=True)  # Hint for AI to find related sources
    ai_augment_strategy = Column(String(20), nullable=True)  # 'augment' | 'fill' | 'support'
    ai_discovered_source_ids = Column(Text, nullable=True)  # JSON array of AI-found source IDs
    
    # Matching (for vision mode)
    matched_source_ids = Column(Text, nullable=True)  # JSON array of matched source IDs
    match_scores = Column(Text, nullable=True)  # JSON: {source_id: score}
    
    # Output
    generated_count = Column(Integer, nullable=True)
    generated_content = Column(Text, nullable=True)  # JSON array of generated pieces
    
    # Style
    style_preset = Column(String(50), nullable=True)
    custom_style = Column(Text, nullable=True)  # JSON
    content_types = Column(Text, nullable=True)  # JSON array: ["reel", "tweet"]
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(20), default='pending')  # 'pending' | 'processing' | 'completed' | 'failed'
    error_message = Column(Text, nullable=True)

    __table_args__ = (
        Index('idx_brain_sessions_status', 'status'),
        Index('idx_brain_sessions_mode', 'mode'),
    )


def init_db():
    Base.metadata.create_all(bind=engine)