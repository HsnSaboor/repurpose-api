"""Enhanced YouTube Transcript Service with English Preference"""
from youtube_transcript_api import YouTubeTranscriptApi
from typing import List, Dict, Optional, Any, Union
from enum import Enum
from pydantic import BaseModel
import logging
import re
import json
import hashlib
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import os

class TranscriptPriority(Enum):
    """Priority levels for transcript selection"""
    MANUAL_ENGLISH = 1
    AUTO_ENGLISH = 2
    MANUAL_TRANSLATED = 3
    AUTO_TRANSLATED = 4

class TranscriptMetadata(BaseModel):
    """Metadata about a transcript"""
    language_code: str
    language: str
    is_generated: bool
    is_translatable: bool
    translation_languages: List[str] = []

class EnglishTranscriptResult(BaseModel):
    """Result of English transcript processing"""
    transcript_text: str
    language_code: str
    language: str
    is_generated: bool
    is_translated: bool
    priority: TranscriptPriority
    translation_source_language: Optional[str] = None
    confidence_score: float = 1.0
    processing_notes: List[str] = []

class TranscriptPreferences(BaseModel):
    """User preferences for transcript processing"""
    prefer_manual: bool = True
    require_english: bool = True
    enable_translation: bool = True
    fallback_languages: List[str] = ["en", "es", "fr", "de"]
    preserve_formatting: bool = False

# Caching functions
def get_cache_key(video_id: str, language_code: str, transcript_type: str) -> str:
    """Generate a unique cache key for transcript data"""
    return f"{video_id}_{language_code}_{transcript_type}"

def get_cached_transcript(video_id: str, language_code: str, transcript_type: str, db_session: Optional[Session] = None) -> Optional[str]:
    """Retrieve cached transcript data"""
    if not db_session:
        return None
    
    try:
        from core.database import TranscriptCache
        
        cache_entry = db_session.query(TranscriptCache).filter(
            TranscriptCache.video_id == video_id,
            TranscriptCache.language_code == language_code,
            TranscriptCache.transcript_type == transcript_type
        ).first()
        
        if cache_entry:
            # Check if cache is still valid (7 days)
            cache_age = datetime.utcnow() - cache_entry.cached_at
            if cache_age < timedelta(days=7):
                logging.info(f"Cache hit for {video_id} ({language_code}, {transcript_type})")
                return cache_entry.transcript_text
            else:
                # Cache expired, remove it
                db_session.delete(cache_entry)
                db_session.commit()
                logging.info(f"Cache expired and removed for {video_id}")
        
        return None
        
    except Exception as e:
        logging.error(f"Error retrieving cached transcript: {e}")
        return None

def cache_transcript(video_id: str, language_code: str, transcript_type: str, transcript_text: str, 
                    is_translated: bool = False, source_language: Optional[str] = None, 
                    db_session: Optional[Session] = None) -> bool:
    """Cache transcript data for future use"""
    if not db_session:
        return False
    
    try:
        from core.database import TranscriptCache
        
        # Check if entry already exists
        existing_entry = db_session.query(TranscriptCache).filter(
            TranscriptCache.video_id == video_id,
            TranscriptCache.language_code == language_code,
            TranscriptCache.transcript_type == transcript_type
        ).first()
        
        if existing_entry:
            # Update existing entry
            existing_entry.transcript_text = transcript_text
            existing_entry.is_translated = is_translated
            existing_entry.source_language = source_language
            existing_entry.cached_at = datetime.utcnow()
        else:
            # Create new cache entry
            cache_entry = TranscriptCache(
                video_id=video_id,
                language_code=language_code,
                transcript_type=transcript_type,
                transcript_text=transcript_text,
                is_translated=is_translated,
                source_language=source_language
            )
            db_session.add(cache_entry)
        
        db_session.commit()
        logging.info(f"Cached transcript for {video_id} ({language_code}, {transcript_type})")
        return True
        
    except Exception as e:
        logging.error(f"Error caching transcript: {e}")
        db_session.rollback()
        return False

def clear_expired_cache(db_session: Optional[Session] = None, days_old: int = 7) -> int:
    """Clear expired cache entries"""
    if not db_session:
        return 0
    
    try:
        from core.database import TranscriptCache
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        expired_entries = db_session.query(TranscriptCache).filter(
            TranscriptCache.cached_at < cutoff_date
        )
        
        count = expired_entries.count()
        expired_entries.delete()
        db_session.commit()
        
        logging.info(f"Cleared {count} expired cache entries")
        return count
        
    except Exception as e:
        logging.error(f"Error clearing expired cache: {e}")
        db_session.rollback()
        return 0

def list_available_transcripts_with_metadata(video_id: str) -> List[TranscriptMetadata]:
    """List all available transcripts with detailed metadata"""
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)
        
        metadata_list = []
        for transcript in transcript_list:
            metadata = TranscriptMetadata(
                language_code=transcript.language_code,
                language=transcript.language,
                is_generated=transcript.is_generated,
                is_translatable=transcript.is_translatable,
                translation_languages=transcript.translation_languages if hasattr(transcript, 'translation_languages') else []
            )
            metadata_list.append(metadata)
            
        return metadata_list
        
    except Exception as e:
        logging.error(f"Error listing transcripts for {video_id}: {e}")
        return []

def find_best_english_transcript_source(video_id: str, preferences: Optional[TranscriptPreferences] = None) -> Optional[Any]:
    """Find the best English transcript source based on priority"""
    if preferences is None:
        preferences = TranscriptPreferences()
    
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)
        
        # Priority 1: Manual English transcript
        for transcript in transcript_list:
            if (transcript.language_code.lower() == 'en' and 
                not transcript.is_generated and 
                preferences.prefer_manual):
                logging.info(f"Found manual English transcript for {video_id}")
                return transcript
        
        # Priority 2: Auto-generated English transcript
        for transcript in transcript_list:
            if (transcript.language_code.lower() == 'en' and 
                transcript.is_generated):
                logging.info(f"Found auto-generated English transcript for {video_id}")
                return transcript
        
        # Priority 3: Manual non-English transcript (if translation enabled)
        if preferences.enable_translation:
            for transcript in transcript_list:
                if (not transcript.is_generated and 
                    transcript.language_code.lower() != 'en' and 
                    transcript.is_translatable and
                    preferences.prefer_manual):
                    logging.info(f"Found manual {transcript.language} transcript for translation for {video_id}")
                    return transcript
        
            # Priority 4: Auto-generated non-English transcript (if translation enabled)
            for transcript in transcript_list:
                if (transcript.is_generated and 
                    transcript.language_code.lower() != 'en' and 
                    transcript.is_translatable):
                    logging.info(f"Found auto-generated {transcript.language} transcript for translation for {video_id}")
                    return transcript
        
        logging.warning(f"No suitable transcript found for {video_id}")
        return None
        
    except Exception as e:
        logging.error(f"Error finding best transcript source for {video_id}: {e}")
        return None

def get_priority_for_transcript(transcript, is_translated: bool = False) -> TranscriptPriority:
    """Determine the priority level for a transcript"""
    if not is_translated:
        if transcript.language_code.lower() == 'en':
            return TranscriptPriority.MANUAL_ENGLISH if not transcript.is_generated else TranscriptPriority.AUTO_ENGLISH
    else:
        return TranscriptPriority.MANUAL_TRANSLATED if not transcript.is_generated else TranscriptPriority.AUTO_TRANSLATED
    
    # Fallback
    return TranscriptPriority.AUTO_TRANSLATED

def get_english_transcript(video_id: str, preferences: Optional[TranscriptPreferences] = None, db_session: Optional[Session] = None) -> Optional[EnglishTranscriptResult]:
    """Get English transcript with intelligent fallback strategy and caching"""
    if preferences is None:
        preferences = TranscriptPreferences()
    
    processing_notes = []
    
    try:
        # First, check cache for English transcript
        if db_session:
            cached_text = get_cached_transcript(video_id, 'en', 'processed', db_session)
            if cached_text:
                processing_notes.append("Retrieved from cache")
                return EnglishTranscriptResult(
                    transcript_text=cached_text,
                    language_code='en',
                    language='English',
                    is_generated=False,  # We don't know from cache, assume best case
                    is_translated=False,
                    priority=TranscriptPriority.MANUAL_ENGLISH,
                    confidence_score=1.0,
                    processing_notes=processing_notes
                )
        
        # Find the best transcript source
        best_transcript = find_best_english_transcript_source(video_id, preferences)
        
        if best_transcript is None:
            logging.error(f"No transcripts available for video {video_id}")
            return None
        
        # Check cache for this specific transcript type
        cache_key_type = 'auto_generated' if best_transcript.is_generated else 'manual'
        if db_session:
            cached_text = get_cached_transcript(video_id, best_transcript.language_code, cache_key_type, db_session)
            if cached_text:
                processing_notes.append(f"Retrieved {cache_key_type} transcript from cache")
                needs_translation = best_transcript.language_code.lower() != 'en'
                priority = get_priority_for_transcript(best_transcript, needs_translation)
                
                return EnglishTranscriptResult(
                    transcript_text=cached_text,
                    language_code='en' if needs_translation else best_transcript.language_code,
                    language=best_transcript.language,
                    is_generated=best_transcript.is_generated,
                    is_translated=needs_translation,
                    priority=priority,
                    confidence_score=0.9,  # Slightly lower for cached
                    processing_notes=processing_notes
                )
        
        # Determine if we need translation
        needs_translation = best_transcript.language_code.lower() != 'en'
        
        # Fetch the transcript data
        transcript_data = best_transcript.fetch()
        if not transcript_data:
            logging.error(f"Failed to fetch transcript data for {video_id}")
            return None
        
        # Convert to raw data format
        if hasattr(transcript_data, 'to_raw_data'):
            raw_data = transcript_data.to_raw_data()
        else:
            raw_data = transcript_data
        
        # Extract text
        transcript_text = " ".join([entry.get('text', '') for entry in raw_data])
        
        # Cache original transcript
        if db_session and not needs_translation:
            cache_transcript(
                video_id, 
                best_transcript.language_code, 
                cache_key_type, 
                transcript_text,
                False, 
                None, 
                db_session
            )
        
        if needs_translation and preferences.enable_translation:
            # Check cache for translated version first
            if db_session:
                cached_translated = get_cached_transcript(video_id, 'en', f"{cache_key_type}_translated", db_session)
                if cached_translated:
                    processing_notes.append(f"Retrieved translated transcript from cache")
                    priority = get_priority_for_transcript(best_transcript, True)
                    
                    return EnglishTranscriptResult(
                        transcript_text=cached_translated,
                        language_code='en',
                        language=best_transcript.language,
                        is_generated=best_transcript.is_generated,
                        is_translated=True,
                        priority=priority,
                        translation_source_language=best_transcript.language_code,
                        confidence_score=0.8,  # Lower for cached translation
                        processing_notes=processing_notes
                    )
            
            # Translate the transcript
            try:
                translated_transcript = best_transcript.translate('en')
                translated_data = translated_transcript.fetch()
                
                if hasattr(translated_data, 'to_raw_data'):
                    translated_raw = translated_data.to_raw_data()
                else:
                    translated_raw = translated_data
                
                transcript_text = " ".join([entry.get('text', '') for entry in translated_raw])
                processing_notes.append(f"Translated from {best_transcript.language} ({best_transcript.language_code})")
                
                # Cache translated transcript
                if db_session:
                    cache_transcript(
                        video_id, 
                        'en', 
                        f"{cache_key_type}_translated", 
                        transcript_text,
                        True, 
                        best_transcript.language_code, 
                        db_session
                    )
                
            except Exception as translation_error:
                logging.error(f"Translation failed for {video_id}: {translation_error}")
                if preferences.require_english:
                    return None
                processing_notes.append(f"Translation failed, using original {best_transcript.language} text")
        
        # Cache final English transcript
        if db_session and (not needs_translation or (needs_translation and 'Translation failed' not in processing_notes[-1] if processing_notes else True)):
            cache_transcript(
                video_id, 
                'en', 
                'processed', 
                transcript_text,
                needs_translation, 
                best_transcript.language_code if needs_translation else None, 
                db_session
            )
        
        # Determine priority
        priority = get_priority_for_transcript(best_transcript, needs_translation)
        
        # Calculate confidence score
        confidence_score = 1.0
        if best_transcript.is_generated:
            confidence_score -= 0.2
        if needs_translation:
            confidence_score -= 0.3
        confidence_score = max(0.1, confidence_score)
        
        # Create result
        result = EnglishTranscriptResult(
            transcript_text=transcript_text,
            language_code='en' if needs_translation else best_transcript.language_code,
            language=best_transcript.language,
            is_generated=best_transcript.is_generated,
            is_translated=needs_translation,
            priority=priority,
            translation_source_language=best_transcript.language_code if needs_translation else None,
            confidence_score=confidence_score,
            processing_notes=processing_notes
        )
        
        logging.info(f"Successfully processed transcript for {video_id}: {priority.name}, confidence: {confidence_score:.2f}")
        return result
        
    except Exception as e:
        logging.error(f"Error processing English transcript for {video_id}: {e}")
        return None

# Legacy functions for backward compatibility
def get_transcript(video_id: str) -> Optional[List[Dict[str, Any]]]:
    """Fetch transcript for a YouTube video with improved error handling (Legacy)"""
    try:
        result = get_english_transcript(video_id)
        if result:
            # Convert back to legacy format
            ytt_api = YouTubeTranscriptApi()
            transcript = ytt_api.fetch(video_id)
            return transcript.to_raw_data() if transcript else None
        return None
    except Exception as e:
        logging.error(f"Error fetching transcript for {video_id}: {e}")
        return None

def get_transcript_safely(video_id: str) -> Optional[List[Dict[str, Any]]]:
    """Safely fetch transcript with fallback strategies (Legacy with English preference)"""
    try:
        # Use new English transcript service
        result = get_english_transcript(video_id)
        if result:
            # Convert to legacy format by fetching raw data
            ytt_api = YouTubeTranscriptApi()
            best_transcript = find_best_english_transcript_source(video_id)
            if best_transcript:
                if result.is_translated:
                    # Get translated transcript
                    translated = best_transcript.translate('en')
                    transcript_data = translated.fetch()
                else:
                    transcript_data = best_transcript.fetch()
                
                if hasattr(transcript_data, 'to_raw_data'):
                    return transcript_data.to_raw_data()
                else:
                    return transcript_data
        
        return None
        
    except Exception as e:
        logging.error(f"Transcript extraction failed for {video_id}: {e}")
        return None

def get_transcript_text(video_id: str, preferences: Optional[TranscriptPreferences] = None, db_session: Optional[Session] = None) -> Optional[str]:
    """Get transcript as concatenated English text with preferences and caching"""
    result = get_english_transcript(video_id, preferences, db_session)
    if result:
        return result.transcript_text
    return None

def get_available_languages(video_id: str) -> List[str]:
    """Get list of available transcript languages for a video"""
    try:
        metadata_list = list_available_transcripts_with_metadata(video_id)
        return [meta.language_code for meta in metadata_list]
    except Exception as e:
        logging.error(f"Could not get available languages for {video_id}: {e}")
        return []

# Cache maintenance functions
def get_cache_statistics(db_session: Optional[Session] = None) -> Dict[str, Any]:
    """Get cache statistics"""
    if not db_session:
        return {}
    
    try:
        from core.database import TranscriptCache
        
        total_entries = db_session.query(TranscriptCache).count()
        
        # Count by language
        language_stats = db_session.query(
            TranscriptCache.language_code, 
            db_session.query(TranscriptCache).filter(
                TranscriptCache.language_code == TranscriptCache.language_code
            ).count()
        ).group_by(TranscriptCache.language_code).all()
        
        # Count translated entries
        translated_count = db_session.query(TranscriptCache).filter(
            TranscriptCache.is_translated == True
        ).count()
        
        # Get oldest and newest entries
        oldest_entry = db_session.query(TranscriptCache).order_by(
            TranscriptCache.cached_at.asc()
        ).first()
        
        newest_entry = db_session.query(TranscriptCache).order_by(
            TranscriptCache.cached_at.desc()
        ).first()
        
        return {
            "total_entries": total_entries,
            "translated_entries": translated_count,
            "languages": dict(language_stats) if language_stats else {},
            "oldest_cache": oldest_entry.cached_at.isoformat() if oldest_entry else None,
            "newest_cache": newest_entry.cached_at.isoformat() if newest_entry else None
        }
        
    except Exception as e:
        logging.error(f"Error getting cache statistics: {e}")
        return {}

def cleanup_cache(db_session: Optional[Session] = None, max_entries: int = 1000) -> Dict[str, int]:
    """Cleanup cache by removing old entries when limit is exceeded"""
    if not db_session:
        return {"removed": 0, "remaining": 0}
    
    try:
        from core.database import TranscriptCache
        
        # Count current entries
        current_count = db_session.query(TranscriptCache).count()
        
        removed_count = 0
        
        if current_count > max_entries:
            # Remove oldest entries
            entries_to_remove = current_count - max_entries
            oldest_entries = db_session.query(TranscriptCache).order_by(
                TranscriptCache.cached_at.asc()
            ).limit(entries_to_remove)
            
            for entry in oldest_entries:
                db_session.delete(entry)
            
            removed_count = entries_to_remove
            db_session.commit()
        
        # Also remove expired entries
        expired_removed = clear_expired_cache(db_session)
        
        remaining_count = db_session.query(TranscriptCache).count()
        
        return {
            "removed": removed_count + expired_removed,
            "remaining": remaining_count
        }
        
    except Exception as e:
        logging.error(f"Error during cache cleanup: {e}")
        db_session.rollback()
        return {"removed": 0, "remaining": 0}