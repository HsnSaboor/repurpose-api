"""
Enhanced YouTube Transcript Service with English Preference
Main service file - imports models and cache functions
"""

from youtube_transcript_api import YouTubeTranscriptApi
from typing import List, Dict, Optional, Any
import logging
import json

# Import from split modules
from core.services.transcript_models import (
    TranscriptPriority,
    TranscriptMetadata,
    EnglishTranscriptResult,
    TranscriptPreferences
)
from core.services.transcript_cache import (
    get_cached_transcript,
    cache_transcript,
    clear_expired_cache,
    get_cache_statistics,
    cleanup_cache
)
from sqlalchemy.orm import Session

# Re-export for backward compatibility
__all__ = [
    'TranscriptPriority',
    'TranscriptMetadata',
    'EnglishTranscriptResult',
    'TranscriptPreferences',
    'get_english_transcript',
    'get_transcript',
    'get_transcript_safely',
    'get_transcript_text',
    'get_available_languages',
    'list_available_transcripts_with_metadata',
    'get_cached_transcript',
    'cache_transcript',
    'clear_expired_cache',
    'get_cache_statistics',
    'cleanup_cache'
]

def list_available_transcripts_with_metadata(video_id: str) -> List[TranscriptMetadata]:
    """List all available transcripts with detailed metadata"""
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)
        
        metadata_list = []
        for transcript in transcript_list:
            # Extract translation language codes properly
            translation_langs = []
            if hasattr(transcript, 'translation_languages'):
                for lang in transcript.translation_languages:
                    if hasattr(lang, 'language_code'):
                        translation_langs.append(lang.language_code)
                    elif isinstance(lang, str):
                        translation_langs.append(lang)
            
            metadata = TranscriptMetadata(
                language_code=transcript.language_code,
                language=transcript.language,
                is_generated=transcript.is_generated,
                is_translatable=transcript.is_translatable,
                translation_languages=translation_langs
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
                    preferences.prefer_manual):
                    logging.info(f"Found manual {transcript.language} transcript for {video_id} (translatable: {transcript.is_translatable})")
                    return transcript
        
            # Priority 4: Auto-generated non-English transcript (if translation enabled)
            for transcript in transcript_list:
                if (transcript.is_generated and 
                    transcript.language_code.lower() != 'en'):
                    logging.info(f"Found auto-generated {transcript.language} transcript for {video_id} (translatable: {transcript.is_translatable})")
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
                # Use original transcript even if translation fails - LLM can handle it
                processing_notes.append(f"YouTube translation failed, using original {best_transcript.language} text - will be handled by LLM")
                needs_translation = False  # Mark as not translated since we're using original
        
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
